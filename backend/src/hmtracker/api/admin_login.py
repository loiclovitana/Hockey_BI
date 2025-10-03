from datetime import timedelta, datetime, timezone
from os import getenv

import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from hmtracker.services import admin
from hmtracker.common.constants import HM_SECRET_KEY_ENV_NAME

ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = getenv(HM_SECRET_KEY_ENV_NAME)
ENCRYPTION_ALGORITHM = "HS256"

admin_login_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")


def create_access_token(username: str, password: str) -> str:
    if not admin.is_admin(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Encryption on server is unavailable",
        )
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = {
        "username": username,
        "is_admin": True,
        "expiration": expire.isoformat(timespec="minutes"),
    }
    encrypted_token = jwt.encode(token, SECRET_KEY, algorithm=ENCRYPTION_ALGORITHM)

    return encrypted_token


def decode_token(token):
    if SECRET_KEY is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ENCRYPTION_ALGORITHM])
        username = decoded_token.get("username")
        is_admin = decoded_token.get("is_admin", False)
        if username is None or not is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username
