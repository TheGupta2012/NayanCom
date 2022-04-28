# use the smtp server
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread, Lock


port = 465  # for SSL
SENDER_EMAIL = "harshit.iotdev@gmail.com"
PASSWORD = "iotdevserver"
threadLock = Lock()

"""Threaded"""


def get_email(text, to_email, em_state=False, subject="Patient Update"):

    # Create a multipart message and set headers
    message = MIMEMultipart()
    body = text
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    if em_state:
        message["Subject"] = "EMERGENCY!"

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    to_send = message.as_string()
    return to_send


def send_email(message, em_state, to_email):
    threadLock.acquire()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("harshit.iotdev@gmail.com", PASSWORD)

        sent = False
        while not sent:
            if not em_state:
                server.sendmail(SENDER_EMAIL, to_email, message)
            else:
                for _ in range(3):
                    server.sendmail(SENDER_EMAIL, to_email, message)
            sent = True
        server.quit()

    threadLock.release()


def send_alerts(text, to_email, em_state=False, subject="Patient Update"):
    message = get_email(text, to_email, em_state, subject)
    thread = Thread(target=send_email, args=(message, em_state, to_email))
    thread.start()
    # no need to wait, just execute the thread
