from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
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
# HELPER — Parse
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
# CREATE — JSON with image paths
# =========================================================
@router.post("/admin", response_model=List[CSRResponse])
async def create_sections(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
    titles: List[str] = Form(...),
    files: List[UploadFile] = File(...),
):
    post_time = datetime.utcnow()

    # 🔥 Fix 1: Support comma-separated titles from Swagger
    if len(titles) == 1 and "," in titles[0]:
        titles = [t.strip() for t in titles[0].split(",") if t.strip()]

    # 🔥 Validate titles
    if not titles:
        raise HTTPException(status_code=400, detail="At least one title required")

    # 🔥 Validate files
    if not files:
        raise HTTPException(status_code=400, detail="Images required")

    # 🔥 Validate 4 images per section
    expected_images = len(titles) * 4

    if len(files) != expected_images:
        raise HTTPException(
            status_code=400,
            detail=f"Each section needs 4 images (expected {expected_images})"
        )

    created_records = []
    file_index = 0

    for title in titles:
        uploaded_paths = []

        for _ in range(4):
            file = files[file_index]

            # 🔥 Validate image type
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} is not a valid image"
                )

            path = save_image(file)
            uploaded_paths.append(path)
            file_index += 1

        record = CSR(
            posted_at=post_time,
            title=title,
            image1=uploaded_paths[0],
            image2=uploaded_paths[1],
            image3=uploaded_paths[2],
            image4=uploaded_paths[3],
        )

        db.add(record)
        created_records.append(record)

    db.commit()

    for record in created_records:
        db.refresh(record)

    return created_records


# =========================================================
# GET — BY DATE
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