import my_info as me
import smtplib
from email.mime.text import MIMEText

def look_up():
    my_email = me.MY_EMAIL
    recipient = me.RECIPIENT_EMAIL
    app_password = me.APP_PW

    subject = "ISS Tracker"
    body = "The International Space Station is near and it might be a good time to look up!"
    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = my_email
    message["To"] = recipient

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=app_password)
            connection.sendmail(from_addr=my_email, to_addrs=recipient,
                                msg=message.as_string())
            print("Email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print("Authentication failed:", e.smtp_error.decode())
    except Exception as ex:
        print("Something went wrong:", ex)

# look_up()