import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

def _require(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

def look_up(
    subject: str = "ISS Tracker",
    body: str = "The International Space Station is near you tonight!"
) -> None:
    my_email = _require("MY_EMAIL")
    recipients_raw = _require("RECIPIENT_EMAIL")
    app_password = _require("APP_PW")

    recipients = [e.strip() for e in recipients_raw.split(",") if e.strip()]

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = my_email
    msg["To"] = ", ".join(recipients)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as conn:
            conn.starttls()
            conn.login(user=my_email, password=app_password)
            conn.sendmail(from_addr=my_email, to_addrs=recipients, msg=msg.as_string())
            print("Email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        detail = e.smtp_error.decode() if isinstance(e.smtp_error, (bytes, bytearray)) else str(e.smtp_error)
        print("Authentication failed:", detail)
    except Exception as ex:
        print("Something went wrong:", ex)

if __name__ == "__main__":
    look_up()