from sqlmodel import SQLModel, Field
from typing import List

class ProductCreate(SQLModel):
    name: str
    description: str = Field(min_length=30)
    price: int
    stock: int
    category_id: int
    disabled: bool = Field(default=True)

class ProductBase(ProductCreate):
    owner_id: int
    product_id: int

class UpdateProduct(SQLModel):
    name: str | None = None
    description: str | None = Field(default=None, min_length=30)
    price: int | None = None
    stock: int | None = None
    category_id: int | None = None
    disabled: bool | None = Field(default=True)

class ProductPaginationResponse(SQLModel):
    total: int
    limit: int
    offset: int
    results: List[ProductBase]