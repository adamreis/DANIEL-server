from secrets import KAIROS_APP_ID, KAIROS_APP_KEY

import requests
import json
import base64

def base64_img(fp):
    with open(fp, "rb") as image_file:
        return base64.b64encode(image_file.read())

def kairos_post(endpoint, data):
    headers = { "content-type" : "application/json",
                "app_id" : KAIROS_APP_ID,
                "app_key" : KAIROS_APP_KEY}

    r = requests.post("http://api.kairos.com/" + endpoint, data=json.dumps(data), headers=headers)
    return r

def add_face_file(base64_img, name, gallery):
    """ returns True on success, False on failure """
    data = {"image" : base64_img,
            "subject_id" : name,
            "gallery_name" : gallery}

    r = kairos_post("enroll", data).json()

    # returns true if this succeeds
    return 'Errors' not in r

def add_face_url(img_url, name, gallery):
    """ returns True on success, False on failure """
    data = {"url" : img_url,
            "subject_id" : name,
            "gallery_name" : gallery}

    r = kairos_post("enroll", data).json()

    # returns true if this succeeds
    return 'Errors' not in r

def check_face_file(base64_img, gallery):
    """ returns name of person (string) on success,
        None on failure """
    data = {"image" : base64_img,
            "threshold" : 0.7,
            "gallery_name" : gallery}

    r = kairos_post("recognize", data).json()

    if r.get('images')[0].get('transaction').get('status') != 'success':
        return None
    else:
        return r.get('images')[0].get('transaction').get('subject')

def check_face_url(img_url, gallery):
    """ returns name of person (string) on success,
        None on failure """

    data = {"url" : img_url,
            "threshold" : 0.7,
            "gallery_name" : gallery}

    r = kairos_post("recognize", data).json()

    if r.get('images')[0].get('transaction').get('status') != 'success':
        return None
    else:
        return r.get('images')[0].get('transaction').get('subject')

# test enroll
# r = add_face_file(base64_img('test_pix/daniel6.jpg'), 'danielm', 'test')

# test recognize
# r = check_face_file(base64_img('test_pix/adam3.jpg'), 'test')
