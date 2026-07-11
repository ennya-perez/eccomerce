from app.models.user import AppUser
from app.schemas.token_schema import TokenData
from app.core.db import SessionDep
from app.core.config import settings
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlalchemy import func


ALGORITHM = "HS256"
password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token/login")

def verify_password(plain_password, hashed_password):
    return password_hasher.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hasher.hash(password)

def get_user(db: SessionDep, username: str):
    clean_username = username.strip().lower()
    statement = select(AppUser).where(AppUser.username == clean_username)
    user = db.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def authenticate_user(session: SessionDep, username: str, password: str):
    user = get_user(session, username)
    if not isinstance(user, AppUser):
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
 session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            print("El username es None")
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        print("Es un PyJWT error")
        raise credentials_exception
    user = get_user(session, username=token_data.username)
    if user is None:
        print("Es una excepcion de credenciales")
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[AppUser, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user
