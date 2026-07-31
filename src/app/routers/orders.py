from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from app.core.db import get_session
from app.core.security import get_current_user
from app.services.payment import get_paypal_access_token, PAYPAL_API_URL
from app.models.cart import CartItem
from app.models.order import Order, OrderStatus
from app.services.pdf_generator import generate_order_invoice
import httpx
import os
import requests

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/checkout")
async def checkout_con_paypal(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    ## Checkout with PayPal
        - Creates an order in the database
        - Creates a payment in PayPal
        - Returns the PayPal approval URL
    """
    items = session.exec(select(CartItem).where(CartItem.user_id == current_user.id)).all()
    if not items:
        return {"message": "The cart is empty", "items": []}
    if not all(isinstance(item, CartItem) for item in items):
        raise ValueError("The elements retrieved are not of type CartItem")
    total_pay = sum(item.total_price for item in items)
    new_order = Order(
        user_id=current_user.id,
        total_price=total_pay,
    )
    session.add(new_order)
    session.commit()
    access_token = await get_paypal_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": total_pay
            },
            "custom_id": f"{str(new_order.id)}"
        }],
        "application_context": {
            "return_url": "http://localhost:8000/orders/success",
            "cancel_url": "http://localhost:8000/orders/canceled"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PAYPAL_API_URL}/v2/checkout/orders", headers=headers, json=payload)
    
    if response.status_code != 201:
        print(" DETAILED ERROR FROM PAYPAL:", response.status_code, response.json())
        raise HTTPException(status_code=400, detail="Could not create payment in PayPal")
        
    paypal_order = response.json()
    print(paypal_order)
    approve_url = next(link["href"] for link in paypal_order["links"] if link["rel"] == "approve")
    
    return {
        "id": paypal_order["id"],
        "message": f"Order made successfully with ID: {new_order.id}",
        "paypal_url": approve_url
    }

@router.post("/{order_id}/capture")
def capture_order(order_id: str):
    """
    ## Capture order
    - Captures the order in PayPal
    - Updates the order status
    """
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    secret = os.getenv("PAYPAL_SECRET_KEY")
    auth_resp = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        auth=(client_id, secret),
        data={"grant_type": "client_credentials"}
    ).json()
    access_token = auth_resp.get("access_token")
    capture_resp = requests.post(
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    ).json()
    
    return capture_resp

@router.get("/history")
async def get_order_history(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    ## Get order history
    Returns user's order history
    """
    orders = session.exec(select(Order).where(Order.user_id == current_user.id)).all()
    return orders

@router.get("/details")
async def get_order_details(
    order_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """"
    ## Get order details
    Returns order details
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return order

@router.get("/{order_id}/invoice")
async def download_invoice(
    order_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """"
    ## Get order invoice
    Returns order invoice pdf
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You have no permission to see this")
        
    if order.status != OrderStatus.PAID:
        print(order.status)
        raise HTTPException(status_code=400, detail="Order has not been paid")
        
    pdf_buffer = generate_order_invoice(order)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=factura_orden_{order_id}.pdf"
        }
    )