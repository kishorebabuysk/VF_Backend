from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    title: str
    department: str
    work_mode: str
    roles_responsibilities: str

    required_skills: Optional[str] = None
    selected_skills: List[str] = Field(default_factory=list)

    experience_min: int
    experience_max: int
    qualification_required: str
    salary_min: int
    salary_max: int

    perks_benefits: Optional[str] = None
    job_location: str
    job_locality: Optional[str] = None
    openings: int
    application_deadline: date


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    work_mode: Optional[str] = None
    roles_responsibilities: Optional[str] = None
    required_skills: Optional[str] = None
    selected_skills: Optional[List[str]] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    qualification_required: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    perks_benefits: Optional[str] = None
    job_location: Optional[str] = None
    job_locality: Optional[str] = None
    openings: Optional[int] = None
    application_deadline: Optional[date] = None


class JobResponse(JobBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedJobResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[JobResponse]
