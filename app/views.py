from app import app
from flask import Flask, request, jsonify
from twilio_driver import send_text
from arduino import open_door
from random import randint
import kairos
import json
import pdb
from time import time

DEFAULT_GALLERY = str(time())

APPROVED_NUMS = {'18584058087':'Adam R'}

PENDING_REQUESTS = {} # {2434 : 'https://asdfsadfasdfasdf'}

# App Logic
@app.route('/', methods=['GET'])
def index():
    return 'yo'

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = json.loads(request.data)
        img_url = data.get('img_url')
        name = data.get('name')
    except Exception, e: # for iOS and postman
        img_url = request.form['img_url']
        name = request.form['name']

    success = kairos.add_face_url(img_url, name, DEFAULT_GALLERY)
    print 'status of upload: {}'.format(success)
    return jsonify({'success': success})

@app.route('/verify', methods=['POST'])
def verify():
    try:
        data = json.loads(request.data)
        img_url = data.get('img_url')
    except Exception, e:
        try: # for postman
            img_url = request.form['img_url']
        except Exception, e: # for iOS
            img_url = json.loads(dict(request.form).keys()[0]).get('img_url')

    name = kairos.identify_face_url(img_url, DEFAULT_GALLERY)
    allowed = name is not None

    if allowed:
        # TODO: open the door.
        open_door()
    else:
        new_id = randint(1000, 9999)
        while (new_id in PENDING_REQUESTS):
            new_id = randint(1000, 9999)

        PENDING_REQUESTS[new_id] = img_url
        text1 = "This person is waiting at your door: {}.".format(img_url)
        text2 = "Reply 'open' \
                to open the door for them, or '{} <their name>' to save \
                their face and always let them in.".format(new_id)
        #TODO: APPROVED_NUMS -> ADMIN_NUMS
        for num in APPROVED_NUMS.iterkeys():
                            send_text(text1, num)
                            send_text(text2, num)


    print 'status of verification: {}; name: {}'.format(allowed, name)
    return jsonify({'allowed': allowed,
                    'name': name})

@app.route('/twilio-hook/',methods=['POST'])
def handle_text():
    text = request.values.get('Body')
    phone_num = request.values.get('From')[1:]

    print 'new text from {}: {}'.format(phone_num, text)

    if phone_num in APPROVED_NUMS:
        if text == 'open':
            open_door()
            send_text('Door opened!', phone_num)
        else:
            try:
                identifier, name = text.split() 
                identifier = int(identifier)

                if identifier in PENDING_REQUESTS:
                    open_door()
                    url = PENDING_REQUESTS[identifier]
                    del PENDING_REQUESTS[identifier]

                    success = kairos.add_face_url(url, name, DEFAULT_GALLERY)
                    if success:
                        text = '{} has been granted access by {}'.format(name, APPROVED_NUMS[phone_num])
                        for num in APPROVED_NUMS.iterkeys():
                            send_text(text, num)
                    else:
                        text = "{}'s picture could not be recognized.  They've been let in, but their picture wasn't saved."
                        send_text(text, phone_num)
                else:
                    send_text('There is no pending request with that ID.', phone_num)

            except Exception, e:
                send_text('invalid response!', phone_num)

    return 'Thanks!', 200
