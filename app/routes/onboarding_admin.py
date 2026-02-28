from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
import os
import shutil
import uuid
from app.utils.jwt_dependency import get_current_admin

from app.database import get_db
from app.models.onboarding import Onboarding
from app.models.onboarding_documents import OnboardingDocument
from app.models.onboarding_nominee import (
    OnboardingNominee,
    OnboardingFamily,
    OnboardingBank,
    OnboardingReference,
    OnboardingExperienceDetails
)
from app.models.onboarding_checklist import OnboardingChecklist
from app.schemas.onboarding import (
    OnboardingPersonalCreate,
    OnboardingResponse,
    NomineeCreate,
    FamilyCreate,
    BankCreate,
    ReferenceCreate,
    ChecklistCreate,
    ExperienceDetailsCreate,
)

router = APIRouter(prefix="/admin/onboarding", tags=["Onboarding"])

UPLOAD_DIR = "uploads/onboarding"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==========================================================
# PERSONAL DETAILS ONLY
# ==========================================================
@router.post("/", response_model=OnboardingResponse)
def create_personal(data: OnboardingPersonalCreate, db: Session = Depends(get_db)):
    if db.query(Onboarding).filter(Onboarding.email == data.email).first():
        raise HTTPException(409, "Email already exists")
    if db.query(Onboarding).filter(Onboarding.aadhar_number == data.aadhar_number).first():
        raise HTTPException(409, "Aadhar already exists")

    onboarding = Onboarding(**data.dict(), status="pending")
    db.add(onboarding)
    db.commit()
    db.refresh(onboarding)
    return onboarding

# ==========================================================
#  NOMINEE
# ==========================================================
@router.post("/{onboarding_id}/nominees")
def add_nominees(
    onboarding_id: int,
    nominees: List[NomineeCreate],
    db: Session = Depends(get_db),
):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")

    for nominee in nominees:
        onboarding.nominees.append(OnboardingNominee(**nominee.dict()))

    db.commit()
    return {"message": "Nominees added successfully"}


# ==========================================================
#  FAMILY
# ==========================================================
@router.post("/{onboarding_id}/family")
def add_family(
    onboarding_id: int,
    family: List[FamilyCreate],
    db: Session = Depends(get_db),
):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")

    for member in family:
        onboarding.family.append(OnboardingFamily(**member.dict()))

    db.commit()
    return {"message": "Family added successfully"}


# ==========================================================
#  BANK
# ==========================================================
@router.post("/{onboarding_id}/bank")
def add_bank(
    onboarding_id: int,
    bank: BankCreate,
    db: Session = Depends(get_db),
):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")

    if onboarding.bank:
        raise HTTPException(status_code=400, detail="Bank already exists")

    onboarding.bank = OnboardingBank(**bank.dict())
    db.commit()

    return {"message": "Bank added successfully"}


# ==========================================================
#  REFERENCES
# ==========================================================
@router.post("/{onboarding_id}/references")
def add_references(
    onboarding_id: int,
    references: List[ReferenceCreate],
    db: Session = Depends(get_db),
):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")

    for ref in references:
        onboarding.references.append(OnboardingReference(**ref.dict()))

    db.commit()
    return {"message": "References added successfully"}


# ==========================================================
#  CHECKLIST
# ==========================================================
@router.post("/{onboarding_id}/checklist")
def add_checklist(
    onboarding_id: int,
    checklist: ChecklistCreate,
    db: Session = Depends(get_db),
):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")

    if onboarding.checklist:
        raise HTTPException(status_code=400, detail="Checklist already exists")

    onboarding.checklist = OnboardingChecklist(**checklist.dict())
    db.commit()

    return {"message": "Checklist added successfully"}


# ==========================================================
#  EXPERIENCE
# ==========================================================
@router.post("/{onboarding_id}/experience")
def add_experience(
    onboarding_id: int,
    experience: ExperienceDetailsCreate,
    db: Session = Depends(get_db),
):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")

    if onboarding.experience_type.lower() != "experienced":
        raise HTTPException(status_code=400, detail="Candidate is not experienced")

    onboarding.experience_details = OnboardingExperienceDetails(**experience.dict())
    db.commit()

    return {"message": "Experience added successfully"}


# ==========================================================
#  DOCUMENTS
# ==========================================================
@router.post("/{onboarding_id}/documents")
def upload_documents(
    onboarding_id: int,
    document_types: List[str] = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")

    if len(document_types) == 1 and "," in document_types[0]:
        document_types = [doc.strip() for doc in document_types[0].split(",")]

    uploaded_documents = []

    for index, file in enumerate(files):

        doc_type = document_types[index] if index < len(document_types) else document_types[-1]

        filename = f"{uuid.uuid4()}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document = OnboardingDocument(
            document_type=doc_type,
            file_path=path,
            file_name=file.filename
        )

        onboarding.documents.append(document)

        uploaded_documents.append({
            "document_type": doc_type,
            "file_name": file.filename
        })

    db.commit()

    return {
        "message": "All documents uploaded successfully",
        "total_uploaded": len(uploaded_documents),
        "documents": uploaded_documents
    }

# ==========================================================
# GET ALL
# ==========================================================
@router.get("/", response_model=List[OnboardingResponse])
def get_all(db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    return db.query(Onboarding).options(
        joinedload(Onboarding.documents),
        joinedload(Onboarding.nominees),
        joinedload(Onboarding.family),
        joinedload(Onboarding.bank),
        joinedload(Onboarding.references),
        joinedload(Onboarding.checklist),
        joinedload(Onboarding.experience_details),
    ).all()


# ==========================================================
# GET BY ID
# ==========================================================
@router.get("/{onboarding_id}", response_model=OnboardingResponse)
def get_by_id(onboarding_id: int, db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    onboarding = db.query(Onboarding).options(
        joinedload(Onboarding.documents),
        joinedload(Onboarding.nominees),
        joinedload(Onboarding.family),
        joinedload(Onboarding.bank),
        joinedload(Onboarding.references),
        joinedload(Onboarding.checklist),
        joinedload(Onboarding.experience_details),
    ).filter(Onboarding.id == onboarding_id).first()

    if not onboarding:
        raise HTTPException(status_code=404, detail="Not found")

    return onboarding


# ==========================================================
# DELETE
# ==========================================================
@router.delete("/{onboarding_id}")
def delete(onboarding_id: int, db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Not found")

    for doc in onboarding.documents:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)

    db.delete(onboarding)
    db.commit()

    return {"message": "Deleted successfully"}


# ==========================================================
# DELETE BY ID
# ==========================================================
@router.delete("/delete_id/{onboarding_id}")
def delete_by_id(onboarding_id: int, db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    onboarding = db.get(Onboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Not found")

    for doc in onboarding.documents:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)

    db.delete(onboarding)
    db.commit()