from app import app
from flask import Flask, request, jsonify
import kairos

DEFAULT_GALLERY = 'default_gallery'

# App Logic
@app.route('/', methods=['GET'])
def index():
    return 'yo'

@app.route('/upload', methods=['POST'])
def upload():
    img_url = request.data['img_url']
    name = request.data['name']

    success = kairos.add_face_url(img_url, name, DEFAULT_GALLERY)
    return jsonify({'success': success})

@app.route('/verify', methods=['GET'])
def verify():
    img_url = request.args.get('img_url')

    name = kairos.identify_face_url(img_url, DEFAULT_GALLERY)
    allowed = name is not None
    # TODO: open the door.
    return jsonify({'allowed': allowed,
                    'name': name})
