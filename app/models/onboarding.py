from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Onboarding(Base):
    __tablename__ = "onboarding"

    id = Column(Integer, primary_key=True, index=True)

    # Personal Information
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    marital_status = Column(String(255))
    gender = Column(String(20), nullable=False)
    aadhar_number = Column(String(20), nullable=False, unique=True)
    father_name = Column(String(255))
    mother_name = Column(String(255))
    spouse_name = Column(String(255))
    communication_address = Column(Text, nullable=False)
    permanent_address = Column(Text, nullable=False)
    landline_number = Column(String(20))
    mobile_number = Column(String(15), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    blood_group = Column(String(10))
    emergency_contact1 = Column(String(15), nullable=False)
    emergency_contact2 = Column(String(15))
    education_qualification = Column(String(255))
    driving_license = Column(String(50))
    vehicle_number = Column(String(50))
    applied_role = Column(String(255), nullable=False)
    experience_type = Column(String(50), nullable=False)

    status = Column(String(20), default="pending")

    # Relationships
    documents = relationship("OnboardingDocument", back_populates="onboarding", cascade="all, delete-orphan")
    nominees = relationship("OnboardingNominee", back_populates="onboarding", cascade="all, delete-orphan")
    family = relationship("OnboardingFamily", back_populates="onboarding", cascade="all, delete-orphan")
    bank = relationship("OnboardingBank", back_populates="onboarding", uselist=False, cascade="all, delete-orphan")
    references = relationship("OnboardingReference", back_populates="onboarding", cascade="all, delete-orphan")
    checklist = relationship("OnboardingChecklist", back_populates="onboarding", uselist=False, cascade="all, delete-orphan")
    experience_details = relationship("OnboardingExperienceDetails", back_populates="onboarding", uselist=False, cascade="all, delete-orphan")