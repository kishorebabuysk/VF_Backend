import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

def send_otp_email(to_email: str, otp: str):
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Admin Password Reset OTP"

    body = f"""
Hello,

Your OTP is: {otp}
This OTP is valid for 5 minutes.

If you did not request this, please ignore this email.
"""
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    if settings.SMTP_USE_TLS:
        server.starttls()

    server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
