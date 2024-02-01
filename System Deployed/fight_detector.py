import time
from absl import app, flags, logging
from absl.flags import FLAGS
import cv2
import tensorflow as tf
from yolov3_tf2.models import YoloV3
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.utils import draw_outputs
import pyrebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from datetime import date
import random
from pyfcm import FCMNotification
from pprint import pprint
import string

def generate_random_key(docs):
    ctr = 0
    all_docs = docs
    ran_num = random.randint(0,1000)
    for each_doc in docs:
        if not ran_num == each_doc['key']:
            ctr = ctr + 1
    if ctr == len(docs):
        docs.append({'key': ran_num})
    else:
        generate_random_key(all_docs)
    return ran_num


def get_random_string(length):
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


yolo = YoloV3(classes=1)

yolo.load_weights('./weights_fight/yolov3.tf')
print('weights loaded')

class_names = [c.strip() for c in open('./data_fight/labels/coco.names').readlines()]
print('classes loaded')

#send frame to firebase
firebaseConfig = {
    "apiKey": "AIzaSyDhT7d-mf0y_eD27Zc_CS0tULCtvZnZqd0",
    "authDomain": "fyp-firebase-3b063.firebaseapp.com",
    "databaseURL": "https://fyp-firebase-3b063.firebaseio.com",
    "projectId": "fyp-firebase-3b063",
    "storageBucket": "fyp-firebase-3b063.appspot.com",
    "messagingSenderId": "1091972157972",
    "appId": "1:1091972157972:web:b03aee8670af4a51e88d01",
    "measurementId": "G-CBKPD027D7"
}

email = "infusion_turbo360@hotmail.com"

password = "icybeam360"

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(email,password)

#initialize firebase
cred = credentials.Certificate("./fyp-firebase-3b063-firebase-adminsdk-u4bk9-71cd0594fa.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def fight_detector(img,current_state):
    try:
        fps = 0.0
        count = 0

        while True:
            print("In while loop")
            print("Current state: ",current_state)

            if img is None:
                logging.warning("Empty Frame")
                time.sleep(0.1)
                count+=1
                if count < 10:
                    continue
                else: 
                    break

            img_in = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
            img_in = tf.expand_dims(img_in, 0)
            img_in = transform_images(img_in, 416)

            t1 = time.time()
            boxes, scores, classes, nums = yolo.predict(img_in)
            fps  = ( fps + (1./(time.time()-t1)) ) / 2

            img = draw_outputs(img, (boxes, scores, classes, nums), class_names)
            img = cv2.putText(img, "FPS: {:.2f}".format(fps), (0, 30),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)

            cv2.imshow('Fight Detector', img)

            print(classes[0][:2])
            print(scores[0][:2])
            class_present=classes[0][:2]
            class_score=scores[0][:2]


            cv2.imwrite("captured_frame.jpg", img)

            #latest time and date
            now = datetime.now()
            currTime = now.strftime("%H:%M:%S")

            today = date.today()
            currDate = today.strftime("%b-%d-%Y")
            
            path_on_cloud = "images/"+"img"+currDate+currTime+".jpg"
            path_local = "captured_frame.jpg"

            result = storage.child(path_on_cloud).put(path_local)
            url = storage.child(path_on_cloud).get_url(user['idToken'])
            
            docs = []
            collecs = db.collection(u'notification').stream()
            for every_doc in collecs:
                docs.append(every_doc.to_dict())

            #inserting data to firestore
            doc_ref = db.collection('notification').document(get_random_string(10))

            for x in range(len(class_present)):
                print("In loop")
            
                if class_score[x] > 0.6:
                    
                    if class_present[x] == 0 and "fight" not in current_state:
                        print("Fight")
                        current_state=["fight"]
                        msg="Alert! Fight Detected"
                        print(msg)

                        doc_ref.set({
                        'currDate': currDate,
                        'currTime': currTime,
                        'image_url':url,
                        'key':str(generate_random_key(docs)),
                        'title':"Weapon Detected",
                        'message':'This person is not in your recognized registered list.',
                        })  
                        
                        push_service = FCMNotification(api_key="AAAA_j6c0hQ:APA91bGoNVAui9SeOrrr7WUd0zR6UT8a7u2drhNHzYcsFL_qShNJIZK22Jy_jxHIKu5Dr5e7UoY5J3XQt4f_EB2v5uPMlP-B49WkhXjqANOcHQnJTdFPCY75V2P3V2jlK8zYtiRqA07p")
            
                        message = "This person is not in your allowed list."

                        registration_id = "cjrjOH1wQFS9DvfzTDfuYf:APA91bHG3xis5_0GkBzjjqWa86fRPBlOrf0Te9JmJq31MBCS2kXmJ3TOswSRpc4iu5K0iU8ahWdGBWUduzOUe0L3FvsQokqvaT9TKyg86f0i8g2hgjgI7hW7D0mBRuGnhJz7Jh2kXoiI"
                
                        result1 = push_service.single_device_data_message(registration_id=registration_id,data_message={"test": "Spy Eye","message":msg})

                        result = push_service.notify_topic_subscribers(topic_name="global", message_body=message)
                        print("Notification sent")

                if class_present[x] == 0 and class_score[x] == 0:
                    print("Empty state")
                    print(current_state)
                    current_state = []

            return ("Fight detection successful",current_state)

    except Exception as e:
        print("Can not detect current frame: ",str(e))                              