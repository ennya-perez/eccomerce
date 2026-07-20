from sqlmodel import SQLModel, Field
from typing import List, Optional

class ProductCreate(SQLModel):
    name: str
    description: str = Field(min_length=30)
    price: int
    stock: int
    category_id: int
    disabled: bool = Field(default=True)
    image_url: Optional[str] = Field(
        default="https://images.unsplash.com/photo-1523275335684-37898b6baf30", 
        description="URL de la imagen del producto"
    )

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
    image_url: Optional[str] = Field(
        default="https://images.unsplash.com/photo-1523275335684-37898b6baf30", 
        description="URL de la imagen del producto"
    )

class ProductPaginationResponse(SQLModel):
    total: int
    limit: int
    offset: int
    results: List[ProductBase]