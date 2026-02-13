from sqlalchemy import JSON, Column, Integer, String, Float, Text, Date, DateTime, func
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    work_mode = Column(String(50))
    roles_responsibilities = Column(Text)
    #required_skills = Column(Text)
    #required_skills = Column(JSON, nullable=False, default=list)
    required_skills = Column(Text, nullable=True)      # manual textbox
    selected_skills = Column(JSON, nullable=False, default=list)  # chip selection

    experience_min = Column(Integer)
    experience_max = Column(Integer)

    qualification_required = Column(String(255))

    salary_min = Column(Integer)
    salary_max = Column(Integer)

    perks_benefits = Column(Text)

    job_location = Column(String(100))
    job_locality = Column(String(100))

    openings = Column(Integer)

    application_deadline = Column(Date)
    created_at = Column(DateTime, default=func.now())