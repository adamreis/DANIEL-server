from secrets import TWILIO_SID, TWILIO_AUTH_TOKEN
import requests
import json
from twilio.rest import TwilioRestClient
import serial
import time
import threading
from mongo_setup import USER_COLLECTION, PENDING_COLLECTION, GALLERY_VERSION
import kairos
import os
import fnmatch

BAUD_RATE = 9600
DEFAULT_GALLERY = 'gallery' + str(GALLERY_VERSION.find_one().get('version'))
SERIAL_CONNECTION = [None]

# db helpers
def reset_db():
    # wipe dbs
    USER_COLLECTION.remove()
    PENDING_COLLECTION.remove()

    # update gallery id
    GALLERY_VERSION.update({}, { '$inc': {'version': 1}})

    global DEFAULT_GALLERY
    version = GALLERY_VERSION.find_one().get('version')
    DEFAULT_GALLERY = 'gallery' + str(version)
    print('version now ' + DEFAULT_GALLERY)

    # add user to new gallery
    name = 'Adam'
    img_url = 'http://files.parsetfss.com/c314ef28-203e-4df7-8043-6898ff73593d/tfss-28df3310-1945-492b-96eb-f39ab493efea-img-31-12-14--11-25-20.png'
    kairos_id = kairos.add_face_url(img_url, name, DEFAULT_GALLERY)
    if kairos_id:
        user = {'name': name,
                'phone': 'XXXXXXXXXXX',
                'admin': True,
                'img_url': img_url,
                'kairos_id': kairos_id}
        USER_COLLECTION.insert(user)
    
    else:
        print('reset_db: could not add default admin to kairos')


# SMS helpers
def send_text(msg, to_num):
    client = TwilioRestClient(TWILIO_SID, TWILIO_AUTH_TOKEN)

    message = client.sms.messages.create(   body=msg, 
                                            to='+'+to_num, 
                                            from_="+16198412130")
    try:
        print('message sent: {}'.format(message.sid))
    except TwilioRestException:
        print('message could not be delivered')

# send_text("someone is waiting: https://www.filepicker.io/api/file/PblYN4wQJ2mc3t1QopwJ text 'open' to open, or 352 to add this user", "18584058087")

def google_shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url'
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    return json.loads(r.text).get('id')

def find(pattern, path):
    """
    From Nadia Alramli's answer: http://stackoverflow.com/questions/1724693/find-a-file-in-python
    """
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def find_serial_interface():
    possibilities = find('tty.usbmodem*', '/dev/')
    if not possibilities:
        raise Exception("Can't find any serial usb modems")
    elif len(possibilities) == 1:
        return possibilities[0]
    else:
        for i, f in enumerate(possibilities):
            print('[{}] {}'.format(i, f))
        idx = int(input('Which file # is correct? '))
        return possibilities[idx]

def connect_to_arduino():
    com_interface = find_serial_interface()
    print("com_interface: {}".format(com_interface))
    try:
        SERIAL_CONNECTION[0] = serial.Serial(com_interface, BAUD_RATE)
    except:
        print("couldn't connect to arduino")
        SERIAL_CONNECTION[0] = None
    time.sleep(2)


# robot parts
def open_door_async():
    thr = threading.Thread(target=open_door, args=(), kwargs={})
    thr.start()

def open_door():
    # open for 5 seconds
    try:
        SERIAL_CONNECTION[0].write('o')
        time.sleep(5)
        SERIAL_CONNECTION[0].write('c')
    except:
        print("attempting to reconnect to arduino")
        connect_to_arduino()
        open_door()