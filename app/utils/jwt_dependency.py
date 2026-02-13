from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.admin import Admin


# Use HTTP Bearer instead of OAuth2PasswordBearer
security = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract token from "Authorization: Bearer <token>"
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        email = payload.get("sub")
        role = payload.get("role")

        if email is None or role != "admin":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    admin = (
        db.query(Admin)
        .filter(
            Admin.email == email,
            Admin.is_active == True
        )
        .first()
    )

    if not admin:
        raise credentials_exception

    return admin
