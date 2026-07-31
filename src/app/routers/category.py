# routers/categories.py
from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session, Category

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[Category])
def get_categories(session: Session = Depends(get_session)):
    """"
    ## Get categories
    Returns all product categories
    """
    return session.exec(select(Category)).all()