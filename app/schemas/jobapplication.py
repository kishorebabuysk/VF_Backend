from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional, List


# ---------------- EXPERIENCE ----------------
class Experience(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    previous_company: str
    previous_role: str
    date_of_joining: date
    relieving_date: date


# ---------------- BASE ----------------
class ApplicationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    first_name: str
    last_name: str
    phone: str
    email: str
    date_of_birth: date
    gender: str
    location: str
    pan_number: str
    linkedin_url: Optional[str] = None

    highest_qualification: str
    specialization: str
    university: str
    college: str
    year_of_passing: int

    position_applied: str
    preferred_work_mode: str
    key_skills: str
    expected_salary: int
    why_hire_me: str

    experience_level: str
    experience: Optional[List[Experience]] = None

    # VALIDATION
    @field_validator("experience")
    @classmethod
    def validate_experience(cls, v, info):
        if info.data.get("experience_level") == "experienced":
            if not v or len(v) == 0:
                raise ValueError("Experienced candidate must add at least one company")
        return v


# ---------------- CREATE ----------------
class ApplicationCreate(ApplicationBase):
    pass


# ---------------- RESPONSE EXPERIENCE ----------------
class ExperienceResponse(Experience):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------------- RESPONSE ----------------
class ApplicationResponse(ApplicationBase):
    id: int
    full_name: str

    pan_card_file: Optional[str]
    resume_file: Optional[str]
    photo_file: Optional[str]

    status: str
    created_at: datetime

    experiences: Optional[List[ExperienceResponse]]