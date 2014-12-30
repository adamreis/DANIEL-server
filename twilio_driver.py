from secrets import TWILIO_SID, TWILIO_AUTH_TOKEN

from twilio.rest import TwilioRestClient

def send_text(msg, to_num):
    client = TwilioRestClient(TWILIO_SID, TWILIO_AUTH_TOKEN)

    message = msg

    message = client.sms.messages.create(   body=message, 
                                            to='+'+to_num, 
                                            from_="+16198412130")
    try:
        print 'message sent: {}'.format(message.sid)
    except TwilioRestException:
        print 'message could not be delivered'

# send_text("hey adam!", "18584058087")