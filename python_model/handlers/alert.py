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

# alert link embed in message 


# can use QuickSend api but not really required I guess. 


# not using twilio as this is paid

# def verify_phone(phone, name):
        
#     # Find your Account SID and Auth Token at twilio.com/console
#     # and set the environment variables. See http://twil.io/secure
#     account_sid = os.environ['TWILIO_ACCOUNT_SID']
#     auth_token = os.environ['TWILIO_AUTH_TOKEN']
#     client = Client(account_sid, auth_token)

#     validation_request = client.validation_requests \
#                             .create(
#                                     friendly_name= name,
#                                     phone_number= "+91" + str(phone)
#                                 )

# def send_message(text, patient_num, em_state = False):
#     # Find your Account SID and Auth Token at twilio.com/console
#     # and set the environment variables. See http://twil.io/secure
#     account_sid = os.environ['TWILIO_ACCOUNT_SID']
#     auth_token = os.environ['TWILIO_AUTH_TOKEN']
#     client = Client(account_sid, auth_token)
#     if not em_state:
#         message = client.messages \
#             .create(
#                 body=text,
#                 from_=,# need to add my number,
#                 to=patient_num
#             )
#     else:
#         for _ in range(3):
#             message = client.messages \
#             .create(
#                 body=text,
#                 from_=, # need to add my number ,
#                 to=patient_num
#             )

