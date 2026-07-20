from sqlmodel import SQLModel, Field
from typing import Optional

class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="appuser.id")
    product_id: int = Field(foreign_key="product.product_id")
    quantity: int = Field(default=1)
    total_price: float = Field(default=0.0)