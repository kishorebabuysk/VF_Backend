from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class OnboardingNominee(Base):
    __tablename__ = "onboarding_nominees"
    id = Column(Integer, primary_key=True)
    nominee_type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    dob = Column(Date, nullable=False)
    relationship_type = Column(String(100), nullable=False)
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="nominees")


class OnboardingFamily(Base):
    __tablename__ = "onboarding_family"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    relationship_type = Column(String(100), nullable=False)
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="family")


class OnboardingBank(Base):
    __tablename__ = "onboarding_bank"
    id = Column(Integer, primary_key=True)
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(255), nullable=False)
    ifsc_code = Column(String(50), nullable=False)
    branch_name = Column(String(255), nullable=False)
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="bank")


class OnboardingReference(Base):
    __tablename__ = "onboarding_references"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255))
    last_employer = Column(String(255), nullable=False)
    relationship_with_candidate = Column(String(255), nullable=False)
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="references")


class OnboardingChecklist(Base):
    __tablename__ = "onboarding_checklist"
    id = Column(Integer, primary_key=True)
    experience_type = Column(String(20), nullable=False)
    aadhar_card = Column(Boolean, default=False)
    qualification_certificates = Column(Boolean, default=False)
    bank_account_proof = Column(Boolean, default=False)
    pan_card = Column(Boolean, default=False)
    passport_size_photo = Column(Boolean, default=False)
    employee_reference = Column(Boolean, default=False)
    internship_proof = Column(Boolean, default=False)
    last_3_months_pay_slips = Column(Boolean, default=False)
    offer_letter = Column(Boolean, default=False)
    hike_letter = Column(Boolean, default=False)
    experience_letter = Column(Boolean, default=False)
    relieving_letter = Column(Boolean, default=False)
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="checklist")


class OnboardingExperienceDetails(Base):
    __tablename__ = "onboarding_experience_details"
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    job_role = Column(String(255), nullable=False)
    date_of_joining = Column(Date, nullable=False)
    date_of_exit = Column(Date, nullable=False)
    total_experience = Column(String(100), nullable=False)
    esi_number = Column(String(100))
    uan_number = Column(String(100))
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="experience_details")


class OnboardingDocument(Base):
    __tablename__ = "onboarding_documents"
    id = Column(Integer, primary_key=True)
    document_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255))
    uploaded_at = Column(DateTime, server_default=func.now())
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="documents")