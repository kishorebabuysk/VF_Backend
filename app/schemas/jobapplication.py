from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional, List


# ---------- EDUCATION ----------
class EducationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    highest_qualification: str
    specialization: str
    university: str
    college: str
    year_of_passing: int


# ---------- EXPERIENCE ----------
class ExperienceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    previous_company: str
    previous_role: str
    date_of_joining: date
    relieving_date: date


# ---------- APPLICATION RESPONSE ----------
class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int

    first_name: str
    last_name: str
    full_name: str

    phone: str
    email: str
    date_of_birth: date
    gender: str
    location: str
    pan_number: str
    linkedin_url: Optional[str]

    position_applied: str
    preferred_work_mode: str
    key_skills: str
    expected_salary: int
    why_hire_me: str
    experience_level: str

    pan_card_file: Optional[str]
    resume_file: Optional[str]
    photo_file: Optional[str]

    status: str
    created_at: datetime

    # ONLY DB RELATIONSHIPS
    educations: List[EducationResponse] = []
    experiences: List[ExperienceResponse] = []
