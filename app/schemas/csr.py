from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class CSRBase(BaseModel):
    title: str
    image1: str
    image2: str
    image3: str
    image4: str


class CSRCreate(BaseModel):
    sections: List[CSRBase]


class CSRUpdate(BaseModel):
    title: Optional[str] = None
    image1: Optional[str] = None
    image2: Optional[str] = None
    image3: Optional[str] = None
    image4: Optional[str] = None


class CSRResponse(CSRBase):
    id: int
    posted_at: datetime

    class Config:
        from_attributes = True