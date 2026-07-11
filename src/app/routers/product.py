from fastapi import APIRouter, BackgroundTasks
from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductPaginationResponse
from app.core.db import SessionDep
from app.core.security import get_current_active_user
from app.services.email_services import EmailType
from sqlmodel import select
from sqlalchemy import func
from typing import Annotated
from fastapi import Depends, HTTPException, Query
from app.models.user import AppUser
from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductPaginationResponse, UpdateProduct
from app.core.security import get_current_active_user
from app.services.email_services import EmailType
from typing import Annotated
from fastapi import Depends, HTTPException, Query

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/add-product", response_model=Product)
async def add_product(session: SessionDep, product: ProductCreate, background_tasks: BackgroundTasks,
current_user: Annotated[AppUser, Depends(get_current_active_user)]):
    """
    ## Add product:
    This endpoint adds a product to the stock of the eccomerce
    - **name:** str
    - **price:** float
    - **stock:** int
    - **description:** str
    - **category_id:** int
    - **owner_id:** int
    - **disabled:** bool

    
    """
    db_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
        description=product.description,
        category_id=product.category_id,
        owner_id=current_user.id,
        disabled=product.disabled
    )

    background_tasks.add_task(
        EmailType.ADD_PRODUCT.send,
        to_email=current_user.email,
        name=current_user.username
    )
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@router.get("/products", response_model=ProductPaginationResponse)
async def get_products(
    session: SessionDep,
    offset: int = Query(default=0, ge=0, description="Records to jump"),
    limit: int = Query(default=10, ge=1, le=50, description="Records per page")
):
    """
    ## Obtain product with pagnation metadata
    Returns solicited product portion and total count for frontend's pagination.
    """
    count_statement = select(func.count()).select_from(Product)
    total_products = session.exec(count_statement).one()
    product_statement = select(Product).offset(offset).limit(limit)
    products = session.exec(product_statement).all()
    return {
        "total": total_products,
        "limit": limit,
        "offset": offset,
        "results": products
    }

@router.patch("/update")
def update_product(id_product: int, update_product:
    UpdateProduct, session: SessionDep, current_user: Annotated[AppUser, Depends(get_current_active_user)], 
    background_tasks: BackgroundTasks):
    db_product = session.get(Product, id_product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    if db_product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this product")
    data_product = update_product.model_dump(exclude_unset=True, exclude_none=True)
    db_product.sqlmodel_update(data_product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    background_tasks.add_task(
        EmailType.PRODUCT_UPDATED.send,
        to_email=current_user.email,
        name=current_user.username
    )
    return db_product


@router.delete("/delete-product")
def delete_product(id_product: int, CurrentUserDep: 
    Annotated[SessionDep, Depends(get_current_active_user)], session: SessionDep, background_tasks: BackgroundTasks):
    product = session.get(Product, id_product)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found. This product is not in the database")
    if product.owner_id == CurrentUserDep.id:
        session.delete(product)
        session.commit()
        background_tasks.add_task(
            EmailType.PRODUCT_DELETED.send, 
            to_email=CurrentUserDep.email, 
            name=CurrentUserDep.username
        )
        return {"Message": "Your product has been deleted"}
    else:
        raise HTTPException(status_code=403, detail="You are not the owner of this product")