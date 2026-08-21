from app.core.config import Settings
from enum import Enum
from pydantic import EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import requests

BREVO_API_KEY = Settings().BREVO_API_KEY

def send_email(to_email: str, subject: str, html_content: str):
    try:
        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json",
        }

        payload = {
            "sender": {
                "name": "Yccomerce",
                "email": "aprentyaketi@gmail.com",
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content,
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [200, 201]:
            print("Correo enviado con éxito por Brevo")
        else:
            print(f"Error enviando correo: {response.text}")
    except Exception as e:
        logging.error(f"[Email Error] Could not send email to {to_email}: {e}")
        return False

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
        
        return send_email(to_email, subject, html) 