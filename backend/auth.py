import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import User

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_ISSUER = "ai-document-assistant"

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing. Add it to your environment file."
    )

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return a secure hash of a password."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int, email: str) -> str:
    """Create a signed JWT that expires after 60 minutes."""
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "email": email,
        "iss": JWT_ISSUER,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Validate a JWT and return its claims."""
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        options={"require": ["sub", "exp", "iss"]},
    )
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db: Session = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User account not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
    finally:
        db.close()