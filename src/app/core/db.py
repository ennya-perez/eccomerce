from app.core.config import Settings
from sqlmodel import create_engine, Session, SQLModel
from app.models.user import AppUser
from app.models.product import Product
from app.models.cart import CartItem
from app.models.product import Category
from typing import Annotated
from fastapi import Depends
from sqlmodel import select


engine = create_engine(Settings().DATABASE_URL, echo=True, pool_pre_ping=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

DEFAULT_CATEGORIES = [
    {"name": "Electronics", "slug": "electronics", "description": "Gadgets and tech items"},
    {"name": "Clothing", "slug": "clothing", "description": "Apparel and accessories"},
    {"name": "Home & Garden", "slug": "home-garden", "description": "Items for your home"},
    {"name": "Sports", "slug": "sports", "description": "Sports equipment and accessories"},
    {"name": "Books", "slug": "books", "description": "Printed and digital books"},
]

def seed_categories():
    with Session(engine) as session:
        existing = session.exec(select(Category)).first()
        if not existing:
            for cat in DEFAULT_CATEGORIES:
                session.add(Category(**cat))
            session.commit()
            print("Categorías base creadas con éxito.")