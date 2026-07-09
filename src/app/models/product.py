from sqlmodel import SQLModel, Field
from typing import Optional, List
from app.schemas.product_schema import ProductCreate


class Product(ProductCreate, table=True):
    product_id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="appuser.id")

