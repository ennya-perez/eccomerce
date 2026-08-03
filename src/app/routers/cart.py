from fastapi import APIRouter
from app.models.product import Product
from app.core.db import SessionDep
from app.core.security import get_current_active_user
from sqlmodel import select
from typing import Annotated
from fastapi import Depends, HTTPException
from app.models.user import AppUser
from app.models.cart import CartItem
from app.schemas.cart_schema import CartItemCreate, CartItemUpdate
from app.core.security import get_current_active_user
from typing import Annotated
from fastapi import Depends, HTTPException

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/get-items", response_model=list[CartItem])
async def get_items(session: SessionDep, current_user: Annotated[AppUser, Depends(get_current_active_user)]):
    """
    ## Get items:
    This endpoint gets the items of the cart
    """
    items = session.exec(select(CartItem).where(CartItem.user_id == current_user.id)).all()
    return items

@router.post("/add-item", response_model=CartItem)
async def add_item(session: SessionDep, cart_item_create: CartItemCreate, 
current_user: Annotated[AppUser, Depends(get_current_active_user)]):
    """
    ## Add item:
    This endpoint adds an item to the cart
    - **product_id:** int
    - **quantity:** int

    
    """
    product = session.get(Product, cart_item_create.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    existing_item = session.exec(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == cart_item_create.product_id
        )
    ).first()
    if existing_item:
        existing_item.quantity += cart_item_create.quantity
        session.add(existing_item)
        return existing_item
    db_cart_item = CartItem(
        product_id=cart_item_create.product_id,
        user_id=current_user.id,
        quantity=cart_item_create.quantity,
        total_price=cart_item_create.quantity * product.price
    )
    session.add(db_cart_item)
    session.commit()
    session.refresh(db_cart_item)
    return db_cart_item

@router.patch("/update-item")
async def update_item(session: SessionDep, id_item: int, cart_item_update: CartItemUpdate,
current_user: Annotated[AppUser, Depends(get_current_active_user)]):
    """
    ## Update item:
    This endpoint updates an item in the cart
    - **product_id:** int
    - **quantity:** int
    """
    product = session.get(Product, cart_item_update.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_cart_item = session.get(CartItem, id_item)
    if not db_cart_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_cart_item.user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_cart_item.quantity = cart_item_update.quantity
    db_cart_item.total_price = cart_item_update.quantity * product.price
    session.add(db_cart_item)
    session.commit()
    session.refresh(db_cart_item)
    return db_cart_item

@router.delete("/delete-item")
async def delete_item(session: SessionDep, id_item: int,
current_user: Annotated[AppUser, Depends(get_current_active_user)]):
    """
    ## Delete item:
    This endpoint deletes an item from the cart
    - **id_item:** int
    """
    db_cart_item = session.get(CartItem, id_item)
    if not db_cart_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_cart_item.user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    session.delete(db_cart_item)
    session.commit()
    return {"message": "Item deleted successfully"}

