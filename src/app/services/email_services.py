from app.core.config import Settings
from enum import Enum
from pydantic import EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

def send_email(to_email: str, subject: str, html_content: str):
    try:
        sender_email = "aprentyaketi@gmail.com"
        app_password = Settings().GOOGLE_PASSWORD

        msg = MIMEMultipart("alternative")
        msg["From"] = f"Ycommerce <{sender_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))
        with smtplib.SMTP("smtp.gmail.com", 465, timeout=10) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, msg.as_string())
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