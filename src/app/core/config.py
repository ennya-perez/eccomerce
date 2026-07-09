from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")



API_DESCRIPTION = """
Welcome to the backend of my project. This API handles the product catalogue, 
user's secure authentication and email automatization.

* **Developed by:** Us7rname (Code Craft)
* **Goal:** Efficient and scalable automatizations
"""
tags_metadata = [
    {
        "name": "Authentication",
        "description": "Sign up flows, login and security tokens gestion.",
    },
    {
        "name": "Products",
        "description": "Complete CRUD with filters, search and pagination forthe Home page.",
    },
    {
        "name": "Orders",
        "description": "Shopcart's gestion, order history and payment process.",
    },
    {
        "name": "Webhooks",
        "description": "Endpoints for receiving and processing Stripe webhooks.",
    }
]