import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.models.order import Order
from app.models.product import Product
from sqlmodel import Session

PAYPAL_SECRET = settings.PAYPAL_SECRET_KEY
PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_API_URL = "https://api-m.sandbox.paypal.com"

async def get_paypal_access_token() -> str:
    url = f"{PAYPAL_API_URL}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), 
            headers=headers, 
            data=data
        )
        
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error al autenticar con PayPal")
        
    return response.json()["access_token"]

def fulfill_order(order_id: int, session: Session) -> bool:
    order = session.get(Order, order_id)
    if not order:
        return False

    if order.status == "PAID":
        return True
    
    for item in order.items:
        product = session.get(Product, item.product_id)
        if not product:
            continue
        if product.stock < item.quantity:
            product.stock = 0
        else:
            product.stock -= item.quantity
            
        session.add(product)
    order.status = "PAID"
    session.add(order)
    session.commit()
    
    return True