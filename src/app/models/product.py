from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List
from app.schemas.product_schema import ProductCreate


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    slug: str = Field(unique=True)
    description: Optional[str] = None
    products: List["Product"] = Relationship(back_populates="category")

class Product(ProductCreate, table=True):
    product_id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="appuser.id")
    category: Optional[Category] = Relationship(back_populates="products")

