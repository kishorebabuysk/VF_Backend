from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.utils.jwt_dependency import get_current_admin
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse, JobUpdate

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# =====================================================
# STATIC ROUTES (ALWAYS FIRST)
# =====================================================

# CREATE JOB
@router.post("/", response_model=JobResponse)
def create_job(
    request: JobCreate,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    new_job = Job(**request.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


# GET ALL JOBS
@router.get("/", response_model=List[JobResponse])
def get_all_jobs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=100)
):
    return db.query(Job).offset(skip).limit(limit).all()


# BULK DELETE JOBS
@router.delete("/bulk")
def bulk_delete_jobs(
    job_ids: List[int] = Query(...),
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    deleted_count = (
        db.query(Job)
        .filter(Job.id.in_(job_ids))
        .delete(synchronize_session=False)
    )

    db.commit()

    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="No jobs found for the provided IDs"
        )

    return {"message": f"Deleted {deleted_count} jobs"}


# DELETE ALL JOBS
@router.delete("/")
def delete_all_jobs(
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    deleted = db.query(Job).delete()
    db.commit()
    return {"message": f"Deleted {deleted} jobs"}


# =====================================================
# DYNAMIC ROUTES (ALWAYS LAST)
# =====================================================

# GET JOB BY ID
@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# UPDATE JOB
@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    request: JobUpdate,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = request.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


# DELETE SINGLE JOB
@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
