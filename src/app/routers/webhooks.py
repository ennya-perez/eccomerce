from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlmodel import Session
from app.core.db import get_session
from app.models.order import Order
from app.models.user import AppUser
from app.services.payment import fulfill_order
from app.services.email_services import EmailType

router_webhooks = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router_webhooks.post("/paypal")
async def webhook_paypal(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)):
    event = await request.json()

    if event["event_type"] == "PAYMENT.CAPTURE.COMPLETED":
        resource = event["resource"]
        local_order_id = resource.get("custom_id") or resource["supplementary_data"]["related_ids"]["order_id"]
        order = session.get(Order, local_order_id)
        order.status = "PAID"
        session.add(order)
        fulfill_order(order_id=local_order_id, session=session)
        session.commit()
        user = session.get(AppUser, order.user_id)
        background_tasks.add_task(
            EmailType.PAYMENT_SUCCESFUL.send,
            to_email=user.email,
            name=user.username
        )
        # 4. Automation in the background (Background Tasks)
        # background_tasks.add_task(generate_invoice_pdf, local_order_id)

        print(f"Confirmed order payment of ID: {local_order_id}!")

    # PayPal requires you to return a 200 OK to know you received the message
    return {"status": "received"}