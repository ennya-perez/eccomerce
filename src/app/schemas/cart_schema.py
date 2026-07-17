from pydantic import BaseModel

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int 
    price: float
    quantity: int

class CartItemUpdate(BaseModel):
    quantity: int | None = None
    product_id: int | None = None