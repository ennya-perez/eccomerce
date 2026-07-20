from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from typing import Optional

class UserBase(SQLModel):
    email: EmailStr
    username: str
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = Field(
        default="https://images.unsplash.com/photo-1523275335684-37898b6baf30", 
        description="URL de la imagen del producto"
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UpdateUser(SQLModel):
    id : int | None = None
    email: EmailStr | None = None
    password: str = Field(default=None, min_length=8)
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserPublic(UserBase):
    id: int