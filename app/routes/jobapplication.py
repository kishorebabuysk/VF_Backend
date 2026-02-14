from fastapi import (
    APIRouter, Depends, HTTPException,
    UploadFile, File, Form, Query, Body
)
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import Optional, List
from datetime import date, datetime
import os
import json

from app.database import get_db
from app.models.jobapplication import Application, ApplicationExperience, ApplicationEducation
from app.schemas.jobapplication import ApplicationResponse
from app.utils.jwt_dependency import get_current_admin
from app.utils.file_upload import save_upload_file
from app.models.admin import Admin as User

router = APIRouter(prefix="/admin/applications", tags=["Job Applications"])

UPLOAD_DIR = "uploads/job_applications"


# =========================================================
# CREATE APPLICATION
# =========================================================
@router.post("/", response_model=ApplicationResponse, status_code=201)
async def apply_job(
    job_id: int = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    date_of_birth: date = Form(...),
    gender: str = Form(...),
    location: str = Form(...),
    pan_number: str = Form(...),
    linkedin_url: Optional[str] = Form(None),

    educations: str = Form(...),

    position_applied: str = Form(...),
    preferred_work_mode: str = Form(...),
    key_skills: str = Form(...),
    expected_salary: int = Form(...),
    why_hire_me: str = Form(...),

    experience_level: str = Form(...),
    experience: Optional[str] = Form(None),

    pan_card: UploadFile = File(...),
    resume: UploadFile = File(...),
    photo: UploadFile = File(...),

    db: Session = Depends(get_db),
):

    full_name = f"{first_name.strip()} {last_name.strip()}"

    pan_card_path = save_upload_file(UPLOAD_DIR, pan_card)
    resume_path = save_upload_file(UPLOAD_DIR, resume)
    photo_path = save_upload_file(UPLOAD_DIR, photo)

    db_application = Application(
        job_id=job_id,
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        phone=phone,
        email=email,
        date_of_birth=date_of_birth,
        gender=gender,
        location=location,
        pan_number=pan_number,
        linkedin_url=linkedin_url,
        position_applied=position_applied,
        preferred_work_mode=preferred_work_mode,
        key_skills=key_skills,
        expected_salary=expected_salary,
        why_hire_me=why_hire_me,
        experience_level=experience_level,
        pan_card_file=pan_card_path,
        resume_file=resume_path,
        photo_file=photo_path,
    )

    # ---------------- EDUCATION ----------------
    try:
        edu_list = json.loads(educations)
        if len(edu_list) == 0:
            raise HTTPException(422, "At least one education required")

        seen_edu = set()
        for edu in edu_list:
            key = (
                edu["highest_qualification"].strip().lower(),
                edu["specialization"].strip().lower(),
                edu["university"].strip().lower(),
                edu["college"].strip().lower(),
                int(edu["year_of_passing"]),
            )
            if key in seen_edu:
                continue
            seen_edu.add(key)

            db_application.educations.append(ApplicationEducation(**edu))

    except Exception as e:
        raise HTTPException(400, f"Invalid education format: {str(e)}")

    # ---------------- EXPERIENCE ----------------
    if experience:
        try:
            exp_list = json.loads(experience)

            if experience_level.lower() == "experienced" and len(exp_list) == 0:
                raise HTTPException(422, "Experience required")

            seen_exp = set()
            for exp in exp_list:
                doj = datetime.strptime(exp["date_of_joining"], "%Y-%m-%d").date()
                rd = datetime.strptime(exp["relieving_date"], "%Y-%m-%d").date()

                key = (
                    exp["previous_company"].strip().lower(),
                    exp["previous_role"].strip().lower(),
                    doj, rd
                )
                if key in seen_exp:
                    continue
                seen_exp.add(key)

                db_application.experiences.append(
                    ApplicationExperience(
                        previous_company=exp["previous_company"],
                        previous_role=exp["previous_role"],
                        date_of_joining=doj,
                        relieving_date=rd,
                    )
                )

        except Exception as e:
            raise HTTPException(400, f"Invalid experience format: {str(e)}")

    elif experience_level.lower() == "experienced":
        raise HTTPException(422, "Experience required for experienced candidate")

    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


# =========================================================
# GET ALL APPLICATIONS
# =========================================================
@router.get("/getall", response_model=List[ApplicationResponse])
async def get_all_applications(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return (
        db.query(Application)
        .options(
            selectinload(Application.experiences),
            selectinload(Application.educations)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return applications

# =========================================================
# LIST APPLICATIONS + STATS
# =========================================================
@router.get("/", response_model=dict)
async def list_applications(
    job_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):

    query = db.query(Application).options(selectinload(Application.experiences))

    if job_id:
        query = query.filter(Application.job_id == job_id)
    if status:
        query = query.filter(Application.status == status)

    applications = query.all()

    stats_query = db.query(Application.status, func.count(Application.id))
    if job_id:
        stats_query = stats_query.filter(Application.job_id == job_id)
    stats_query = stats_query.group_by(Application.status)

    status_counts = dict(stats_query.all())

    return {
        "applications": [ApplicationResponse.model_validate(a) for a in applications],
        "stats": {
            "total": len(applications),
            "pending": status_counts.get("Pending", 0),
            "shortlisted": status_counts.get("Shortlisted", 0),
            "maybe": status_counts.get("Maybe", 0),
            "rejected": status_counts.get("Rejected", 0),
            "by_status": status_counts,
        },
    }


# =========================================================
# BULK DELETE
# =========================================================
@router.delete("/bulk")
async def delete_applications_bulk(
    application_ids: List[int] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    deleted = 0

    for app_id in application_ids:
        app = db.query(Application).filter(Application.id == app_id).first()
        if app:
            for field in ["pan_card_file", "resume_file", "photo_file"]:
                file_path = getattr(app, field)
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)

            db.delete(app)
            deleted += 1

    db.commit()
    return {"message": f"Deleted {deleted} applications"}


# =========================================================
# GET SINGLE APPLICATION
# =========================================================
@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    application = (
        db.query(Application)
        .options(
            selectinload(Application.experiences),
            selectinload(Application.educations)
        )
        .filter(Application.id == application_id)
        .first()
    )

    if not application:
        raise HTTPException(404, "Application not found")

    return application


# =========================================================
# UPDATE STATUS
# =========================================================
@router.patch("/{application_id}/status")
async def update_status(
    application_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(404, "Application not found")

    old_status = application.status
    application.status = status
    db.commit()
    db.refresh(application)

    return {
        "id": application.id,
        "old_status": old_status,
        "new_status": status,
        "message": "Status updated successfully"
    }


# =========================================================
# DELETE
# =========================================================
@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(404, "Application not found")

    for field in ["pan_card_file", "resume_file", "photo_file"]:
        path = getattr(application, field)
        if path and os.path.exists(path):
            os.remove(path)

    db.delete(application)
    db.commit()

    return {"message": "Application deleted successfully"}
