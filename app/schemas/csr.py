from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


# Image object returned to frontend
class CSRImage(BaseModel):
    id: str
    path: str


class CSRCreate(BaseModel):
    title: str
    images: List[str] = Field(default_factory=list)   # still send paths


class CSRUpdate(BaseModel):
    title: Optional[str] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class CSRResponse(BaseModel):
    id: int
    title: str
    images: List[CSRImage]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
