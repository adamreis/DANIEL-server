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
    # test enroll
    data = {"image" : base64_img,
            "subject_id" : "daniel m",
            "gallery_name" : "test"}

    r = kairos_post("enroll", data)

    # returns true if this succeeds
    return 'Errors' not in r.json()

def add_face_url(img_url, name, gallery):
    return True

def check_face_file(base64_img, gallery):
    return True

def check_face_url(img_url, gallery):
    return True

# # test enroll

r = add_face_file(base64_img('test_pix/daniel6.jpg'), 'danielm', 'test')
import pdb; pdb.set_trace() 

# # test recognize 75%
# data = {"image" : base64_img('test_pix/daniel6.jpg'),
#         "threshold" : 0.5,
#         "gallery_name" : "test"}

# r = kairos_post("recognize", data)
# print r.json()

print base64_img('test_pix/daniel6.jpg')