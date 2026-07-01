from sqlmodel import SQLModel
from pydantic import Field
from typing import List, Optional
from sqlalchemy import Column, JSON
from pydantic import EmailStr
from enum import Enum
from datetime import datetime

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

class Product(SQLModel, table=True):
    product_id: int | None = Field(default=None, primary_key=True)
    id: int
    name: str
    description: str = Field(min_length=30)
    price: int = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: int
    disabled: bool = Field(default=True)
    password: str

class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    total_price: int = Field(gt=0)
    status: Enum("pending", "paid", "delivered", "receipt", "canceled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    payment_id: str | None = None

