from app import app
from flask import Flask, request, jsonify
from utils import send_text, open_door_async, google_shorten_url, DEFAULT_GALLERY, reset_db
from random import randint
import kairos
import json
import pdb
from time import time
from mongo_setup import USER_COLLECTION, PENDING_COLLECTION
from bson.objectid import ObjectId

# App Logic
@app.route('/', methods=['GET'])
def index():
    return 'yo'

@app.route('/reset', methods=['GET'])
def reset():
    reset_db()
    return 'reset!'

@app.route('/open', methods=['POST'])
def open():
    open_door_async()
    return jsonify({'message': 'Opening door!'})

@app.route('/users', methods=['GET'])
def users():
    users = list(USER_COLLECTION.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify({'users': users})

@app.route('/users/new', methods=['POST'])
def users_new():
    data = json.loads(request.data)
    name = data.get('name')
    img_url = data.get('img_url')
    admin = data.get('admin')
    phone = data.get('phone')
    kairos_id = kairos.add_face_url(img_url, name, DEFAULT_GALLERY)
    if kairos_id:
        user = {
            'name': name,
            'img_url': img_url,
            'admin': admin,
            'phone': phone,
            'kairos_id': kairos_id
        }
        USER_COLLECTION.insert(user)

    return jsonify({'success': kairos_id is not None})

@app.route('/user/<user_id>', methods=['DELETE'])
def user_delete(user_id):
    user = USER_COLLECTION.find_one({'_id': ObjectId(user_id)})
    kairos_id = user.get('kairos_id')

    success = kairos.remove_subject(kairos_id, DEFAULT_GALLERY)

    if success:
        USER_COLLECTION.remove(user)

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
        open_door_async()
        kairos.add_face_url_async(img_url, name, DEFAULT_GALLERY)
    else:
        code = randint(1000, 9999)

        while (PENDING_COLLECTION.find_one({'code': code})):
            code = randint(1000, 9999)

        ding_dong = {'code': code, 'img_url': img_url}
        PENDING_COLLECTION.insert(ding_dong)

        short_url = google_shorten_url(img_url)
        text = "Ding dong! You have a visitor: {}. Reply 'open' to open the door, or '{} <their name>' to save their face and always let them in.".format(short_url, code)
        admins = USER_COLLECTION.find({'admin': True})
        for user in admins:
            num = user.get('phone')
            send_text(text, num)


    print 'status of verification: {}; name: {}'.format(allowed, name)
    return jsonify({'allowed': allowed,
                    'name': name})

@app.route('/twilio-hook/',methods=['POST'])
def handle_text():
    text = request.values.get('Body')
    phone_num = request.values.get('From')[1:]

    print 'new text from {}: {}'.format(phone_num, text)

    admins = USER_COLLECTION.find({'admin': True})
    admin_nums = [admin.get('phone') for admin in admins]

    if phone_num in admin_nums:
        if text.lower() == 'open':
            open_door_async()
            send_text('Door opened!', phone_num)
        else:
            try:
                l = text.split()
                code = l[0]
                name = ' '.join(l[1:])
                code = int(code)

                ding_dong = PENDING_COLLECTION.find_one({'code': code})
                if ding_dong: 
                    # allow entry
                    open_door_async()
                    img_url = ding_dong.get('img_url')
                    
                    PENDING_COLLECTION.remove(ding_dong)
                    kairos_id = kairos.add_face_url(img_url, name, DEFAULT_GALLERY)
                    if kairos_id:
                        # let admins know entry allowed
                        admin_name = USER_COLLECTION.find_one({'admin': True, 'phone': phone_num}).get('name')
                        text = '{} has been granted access by {}'.format(name, admin_name)
                        for num in admin_nums:
                            send_text(text, num)
                        # create new user in db
                        user = {
                            'name': name,
                            'img_url': img_url,
                            'admin': False,
                            'phone': None,
                            'kairos_id': kairos_id
                        }
                        USER_COLLECTION.insert(user)
                        print 'inserted new users: {}'.format(user)

                    else:
                        text = "{}'s picture could not be recognized.  They've been let in, but their picture wasn't saved."
                        send_text(text, phone_num)
                else:
                    send_text('There is no pending request with that ID.', phone_num)

            except Exception, e:
                send_text('invalid response!', phone_num)

    return 'Thanks!', 200

