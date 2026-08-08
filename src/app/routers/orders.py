from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.db import get_session
from app.core.security import get_current_user
from app.services.payment import get_paypal_access_token, PAYPAL_API_URL
from app.models.cart import CartItem
from app.models.order import Order, OrderStatus, Order, OrderItem
from app.models.product import Product
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
    - Makes the order in local DB
    - Makes PayPal payment order
    - Returns the PayPal order ID and local DB ID
    """
    items = session.exec(select(CartItem).where(CartItem.user_id == current_user.id)).all()
    if not items:
        raise HTTPException(status_code=400, detail="The cart is void")
    total_pay = sum(item.total_price for item in items)
    new_order = Order(
        user_id=current_user.id,
        total_price=total_pay,
        status=OrderStatus.PENDING if hasattr(OrderStatus, 'PENDING') else "PENDING"
    )
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    for cart_item in items:
        product = session.get(Product, cart_item.product_id)
        order_item = OrderItem(
        order_id=new_order.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        price_at_purchase=product.price
    )
    session.add(order_item)
    session.commit()
    access_token = await get_paypal_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    formatted_total = f"{total_pay:.2f}"
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": formatted_total
            },
            "custom_id": str(new_order.id)
        }]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PAYPAL_API_URL}/v2/checkout/orders", headers=headers, json=payload)
    if response.status_code != 201:
        print("DETAILED ERROR FROM PAYPAL:", response.status_code, response.json())
        raise HTTPException(status_code=400, detail="Payment could not be made")
    paypal_order = response.json()
    return {
        "order_id": new_order.id,
        "paypal_order_id": paypal_order["id"],
        "message": "Order made correctly"
    }


@router.post("/capture-paypal")
def capture_paypal_payment(
    payload: dict,
    session: Session = Depends(get_session)
):
    """
    ## Captures PayPal payment
    Captures approved order and sends data to the DB
    """
    paypal_order_id = payload.get("paypal_order_id")
    local_order_id = payload.get("local_order_id") or payload.get("order_id")
    if not paypal_order_id or not local_order_id:
        raise HTTPException(status_code=400, detail="Faltan IDs de la orden (paypal_order_id o local_order_id)")
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    secret = os.getenv("PAYPAL_SECRET_KEY")
    auth_response = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        auth=(client_id, secret),
        data={"grant_type": "client_credentials"}
    )
    if auth_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error de autenticación con PayPal")
    access_token = auth_response.json().get("access_token")
    capture_response = requests.post(
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}/capture",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    capture_data = capture_response.json()
    if capture_response.status_code in [200, 201] and capture_data.get("status") == "COMPLETED":
        order = session.get(Order, int(local_order_id))
        if order:
            order.status = OrderStatus.PAID if hasattr(OrderStatus, 'PAID') else "PAID"
            session.add(order)
            cart_items = session.exec(select(CartItem).where(CartItem.user_id == order.user_id)).all()
            for item in cart_items:
                session.delete(item)
            session.commit()
            for item in order.items:
                product = session.get(Product, item.product_id)
                if product:
                    product.stock = max(0, product.stock - item.quantity)
                    session.add(product)
            session.commit()
            return {"status": "success", "message": "Payment completed and order updated"}
    print("ERROR PAYPAL CAPTURE:", capture_data)
    raise HTTPException(status_code=400, detail="PayPal could not complete the capture")


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
    """
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
def get_order_invoice(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    for item in items:
        item.product = session.get(Product, item.product_id)
    order.items = items
    pdf_buffer = generate_order_invoice(order)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=factura-{order_id}.pdf"},
    )