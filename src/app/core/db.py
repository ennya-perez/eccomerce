from app.core.config import Settings
from sqlmodel import create_engine, Session, SQLModel
from typing import Annotated
from fastapi import Depends


engine = create_engine(Settings().DATABASE_URL, echo=True, pool_pre_ping=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]