from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class CSR(Base):
    __tablename__ = "csr"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)

    # store only file paths in DB
    images = Column(JSON, nullable=False, default=lambda: [])

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
