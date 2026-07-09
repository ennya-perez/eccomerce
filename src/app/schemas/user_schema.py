from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from typing import Optional

class UserBase(SQLModel):
    email: EmailStr
    username: str
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