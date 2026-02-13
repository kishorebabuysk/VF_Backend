from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class OnboardingChecklist(Base):
    __tablename__ = "onboarding_checklist"
    
    id = Column(Integer, primary_key=True, index=True)
    experience_type = Column(String(20), nullable=False)  # fresher / experienced
    
    # Common for both fresher and experienced
    aadhar_card = Column(Boolean, default=False)
    qualification_certificates = Column(Boolean, default=False)
    bank_account_proof = Column(Boolean, default=False)
    pan_card = Column(Boolean, default=False)
    passport_size_photo = Column(Boolean, default=False)
    employee_reference = Column(Boolean, default=False)
    
    # Fresher only
    internship_proof = Column(Boolean, default=False)
    
    # Experienced only
    last_3_months_pay_slips = Column(Boolean, default=False)
    offer_letter = Column(Boolean, default=False)
    hike_letter = Column(Boolean, default=False)
    experience_letter = Column(Boolean, default=False)
    relieving_letter = Column(Boolean, default=False)
    
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="checklist")