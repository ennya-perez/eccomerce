from fastapi import FastAPI, Depends
from app.core.db import create_db_and_tables, get_session
from app.core.security import get_current_user
from app.schemas.user_schema import UserPublic
from app.core.config import API_DESCRIPTION
from app.routers import auth, orders, product
from sqlmodel import Session

app = FastAPI(
    title="🚀 My Ecommerce & Automation API",
    description=API_DESCRIPTION,
    version="1.0.0",
    contact={
        "name": "Us7rname",
        "github": "https://github.com/Us7rname",
    }
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root(session: Session = Depends(get_session)):
    return "Hello world"

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        theme="purple",
    )

app.include_router(auth.router)
app.include_router(product.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)