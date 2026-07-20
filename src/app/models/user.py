from sqlmodel import Field
from app.schemas.user_schema import UserBase

class AppUser(UserBase, table=True, unique=True):
    id: int | None = Field(default=None, primary_key=True)
    disabled: bool = Field(default=True)
    password: str