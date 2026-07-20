from fastapi import APIRouter
from app.models.user import AppUser
from app.core.security import authenticate_user, create_access_token, password_hasher
from app.core.config import settings
from app.schemas.token_schema import Token
from app.services.email_services import EmailType
from sqlmodel import Session, select
from typing import Annotated
from fastapi import Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.core.db import get_session, SessionDep
from app.schemas.user_schema import UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])





@router.post("/token/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
session: SessionDep) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_users = session.get(AppUser, user.id)
    data_user = user.model_dump()
    db_users.sqlmodel_update(data_user)
    session.add(db_users)
    session.commit()
    session.refresh(db_users)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post("/sign-up", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def sign_up(session: SessionDep, user: UserCreate, background_tasks: BackgroundTasks):
    """
    ## Registro de usuario:
    - username: str
    - email: EmailStr
    - password: str
    - bio: Optional[str]
    """
    
    statement = select(AppUser).where((AppUser.email == user.email.lower().strip()) 
    | (AppUser.username == user.username.lower().strip()))
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user name or email is already registered."
        )
    hashed_password = password_hasher.hash(user.password)
    db_user = AppUser.model_validate(
        user, 
        update={
            "email": user.email.lower().strip(),
            "username": user.username.lower().strip(),
            "password": hashed_password,
            "disabled": False
        }
    )
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user or email is already registered."
        )
    background_tasks.add_task(
        EmailType.REGISTRATION.send, 
        to_email=db_user.email, 
        name=db_user.username
    )
    
    return db_user