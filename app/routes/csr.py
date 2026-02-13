import os
import hashlib
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.csr import CSR
from app.schemas.csr import CSRCreate, CSRUpdate, CSRResponse
from app.utils.jwt_dependency import get_current_admin
from app.utils.file_upload import save_upload_file


router = APIRouter(prefix="/csr", tags=["CSR"])
UPLOAD_DIR = "uploads/csr"


# =========================================================
# Helpers
# =========================================================
def generate_image_id(path: str) -> str:
    return hashlib.md5(path.encode()).hexdigest()


def format_response(csr: CSR):
    """Convert DB images dict → frontend array format"""
    images = []
    for slot in ["1", "2", "3", "4"]:
        path = csr.images.get(slot)
        if path:
            images.append({
                "slot": int(slot),
                "id": generate_image_id(path),
                "path": path
            })

    return {
        "id": csr.id,
        "title": csr.title,
        "images": images,
        "is_active": csr.is_active,
        "created_at": csr.created_at
    }


# =========================================================
# PUBLIC — LIST ALL SECTIONS
# =========================================================
@router.get("", response_model=list[CSRResponse])
def list_csr(db: Session = Depends(get_db)):
    records = (
        db.query(CSR)
        .filter(CSR.is_active == True)
        .order_by(CSR.created_at.desc())
        .all()
    )
    return [format_response(r) for r in records]


# =========================================================
# PUBLIC — GET SINGLE SECTION
# =========================================================
@router.get("/{csr_id}", response_model=CSRResponse)
def get_csr(csr_id: int, db: Session = Depends(get_db)):
    csr = db.query(CSR).filter(CSR.id == csr_id, CSR.is_active == True).first()

    if not csr:
        raise HTTPException(404, "CSR not found")

    return format_response(csr)


# =========================================================
# ADMIN — UPLOAD IMAGE
# =========================================================
@router.post("/admin/upload")
async def upload_csr_image(
    file: UploadFile = File(...),
    admin=Depends(get_current_admin)
):
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(400, "Only JPG/PNG allowed")

    file_path = save_upload_file(UPLOAD_DIR, file)

    return {
        "id": generate_image_id(file_path),
        "path": file_path
    }


# =========================================================
# ADMIN — CREATE SECTION (MUST HAVE 4 IMAGES)
# =========================================================
@router.post("/admin", response_model=CSRResponse)
def create_csr(data: CSRCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):

    if len(data.images) != 4:
        raise HTTPException(400, "CSR must contain exactly 4 images")

    images_dict = {str(i+1): img for i, img in enumerate(data.images)}

    csr = CSR(title=data.title, images=images_dict)

    db.add(csr)
    db.commit()
    db.refresh(csr)

    return format_response(csr)


# =========================================================
# ADMIN — UPDATE TITLE
# =========================================================
@router.put("/admin/{csr_id}", response_model=CSRResponse)
def update_csr(csr_id: int, data: CSRUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):

    csr = db.query(CSR).filter(CSR.id == csr_id).first()
    if not csr:
        raise HTTPException(404, "CSR not found")

    if data.title is not None:
        csr.title = data.title

    db.commit()
    db.refresh(csr)

    return format_response(csr)


# =========================================================
# ADMIN — REPLACE IMAGE IN SLOT
# =========================================================
@router.put("/admin/{csr_id}/image/{slot}", response_model=CSRResponse)
def replace_image(
    csr_id: int,
    slot: int,
    image_path: str = Query(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    if slot not in [1,2,3,4]:
        raise HTTPException(400, "Slot must be between 1-4")

    csr = db.query(CSR).filter(CSR.id == csr_id).first()
    if not csr:
        raise HTTPException(404, "CSR not found")

    csr.images[str(slot)] = image_path

    db.commit()
    db.refresh(csr)

    return format_response(csr)


# =========================================================
# ADMIN — REMOVE IMAGE FROM SLOT (ONLY DB)
# =========================================================
@router.delete("/admin/{csr_id}/image/{slot}")
def remove_image(csr_id: int, slot: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):

    if slot not in [1,2,3,4]:
        raise HTTPException(400, "Slot must be between 1-4")

    csr = db.query(CSR).filter(CSR.id == csr_id).first()
    if not csr:
        raise HTTPException(404, "CSR not found")

    csr.images[str(slot)] = None
    db.commit()

    return {"message": f"Image removed from slot {slot}"}


# =========================================================
# ADMIN — SOFT DELETE SECTION (HIDE FROM WEBSITE)
# =========================================================
@router.delete("/admin/{csr_id}")
def soft_delete_csr(csr_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):

    csr = db.query(CSR).filter(CSR.id == csr_id).first()
    if not csr:
        raise HTTPException(404, "CSR not found")

    csr.is_active = False
    db.commit()

    return {"message": "CSR hidden successfully"}


# =========================================================
# ADMIN — PERMANENT DELETE (REMOVE FILES + DB)
# =========================================================
@router.delete("/admin/{csr_id}/permanent")
def permanent_delete(csr_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):

    csr = db.query(CSR).filter(CSR.id == csr_id).first()
    if not csr:
        raise HTTPException(404, "CSR not found")

    # delete images from disk
    for path in csr.images.values():
        if path:
            full_path = os.path.join(os.getcwd(), path)
            if os.path.exists(full_path):
                os.remove(full_path)

    db.delete(csr)
    db.commit()

    return {"message": "CSR permanently deleted"}
