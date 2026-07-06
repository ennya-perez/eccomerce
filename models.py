from sqlmodel import SQLModel, Field
from typing import List, Optional
from sqlalchemy import Column, JSON
from pydantic import EmailStr
from enum import Enum
from datetime import datetime, timezone

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    SENT = "sent"
    DELIVERED = "delivered"
    CANCELED = "canceled"


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

class AppUser(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    disabled: bool = Field(default=True)
    password: str

class Product(SQLModel, table=True):
    product_id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str = Field(min_length=30)
    price: int = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: int
    disabled: bool = Field(default=True)
    

class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    total_price: int = Field(gt=0)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    payment_id: str | None = None

class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.product_id")
    quantity: int = Field(gt=0)
    price_at_purchase: int = Field(gt=0)
