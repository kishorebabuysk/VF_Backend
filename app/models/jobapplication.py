from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer)

    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(200))

    phone = Column(String(20))
    email = Column(String(150))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    location = Column(String(150))

    pan_number = Column(String(20))
    linkedin_url = Column(String(255))

    highest_qualification = Column(String(100))
    specialization = Column(String(100))
    university = Column(String(150))
    college = Column(String(150))
    year_of_passing = Column(Integer)

    position_applied = Column(String(100))
    preferred_work_mode = Column(String(50))
    key_skills = Column(Text)
    expected_salary = Column(Integer)
    why_hire_me = Column(Text)

    experience_level = Column(String(50))

    pan_card_file = Column(String(255))
    resume_file = Column(String(255))
    photo_file = Column(String(255))

    status = Column(String(50), default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ CORRECT RELATIONSHIP NAME
    experiences = relationship(
        "ApplicationExperience",
        back_populates="application",
        cascade="all, delete-orphan"
    )


class ApplicationExperience(Base):
    __tablename__ = "application_experience"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"))

    previous_company = Column(String(150))
    previous_role = Column(String(150))
    date_of_joining = Column(Date)
    relieving_date = Column(Date)

    # ✅ MUST MATCH ABOVE
    application = relationship("Application", back_populates="experiences")

