from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base
from datetime import datetime


class CSR(Base):
    __tablename__ = "csr_sections"

    id = Column(Integer, primary_key=True, index=True)

    posted_at = Column(DateTime, index=True)

    title = Column(String(200), nullable=False)

    image1 = Column(String(500), nullable=False)
    image2 = Column(String(500), nullable=False)
    image3 = Column(String(500), nullable=False)
    image4 = Column(String(500), nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)