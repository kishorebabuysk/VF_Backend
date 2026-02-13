from fastapi import APIRouter, Depends, HTTPException
#from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminLoginRequest, TokenResponse, ChangePasswordRequest
from app.utils.auth import (
    verify_password,
    hash_password,
    create_access_token
)
from app.utils.jwt_dependency import get_current_admin
from app.utils.email import send_otp_email
from app.utils.otp import generate_otp, otp_expiry

router = APIRouter(prefix="/admin", tags=["Admin Auth"])


# -------------------- LOGIN --------------------
@router.post("/login", response_model=TokenResponse)
def admin_login(
    data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == data.email).first()

    if not admin or not verify_password(
        data.password,
        admin.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "sub": admin.email,
        "role": "admin"
    })

    return {"access_token": token, "token_type": "bearer"}


# -------------------- CHANGE PASSWORD --------------------
@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # 1️⃣ Check current password
    if not verify_password(
        data.current_password,
        current_admin.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    # 2️⃣ Check new password and confirm password match
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="New password and confirm password do not match"
        )

    # 4️⃣ Update password
    current_admin.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


# -------------------- FORGOT PASSWORD --------------------
@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Email not registered")

    otp = generate_otp()
    admin.otp = otp
    admin.otp_expiry = otp_expiry()
    db.commit()

    send_otp_email(email, otp)
    return {"message": "OTP sent successfully"}


# -------------------- VERIFY OTP --------------------
@router.post("/verify-otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or admin.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if admin.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    reset_token = str(uuid.uuid4())
    admin.reset_token = reset_token
    admin.reset_token_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    return {"message": "OTP verified", "reset_token": reset_token}


# -------------------- RESET PASSWORD --------------------
@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.reset_token == token).first()
    if not admin:
        raise HTTPException(status_code=400, detail="Invalid token")

    if admin.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    admin.password_hash = hash_password(new_password)
    admin.otp = None
    admin.reset_token = None
    admin.reset_token_expiry = None
    db.commit()

    return {"message": "Password reset successful"}