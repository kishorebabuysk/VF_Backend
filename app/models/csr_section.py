# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database import Base


# class CSRSection(Base):
#     __tablename__ = "csr_sections"

#     id = Column(Integer, primary_key=True, index=True)
#     csr_id = Column(Integer, ForeignKey("csr.id", ondelete="CASCADE"))

#     title = Column(String(200), nullable=False)

#     image1 = Column(String(500))
#     image2 = Column(String(500))
#     image3 = Column(String(500))
#     image4 = Column(String(500))

#     csr = relationship("CSR", back_populates="sections")
