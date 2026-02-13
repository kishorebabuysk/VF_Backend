from fastapi import APIRouter, Depends, Form, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session, joinedload
from typing import List
import os
import shutil
import uuid

from app.database import get_db
from app.schemas.onboarding import OnboardingCreate, OnboardingResponse
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
from app.utils.jwt_dependency import get_current_admin

UPLOAD_DIR = "uploads/onboarding"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/admin/onboarding", tags=["Onboarding"])

@router.post("/{onboarding_id}/upload-documents")
def upload_multiple_documents(
    onboarding_id: int,
    document_types: List[str] = Form(default=[]),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    """
    Upload multiple documents for an onboarding record.
    Completely flexible - accepts 0 to unlimited documents.
    No restrictions on count or type.
    """
    # Check if onboarding exists
    onboarding = db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")
    
    # If no files provided, return success with 0 count
    if len(files) == 0:
        return {
            "message": "No documents uploaded",
            "count": 0,
            "documents": []
        }
    
    # Validate that document_types and files count match
    if len(document_types) != len(files):
        raise HTTPException(
            status_code=400, 
            detail=f"Number of document_types ({len(document_types)}) must match number of files ({len(files)})"
        )
    
    saved_docs = []
    
    # Process and save each file
    for doc_type, file in zip(document_types, files):
        # Validate file
        if not file.filename:
            continue  # Skip files with invalid names instead of erroring
        
        # Get safe filename
        safe_name = os.path.basename(file.filename)
        
        # Generate unique filename to prevent collisions
        filename = f"{uuid.uuid4()}_{safe_name}"
        path = os.path.join(UPLOAD_DIR, filename)
        
        try:
            # Save file to disk
            with open(path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create database record
            doc = OnboardingDocument(
                document_type=doc_type,
                file_path=path,
                file_name=safe_name,
                onboarding_id=onboarding_id
            )
            db.add(doc)
            saved_docs.append({
                "document_type": doc_type,
                "file_name": safe_name,
                "file_path": path
            })
            
        except Exception as e:
            # If file save fails, rollback and clean up
            db.rollback()
            # Try to remove the file if it was created
            if os.path.exists(path):
                os.remove(path)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload {safe_name}: {str(e)}"
            )
    
    # Commit all documents to database
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save documents to database: {str(e)}"
        )
    
    return {
        "message": f"Documents uploaded successfully" if len(saved_docs) > 0 else "No documents uploaded",
        "count": len(saved_docs),
        "documents": saved_docs
    }

@router.post("/", response_model=OnboardingResponse)
def create_onboarding(
    data: OnboardingCreate,
    db: Session = Depends(get_db)
):
    """Create a new onboarding record"""
    try:
        # Check if onboarding already exists for this email
        existing = (
            db.query(Onboarding)
            .filter(Onboarding.email == data.email)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Onboarding already submitted for this user"
            )
        
        # Create main onboarding record
        onboarding = Onboarding(
            name=data.name,
            dob=data.dob,
            marital_status=data.marital_status,
            gender=data.gender,
            aadhar_number=data.aadhar_number,
            father_name=data.father_name,
            mother_name=data.mother_name,
            spouse_name=data.spouse_name,
            communication_address=data.communication_address,
            permanent_address=data.permanent_address,
            landline_number=data.landline_number,
            mobile_number=data.mobile_number,
            email=data.email,
            blood_group=data.blood_group,
            emergency_contact1=data.emergency_contact1,
            emergency_contact2=data.emergency_contact2,
            education_qualification=data.education_qualification,
            driving_license=data.driving_license,
            vehicle_number=data.vehicle_number,
            applied_role=data.applied_role,
            experience_type=data.experience_type,
            status="pending",
        )
        
        db.add(onboarding)
        db.flush()
        
        # ================= DOCUMENTS =================
        if data.documents:
            for doc in data.documents:
                onboarding.documents.append(
                    OnboardingDocument(
                        document_type=doc.document_type,
                        file_path=doc.file_path,
                        file_name=doc.file_name,
                        onboarding_id=onboarding.id
                    )
                )
        
        # ================= NOMINEES (Multiple entries allowed) =================
        if data.nominees:
            for nominee in data.nominees:
                onboarding.nominees.append(
                    OnboardingNominee(
                        nominee_type=nominee.nominee_type,
                        name=nominee.name,
                        age=nominee.age,
                        dob=nominee.dob,
                        relationship_type=nominee.relationship_type,
                        onboarding_id=onboarding.id
                    )
                )
        
        # ================= FAMILY (Multiple entries allowed) =================
        if data.family:
            for member in data.family:
                onboarding.family.append(
                    OnboardingFamily(
                        name=member.name,
                        dob=member.dob,
                        relationship_type=member.relationship_type,
                        onboarding_id=onboarding.id
                    )
                )
        
        # ================= BANK =================
        if data.bank:
            onboarding.bank = OnboardingBank(
                account_name=data.bank.account_name,
                account_number=data.bank.account_number,
                ifsc_code=data.bank.ifsc_code,
                branch_name=data.bank.branch_name,
                onboarding_id=onboarding.id
            )
        
        # ================= REFERENCES (Multiple entries allowed) =================
        if data.references:
            for ref in data.references:
                onboarding.references.append(
                    OnboardingReference(
                        name=ref.name,
                        designation=ref.designation,
                        phone=ref.phone,
                        email=ref.email,
                        last_employer=ref.last_employer,
                        relationship_with_candidate=ref.relationship_with_candidate,
                        onboarding_id=onboarding.id
                    )
                )
        
        # ================= EXPERIENCE DETAILS (Only for experienced) =================
        if data.experience_type.lower() == "experienced" and data.experience_details:
            onboarding.experience_details = OnboardingExperienceDetails(
                company_name=data.experience_details.company_name,
                job_role=data.experience_details.job_role,
                date_of_joining=data.experience_details.date_of_joining,
                date_of_exit=data.experience_details.date_of_exit,
                total_experience=data.experience_details.total_experience,
                esi_number=data.experience_details.esi_number,
                uan_number=data.experience_details.uan_number,
                onboarding_id=onboarding.id
            )
        
        # ================= CHECKLIST =================
        if data.checklist:
            onboarding.checklist = OnboardingChecklist(
                experience_type=data.checklist.experience_type,
                # Common fields
                aadhar_card=data.checklist.aadhar_card,
                qualification_certificates=data.checklist.qualification_certificates,
                bank_account_proof=data.checklist.bank_account_proof,
                pan_card=data.checklist.pan_card,
                passport_size_photo=data.checklist.passport_size_photo,
                employee_reference=data.checklist.employee_reference,
                # Fresher only
                internship_proof=data.checklist.internship_proof or False,
                # Experienced only
                last_3_months_pay_slips=data.checklist.last_3_months_pay_slips or False,
                offer_letter=data.checklist.offer_letter or False,
                hike_letter=data.checklist.hike_letter or False,
                experience_letter=data.checklist.experience_letter or False,
                relieving_letter=data.checklist.relieving_letter or False,
                onboarding_id=onboarding.id
            )
        
        db.commit()
        db.refresh(onboarding)
        
        return onboarding
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[OnboardingResponse])
def list_onboardings(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """List all onboarding records"""
    onboardings = (
        db.query(Onboarding)
        .options(
            joinedload(Onboarding.documents),
            joinedload(Onboarding.nominees),
            joinedload(Onboarding.family),
            joinedload(Onboarding.bank),
            joinedload(Onboarding.references),
            joinedload(Onboarding.checklist),
            joinedload(Onboarding.experience_details),
        )
        .all()
    )
    
    return onboardings

@router.get("/{onboarding_id}", response_model=OnboardingResponse)
def get_onboarding_by_id(
    onboarding_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Get a specific onboarding record by ID"""
    onboarding = (
        db.query(Onboarding)
        .options(
            joinedload(Onboarding.documents),
            joinedload(Onboarding.nominees),
            joinedload(Onboarding.family),
            joinedload(Onboarding.bank),
            joinedload(Onboarding.references),
            joinedload(Onboarding.checklist),
            joinedload(Onboarding.experience_details),
        )
        .filter(Onboarding.id == onboarding_id)
        .first()
    )
    
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")
    
    return onboarding

@router.put("/{onboarding_id}", response_model=OnboardingResponse)
def update_onboarding(
    onboarding_id: int,
    data: OnboardingCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Update an existing onboarding record"""
    try:
        onboarding = db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()
        if not onboarding:
            raise HTTPException(status_code=404, detail="Onboarding not found")
        
        # Update main fields
        onboarding.name = data.name
        onboarding.dob = data.dob
        onboarding.marital_status = data.marital_status
        onboarding.gender = data.gender
        onboarding.aadhar_number = data.aadhar_number
        onboarding.father_name = data.father_name
        onboarding.mother_name = data.mother_name
        onboarding.spouse_name = data.spouse_name
        onboarding.communication_address = data.communication_address
        onboarding.permanent_address = data.permanent_address
        onboarding.landline_number = data.landline_number
        onboarding.mobile_number = data.mobile_number
        onboarding.email = data.email
        onboarding.blood_group = data.blood_group
        onboarding.emergency_contact1 = data.emergency_contact1
        onboarding.emergency_contact2 = data.emergency_contact2
        onboarding.education_qualification = data.education_qualification
        onboarding.driving_license = data.driving_license
        onboarding.vehicle_number = data.vehicle_number
        onboarding.applied_role = data.applied_role
        onboarding.experience_type = data.experience_type
        
        # Clear and update nominees
        onboarding.nominees.clear()
        if data.nominees:
            for nominee in data.nominees:
                onboarding.nominees.append(
                    OnboardingNominee(
                        nominee_type=nominee.nominee_type,
                        name=nominee.name,
                        age=nominee.age,
                        dob=nominee.dob,
                        relationship_type=nominee.relationship_type,
                        onboarding_id=onboarding.id
                    )
                )
        
        # Clear and update family
        onboarding.family.clear()
        if data.family:
            for member in data.family:
                onboarding.family.append(
                    OnboardingFamily(
                        name=member.name,
                        dob=member.dob,
                        relationship_type=member.relationship_type,
                        onboarding_id=onboarding.id
                    )
                )
        
        # Update bank
        if onboarding.bank:
            db.delete(onboarding.bank)
        if data.bank:
            onboarding.bank = OnboardingBank(
                account_name=data.bank.account_name,
                account_number=data.bank.account_number,
                ifsc_code=data.bank.ifsc_code,
                branch_name=data.bank.branch_name,
                onboarding_id=onboarding.id
            )
        
        # Clear and update references
        onboarding.references.clear()
        if data.references:
            for ref in data.references:
                onboarding.references.append(
                    OnboardingReference(
                        name=ref.name,
                        designation=ref.designation,
                        phone=ref.phone,
                        email=ref.email,
                        last_employer=ref.last_employer,
                        relationship_with_candidate=ref.relationship_with_candidate,
                        onboarding_id=onboarding.id
                    )
                )
        
        # Update experience details
        if onboarding.experience_details:
            db.delete(onboarding.experience_details)
        if data.experience_type.lower() == "experienced" and data.experience_details:
            onboarding.experience_details = OnboardingExperienceDetails(
                company_name=data.experience_details.company_name,
                job_role=data.experience_details.job_role,
                date_of_joining=data.experience_details.date_of_joining,
                date_of_exit=data.experience_details.date_of_exit,
                total_experience=data.experience_details.total_experience,
                esi_number=data.experience_details.esi_number,
                uan_number=data.experience_details.uan_number,
                onboarding_id=onboarding.id
            )
        
        # Update checklist
        if onboarding.checklist:
            db.delete(onboarding.checklist)
        if data.checklist:
            onboarding.checklist = OnboardingChecklist(
                experience_type=data.checklist.experience_type,
                aadhar_card=data.checklist.aadhar_card,
                qualification_certificates=data.checklist.qualification_certificates,
                bank_account_proof=data.checklist.bank_account_proof,
                pan_card=data.checklist.pan_card,
                passport_size_photo=data.checklist.passport_size_photo,
                employee_reference=data.checklist.employee_reference,
                internship_proof=data.checklist.internship_proof or False,
                last_3_months_pay_slips=data.checklist.last_3_months_pay_slips or False,
                offer_letter=data.checklist.offer_letter or False,
                hike_letter=data.checklist.hike_letter or False,
                experience_letter=data.checklist.experience_letter or False,
                relieving_letter=data.checklist.relieving_letter or False,
                onboarding_id=onboarding.id
            )
        
        db.commit()
        db.refresh(onboarding)
        
        return onboarding
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{onboarding_id}")
def delete_onboarding(
    onboarding_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Delete a specific onboarding record"""
    onboarding = db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")
    
    # Delete associated files
    for document in onboarding.documents:
        if os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                print(f"Error deleting file {document.file_path}: {str(e)}")
    
    db.delete(onboarding)
    db.commit()
    
    return {
        "message": "Onboarding deleted permanently",
        "onboarding_id": onboarding_id
    }

@router.delete("/bulk-delete/")
def bulk_delete_onboardings(
    onboarding_ids: List[int] = Query(...),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Delete multiple onboarding records"""
    onboardings = db.query(Onboarding).filter(Onboarding.id.in_(onboarding_ids)).all()
    
    if not onboardings:
        raise HTTPException(
            status_code=404,
            detail="No onboardings found for the provided IDs"
        )
    
    # Delete associated files
    for onboarding in onboardings:
        for document in onboarding.documents:
            if os.path.exists(document.file_path):
                try:
                    os.remove(document.file_path)
                except Exception as e:
                    print(f"Error deleting file {document.file_path}: {str(e)}")
    
    for onboarding in onboardings:
        db.delete(onboarding)
    
    db.commit()
    
    return {
        "message": f"Deleted {len(onboardings)} onboardings successfully"
    }


@router.get("/{onboarding_id}/documents")
def get_onboarding_documents(
    onboarding_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Get all documents for a specific onboarding record"""
    onboarding = db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")
    
    documents = db.query(OnboardingDocument).filter(
        OnboardingDocument.onboarding_id == onboarding_id
    ).all()
    
    return {
        "onboarding_id": onboarding_id,
        "count": len(documents),
        "documents": [
            {
                "id": doc.id,
                "document_type": doc.document_type,
                "file_name": doc.file_name,
                "file_path": doc.file_path,
                "uploaded_at": doc.uploaded_at
            }
            for doc in documents
        ]
    }