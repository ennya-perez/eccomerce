from enum import Enum
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from db import create_db_and_tables, get_session, Session, engine
from sqlalchemy import func
from sqlmodel import select
from models import AppUser, Product, AppUser, UserCreate, UserPublic
from pydantic import EmailStr, BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
import os
import jwt
import resend
from jwt.exceptions import PyJWTError
from pwdlib import PasswordHash
from typing import Annotated

app = FastAPI()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/login")
ACCESS_TOKEN_EXPIRE_MINUTES = 30



class EmailType(Enum):
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    ADD_PRODUCT = "add_product"

    def send(self, to_email: EmailStr, name: str):
        """
        This method receives the dynamic data of the user, builds the 
        corresponding template and triggers the email using Resend.
        """
        if self == EmailType.REGISTRATION:
            subject = f"Hello {name}!"
            html = f"""
            <h3>Welcome {name}!</h3>
            <p>Congrats on successfully <strong>making an account on our store!</strong></p>
            """
        
        elif self == EmailType.PASSWORD_RESET:
            subject = "Recover your password"
            html = f"""
            <h3>Hello {name}</h3>
            <p>We received a request to reset your password. If you didn't make this request, ignore this email.</p>
            """
        elif self == EmailType.ADD_PRODUCT:
            subject = "New product added"
            html = f"""
            <h3>Hello {name}</h3>
            <p>A new product has been added to your store.</p>
            """
        else:
            raise ValueError("Tipo de email no soportado")

        payload = {
            "from": "Ycommerce <onboarding@resend.dev>",
            "to": to_email,
            "subject": subject,
            "html": html
        }
        
        return resend.Emails.send(payload)

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


SessionDep = Annotated[Session, Depends(get_session)]

def verify_password(plain_password, hashed_password):
    return password_hasher.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hasher.hash(password)


def get_user(db: SessionDep, username: str):
    statement = select(AppUser).where(
        func.lower(func.trim(AppUser.username)) == func.lower(func.trim(username))
    )
    user = db.exec(statement).first()
    if not isinstance(user, AppUser):
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
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
 session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root(session: Session = Depends(get_session)):
    return "Hello world"

@app.post("/token/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
session: SessionDep) -> Token:
    print("Inicio este endpoint \n \n \n \n \n \n \n")
    user = authenticate_user(session, form_data.username, form_data.password)
    if user == False:
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[AppUser, Depends(get_current_active_user)],
) -> UserPublic:
    return current_user

@app.post("/sign-up", response_model=UserPublic)
async def sign_up(session: SessionDep, user: UserCreate, background_tasks: BackgroundTasks):
    """
    ## User sign up:
    - username: str
    - email: EmailStr
    - password: str
    - bio: Optional[str]
    - disabled: bool

    
    """
    user.password = password_hasher.hash(user.password)
    db_user = AppUser(
        username=user.username,
        email=user.email,
        password=user.password,
        bio=user.bio,
        disabled=False
    )
    background_tasks.add_task(
        EmailType.REGISTRATION.send, 
        to_email=user.email, 
        name=user.username
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/add-product", response_model=Product)
async def add_product(session: SessionDep, product: Product, background_tasks: BackgroundTasks,
current_user: Annotated[AppUser, Depends(get_current_active_user)]):
    """
    ## Add product:
    This endpoint adds a product to the stock of the eccomerce
    - **name:** str
    - **price:** float
    - **stock:** int
    - **description:** str
    - **category_id:** int
    - **disabled:** bool

    
    """
    db_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
        description=product.description,
        category_id=product.category_id,
        disabled=False
    )

    background_tasks.add_task(
        EmailType.ADD_PRODUCT.send,
        to_email=current_user.email,
        name=current_user.username
    )
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

