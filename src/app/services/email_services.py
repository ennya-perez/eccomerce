from app.core.config import Settings
from enum import Enum
from pydantic import EmailStr
import resend

resend.api_key = Settings().RESEND_API_KEY

class EmailType(Enum):
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    ADD_PRODUCT = "add_product"
    PRODUCT_UPDATED = "update_product"
    PRODUCT_DELETED = "delete_product"
    PAYMENT_SUCCESFUL = "payment_succesful" 

    def send(self, to_email: EmailStr, name: str):
        """
        This method receives the dynamic data of the user, builds the 
        corresponding template and triggers the email using Resend.
        """
        if self == EmailType.REGISTRATION:
            subject = f"Hello {name}!"
            html = f"""
            <h3>Welcome {name}!</h3>
            <p>Congrats on successfully <strong>making an account on our store!</strong></p>
            """
        
        elif self == EmailType.PASSWORD_RESET:
            subject = "Recover your password"
            html = f"""
            <h3>Hello {name}</h3>
            <p>We received a request to reset your password. If you didn't make this request, ignore this email.</p>
            """
        elif self == EmailType.ADD_PRODUCT:
            subject = "New product added"
            html = f"""
            <h3>Hello {name}</h3>
            <p>A new product has been added to your store.</p>
            """
        elif self == EmailType.PRODUCT_UPDATED:
            subject = "Your product has been updated"
            html = f"""
            <h3>Hello, {name}</h3>
            <p>You have successfully a product on your store</p>
            """
        elif self == EmailType.PRODUCT_DELETED:
            subject = "Your product has been deleted"
            html = f"""
            <h3>Hello {name}</h3>
            <p>Your product has been succesfully deleted</p>
            """
        elif self == EmailType.PAYMENT_SUCCESFUL:
            subject = "Payment successful"
            html = f"""
            <h3>Hello {name}</h3>
            <p>Your payment has been succesfully completed</p>
            """
        else:
            raise ValueError("Tipo de email no soportado")

        payload = {
            "from": "Ycommerce <onboarding@resend.dev>",
            "to": to_email,
            "subject": subject,
            "html": html
        }
        
        return resend.Emails.send(payload) 