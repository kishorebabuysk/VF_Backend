from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.jwt_dependency import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/me")
def get_admin_profile(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    return {
        "id": admin.id,
        "email": admin.email,
        "is_active": admin.is_active
    }
