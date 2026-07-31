from fastapi import APIRouter, Request, BackgroundTasks, Depends, HTTPException, status
from sqlmodel import Session
from app.core.db import get_session
from app.models.order import Order
from app.models.user import AppUser
from app.services.payment import fulfill_order
from app.services.email_services import EmailType
from app.services.pdf_generator import generate_order_invoice

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/paypal")
async def webhook_paypal(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    try:
        event = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Procesar solo si es captura completada
    if event.get("event_type") == "PAYMENT.CAPTURE.COMPLETED":
        resource = event.get("resource", {})

        # Extracción segura de IDs sin riesgo de KeyError
        local_order_id = resource.get("custom_id")
        
        if not local_order_id:
            supp_data = resource.get("supplementary_data", {})
            related_ids = supp_data.get("related_ids", {})
            local_order_id = related_ids.get("order_id")

        if not local_order_id:
            print("Webhook recibido sin ID de orden válida.")
            return {"status": "ignored", "reason": "Missing order ID"}

        # Asegurar tipo de dato si tu ID en BD es entero (ej: int(local_order_id))
        order = session.get(Order, local_order_id)
        
        if not order:
            print(f"Orden ID {local_order_id} no encontrada en la BD.")
            return {"status": "error", "message": "Order not found"}

        # Idempotencia: Procesar solo si aún no está pagada
        if order.status != "PAID":
            order.status = "PAID"
            session.add(order)
            fulfill_order(order_id=local_order_id, session=session)
            session.commit()        

            user = session.get(AppUser, order.user_id)
            if user and user.email:
                background_tasks.add_task(
                    EmailType.PAYMENT_SUCCESFUL.send,
                    to_email=user.email,
                    name=user.username
                )
            
            background_tasks.add_task(generate_order_invoice, local_order_id)
            print(f"Confirmed order payment of ID: {local_order_id}!")

    return {"status": "received"}