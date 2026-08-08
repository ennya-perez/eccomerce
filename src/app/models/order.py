from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="appuser.id")
    total_price: int = Field(gt=0)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payment_id: str | None = None
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.product_id")
    quantity: int = Field(gt=0)
    price_at_purchase: int = Field(gt=0)
    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional[Product] = Relationship()