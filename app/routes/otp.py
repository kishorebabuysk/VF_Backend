from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.otp import OTP
from app.models.admin import Admin
from app.schemas.admin import ForgotPasswordRequest,VerifyOTPRequest,ResetPasswordRequest
from app.utils.otp import generate_otp, otp_expiry
from app.utils.email import send_otp_email
from app.utils.auth import hash_password

router = APIRouter(prefix="/auth", tags=["Admin"])
'''
@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    otp = generate_otp()
    record = OTP(
        email=email,
        otp_code=otp,
        expires_at=otp_expiry()
    )

    db.add(record)
    db.commit()

    try:
        send_otp_email(email, otp)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )

    return {"message": "OTP sent to email"}


@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    record = (
        db.query(OTP)
        .filter(OTP.email == data.email, OTP.otp_code == data.otp)
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not record or record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    return {"message": "OTP verified"}



@router.post("/reset-password")
def reset_password(email: str, new_password: str, otp: str, db: Session = Depends(get_db)):
    record = (
        db.query(OTP)
        .filter(
            OTP.email == email,
            OTP.otp_code == otp,
            OTP.expires_at > datetime.utcnow()
        )
        .first()
    )

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    admin = db.query(Admin).filter(Admin.email == email).first()
    admin.password_hash = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}'''
'''
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == data.email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    otp = generate_otp()

    db.query(OTP).filter(OTP.email == data.email).delete()

    record = OTP(
        email=data.email,
        otp_code=otp,
        expires_at=otp_expiry()
    )
    db.add(record)
    db.commit()

    send_otp_email(data.email, otp)
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    record = db.query(OTP).filter(
        OTP.email == data.email,
        OTP.otp_code == data.otp,
        OTP.is_used == False,
        OTP.expires_at > datetime.utcnow()
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    record.is_used = True
    db.commit()

    return {"message": "OTP verified"}

@router.post("/reset-password")
def reset_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    record = db.query(OTP).filter(
        OTP.email == data.email,
        OTP.is_used == True
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="OTP not verified")

    admin = db.query(Admin).filter(Admin.email == data.email).first()
    admin.password_hash = hash_password(data.new_password)

    db.delete(record)
    db.commit()

    return {"message": "Password reset successful"}'''


