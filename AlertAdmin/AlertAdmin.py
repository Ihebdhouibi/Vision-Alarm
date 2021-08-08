import os
from twilio.rest import Client
from dotenv import load_dotenv

def send_sms(msg):

    load_dotenv(dotenv_path='twilio.env')
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']

    # create client
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=msg,
        from_='+13155632205',
        to='+21652562136'
    )


# send_sms()