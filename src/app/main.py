from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import create_db_and_tables, get_session
from app.core.security import get_current_user
from app.core.config import API_DESCRIPTION
from app.routers import auth, orders, product, cart, webhooks
from sqlmodel import Session

app = FastAPI(
    title="🚀 My Marketplace & Automation API",
    description=API_DESCRIPTION,
    version="1.0.0",
    contact={
        "name": "Us7rname",
        "github": "https://github.com/Us7rname",
    }
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(webhooks.router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)