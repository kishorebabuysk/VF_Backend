from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models.csr import CSR
from app.schemas.csr import CSRCreate, CSRUpdate, CSRResponse
from app.utils.jwt_dependency import get_current_admin
from app.utils.csr_file_upload import save_image

router = APIRouter(prefix="/csr", tags=["CSR"])


# =========================================================
# HELPER — Parse DD-MM-YYYY or DD/MM/YYYY
# =========================================================
def parse_date(date_str: str):
    try:
        date_str = date_str.replace("/", "-")
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")

        start = date_obj
        end = date_obj + timedelta(days=1)

        return start, end
    except ValueError:
        raise HTTPException(400, "Date must be DD-MM-YYYY or DD/MM/YYYY")


# =========================================================
# IMAGE UPLOAD (Single)
# =========================================================
@router.post("/upload")
def upload_images(files: List[UploadFile] = File(...), admin=Depends(get_current_admin)):

    if len(files) == 0:
        raise HTTPException(400, "No files uploaded")

    uploaded_paths = []

    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(400, f"{file.filename} is not an image")

        path = save_image(file)
        uploaded_paths.append(path)

    return {
        "count": len(uploaded_paths),
        "paths": uploaded_paths
    }


# =========================================================
# CREATE — JSON with image paths
# =========================================================
@router.post("/admin", response_model=List[CSRResponse])
def create_sections(
    data: CSRCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    post_time = datetime.utcnow()
    created = []

    for sec in data.sections:
        record = CSR(
            posted_at=post_time,
            title=sec.title,
            image1=sec.image1,
            image2=sec.image2,
            image3=sec.image3,
            image4=sec.image4
        )
        db.add(record)
        created.append(record)

    db.commit()

    for r in created:
        db.refresh(r)

    return created


# =========================================================
# GET — BY DATE (DD-MM-YYYY)
# =========================================================
@router.get("/date/{date}", response_model=List[CSRResponse])
def get_by_date(date: str, db: Session = Depends(get_db)):
    start, end = parse_date(date)

    records = (
        db.query(CSR)
        .filter(CSR.posted_at >= start, CSR.posted_at < end)
        .order_by(CSR.posted_at.desc())
        .all()
    )

    if not records:
        raise HTTPException(404, "No activities found for this date")

    return records


# =========================================================
# GET — SINGLE BY ID
# =========================================================
@router.get("/{section_id}", response_model=CSRResponse)
def get_by_id(section_id: int, db: Session = Depends(get_db)):
    record = db.query(CSR).filter(CSR.id == section_id).first()
    if not record:
        raise HTTPException(404, "Activity not found")
    return record


# =========================================================
# GET — ALL
# =========================================================
@router.get("", response_model=List[CSRResponse])
def get_all(db: Session = Depends(get_db)):
    return db.query(CSR).order_by(CSR.posted_at.desc()).all()


# =========================================================
# UPDATE — BY ID
# =========================================================
@router.put("/admin/{section_id}", response_model=CSRResponse)
def update(
    section_id: int,
    data: CSRUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    record = db.query(CSR).filter(CSR.id == section_id).first()
    if not record:
        raise HTTPException(404, "Activity not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


# =========================================================
# DELETE — BY ID
# =========================================================
@router.delete("/admin/{section_id}")
def delete(
    section_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    record = db.query(CSR).filter(CSR.id == section_id).first()
    if not record:
        raise HTTPException(404, "Activity not found")

    db.delete(record)
    db.commit()
    return {"message": "Activity deleted"}


# =========================================================
# DELETE — BY DATE
# =========================================================
@router.delete("/admin/date/{date}")
def delete_by_date(
    date: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    start, end = parse_date(date)

    records = db.query(CSR).filter(CSR.posted_at >= start, CSR.posted_at < end).all()
    if not records:
        raise HTTPException(404, "No activities found")

    count = len(records)

    for record in records:
        db.delete(record)

    db.commit()
    return {"message": f"Deleted {count} activities from {date}"}


# =========================================================
# DELETE — ALL (Admin)
# =========================================================
@router.delete("/admin/all")
def delete_all(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    count = db.query(CSR).delete()
    db.commit()
    return {"message": f"Deleted {count} activities"}