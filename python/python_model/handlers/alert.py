# use the smtp server 
import smtplib, ssl 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 


port = 465 # for SSL 
SENDER_EMAIL = 'harshit.iotdev@gmail.com'
PASSWORD = 'iotdevserver'

def send_alerts(text, to_email, em_state = False):
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    body = text 
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    
    if not em_state:
        message["Subject"] = "Patient Update"
    else:
        message["Subject"] = "EMERGENCY!"

    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    to_send = message.as_string()
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("harshit.iotdev@gmail.com", PASSWORD)
        
        sent = False 
        while not sent:
            if not em_state:
                server.sendmail(SENDER_EMAIL, to_email, to_send)
            else:
                for _ in range(3):
                    server.sendmail(SENDER_EMAIL, to_email, to_send)
            sent = True 