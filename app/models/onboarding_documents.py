from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class OnboardingDocument(Base):
    __tablename__ = "onboarding_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now())
    
    onboarding_id = Column(Integer, ForeignKey("onboarding.id"))
    onboarding = relationship("Onboarding", back_populates="documents")