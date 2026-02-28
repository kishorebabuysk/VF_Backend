from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import date, datetime
from typing import List, Optional

# Personal Create
class OnboardingPersonalCreate(BaseModel):
    name: str
    dob: date
    marital_status: Optional[str] = None
    gender: str
    aadhar_number: str
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    spouse_name: Optional[str] = None
    communication_address: str
    permanent_address: str
    landline_number: Optional[str] = None
    mobile_number: str
    email: EmailStr
    blood_group: Optional[str] = None
    emergency_contact1: str
    emergency_contact2: Optional[str] = None
    education_qualification: Optional[str] = None
    driving_license: Optional[str] = None
    vehicle_number: Optional[str] = None
    applied_role: str
    experience_type: str

# -------- Documents --------
class DocumentCreate(BaseModel):
    document_type: str
    file_path: str
    file_name: Optional[str] = None

class DocumentResponse(DocumentCreate):
    id: int
    uploaded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# -------- Nominee --------
class NomineeCreate(BaseModel):
    nominee_type: str  # PF / ESI / Accident
    name: str
    age: Optional[int] = None
    dob: date
    relationship_type: str

class NomineeResponse(NomineeCreate):
    id: int
    
    class Config:
        from_attributes = True

# -------- Family --------
class FamilyCreate(BaseModel):
    name: str
    dob: date
    relationship_type: str

class FamilyResponse(FamilyCreate):
    id: int
    
    class Config:
        from_attributes = True

# -------- Bank --------
class BankCreate(BaseModel):
    account_name: str
    account_number: str
    ifsc_code: str
    branch_name: str

class BankResponse(BankCreate):
    id: int
    
    class Config:
        from_attributes = True

# -------- References --------
class ReferenceCreate(BaseModel):
    name: str
    designation: str
    phone: str
    email: Optional[EmailStr] = None
    last_employer: str
    relationship_with_candidate: str

class ReferenceResponse(ReferenceCreate):
    id: int
    
    class Config:
        from_attributes = True


# -------- Experience Details --------
class ExperienceDetailsCreate(BaseModel):
    company_name: str
    job_role: str
    date_of_joining: date
    date_of_exit: date
    total_experience: str
    esi_number: Optional[str] = None
    uan_number: Optional[str] = None

class ExperienceDetailsResponse(ExperienceDetailsCreate):
    id: int
    
    class Config:
        from_attributes = True

# -------- Checklist --------
class ChecklistCreate(BaseModel):
    experience_type: str  # fresher / experienced
    
    # Common for both fresher and experienced
    aadhar_card: bool = False
    qualification_certificates: bool = False
    bank_account_proof: bool = False
    pan_card: bool = False
    passport_size_photo: bool = False
    employee_reference: bool = False
    
    # Fresher only
    internship_proof: Optional[bool] = False
    
    # Experienced only
    last_3_months_pay_slips: Optional[bool] = False
    offer_letter: Optional[bool] = False
    hike_letter: Optional[bool] = False
    experience_letter: Optional[bool] = False
    relieving_letter: Optional[bool] = False

class ChecklistResponse(ChecklistCreate):
    id: int
    
    class Config:
        from_attributes = True

# -------- Main Onboarding --------
class OnboardingCreate(BaseModel):
    # Personal Info
    name: str
    dob: date
    marital_status: Optional[str] = None
    gender: str
    aadhar_number: str
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    spouse_name: Optional[str] = None
    communication_address: str
    permanent_address: str
    landline_number: Optional[str] = None
    mobile_number: str
    email: EmailStr
    blood_group: Optional[str] = None
    emergency_contact1: str
    emergency_contact2: Optional[str] = None
    education_qualification: Optional[str] = None
    driving_license: Optional[str] = None
    vehicle_number: Optional[str] = None
    applied_role: str
    experience_type: str
    

    documents: Optional[List[DocumentCreate]] = []
    nominees: List[NomineeCreate]
    family: List[FamilyCreate]
    bank: BankCreate
    references: List[ReferenceCreate]
    checklist: ChecklistCreate
    experience_details: Optional[ExperienceDetailsCreate] = None
    
    @model_validator(mode="after")
    def validate_experienced_fields(self):
        if self.experience_type.lower() == "experienced":
            if not self.experience_details:
                raise ValueError("Experience details are required for experienced candidates")
        return self

class OnboardingResponse(BaseModel):
    id: int
    name: str
    dob: date
    marital_status: Optional[str]
    gender: str
    aadhar_number: str
    father_name: Optional[str]
    mother_name: Optional[str]
    spouse_name: Optional[str]
    communication_address: str
    permanent_address: str
    landline_number: Optional[str]
    mobile_number: str
    email: str
    blood_group: Optional[str]
    emergency_contact1: str
    emergency_contact2: Optional[str]
    education_qualification: Optional[str]
    driving_license: Optional[str]
    vehicle_number: Optional[str]
    applied_role: str
    experience_type: str
    status: str
    
    documents: Optional[List[DocumentResponse]] = []
    nominees: List[NomineeResponse] = []
    family: List[FamilyResponse] = []
    references: List[ReferenceResponse] = []
    bank: Optional[BankResponse] = None
    checklist: Optional[ChecklistResponse] = None
    experience_details: Optional[ExperienceDetailsResponse] = None
    
    class Config:
        from_attributes = True