from secrets import TWILIO_SID, TWILIO_AUTH_TOKEN
import requests
import json
from twilio.rest import TwilioRestClient

def send_text(msg, to_num):
    client = TwilioRestClient(TWILIO_SID, TWILIO_AUTH_TOKEN)

    message = client.sms.messages.create(   body=msg, 
                                            to='+'+to_num, 
                                            from_="+16198412130")
    try:
        print 'message sent: {}'.format(message.sid)
    except TwilioRestException:
        print 'message could not be delivered'

# send_text("someone is waiting: https://www.filepicker.io/api/file/PblYN4wQJ2mc3t1QopwJ text 'open' to open, or 352 to add this user", "18584058087")

def open_door():
    # open for 5 seconds
    print 'DOOR OPENED!'
    pass

def google_shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url'
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    return json.loads(r.text).get('id')