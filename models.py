from sqlmodel import SQLModel
from pydantic import Field
from typing import List, Optional
from sqlalchemy import Column, JSON
from pydantic import EmailStr

class UserBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr
    bio: Optional[str] = None

    
class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UpdateUser(SQLModel):
    id : int | None = None
    email: EmailStr | None = None
    password: str = Field(default=None, min_length=8)
    bio: Optional[str] = None


class UserPublic(UserBase):
    id: int

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    disabled: bool = Field(default=True)
    password: str       