from app import app
from flask import Flask, request, jsonify
from twilio_driver import send_text
import kairos
import json
import pdb

DEFAULT_GALLERY = 'test1'

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
    except Exception, e: # for testing with postman
        img_url = request.form['img_url']
        name = request.form['name']


    success = kairos.add_face_url(img_url, name, DEFAULT_GALLERY)
    print 'status of upload: {}'.format(success)
    return jsonify({'success': success})

@app.route('/verify', methods=['GET'])
def verify():
    img_url = request.args.get('img_url')

    name = kairos.identify_face_url(img_url, DEFAULT_GALLERY)
    allowed = name is not None
    # TODO: open the door.

    print 'status of verification: {}'.format(allowed)
    return jsonify({'allowed': allowed,
                    'name': name})

@app.route('/twilio-hook/',methods=['POST'])
def handle_text():
    text = request.values.get('Body')
    phone_num = request.values.get('From')[1:]

    print 'new text from {}: {}'.format(phone_num, text)
    return 'Thanks!', 200
