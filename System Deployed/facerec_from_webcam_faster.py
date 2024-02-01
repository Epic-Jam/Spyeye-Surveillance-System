import face_recognition
import cv2
import numpy as np
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
import pickle
from spoofing_detection import Prediction


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

path = 'crop_images\\'

#video_capture = cv2.VideoCapture(0)
user = pickle.load(open("User_names.p","rb"))
print("Registered user:",user)
known_face_encodings=[]
for each_user in user:
    new_image = face_recognition.load_image_file(path + each_user +".jpg")
    print(path+each_user+".jpg")
    new_face_encoding = face_recognition.face_encodings(new_image)[0]
    known_face_encodings.append(new_face_encoding)

known_face_names = user
print("Known Face Encoding",known_face_encodings)
print("Known Face Names",known_face_names)

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
path_on_cloud = "images/frame_on_cloud.jpg"


# initialize firebase
cred = credentials.Certificate("./fyp-firebase-3b063-firebase-adminsdk-u4bk9-71cd0594fa.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def run(frame, current_name): 
    try:      
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True


        spoof = "real"
        while True:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                #latest time and date
                now = datetime.now()
                currTime = now.strftime("%H:%M:%S")

                today = date.today()
                currDate = today.strftime("%b-%d-%Y")

                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    spoof = Prediction(frame)
                    print("Spoofing",spoof)
                    if spoof == "fake" and "fake" not in current_name:
                        print("Emergency Alert!")
                        
                        #send notification
                        msg="Alert! Someone trying fake identity."
                        print(msg)
                        docs = []
                        collecs = db.collection(u'notification').stream()
                        for every_doc in collecs:
                            docs.append(every_doc.to_dict())


                        # inserting data to firestore
                        doc_ref = db.collection('notification').document(get_random_string(10))
                        doc_ref.set({
                        'currDate': currDate,
                        'currTime': currTime,
                        'image_url':"fake",
                        'key':str(generate_random_key(docs)),
                        'title':"Alert! Someone trying fake identity.",
                        'message':'This person is not in your recognized registered list.',
                        })  
                        
                        
                        push_service = FCMNotification(api_key="AAAA_j6c0hQ:APA91bGoNVAui9SeOrrr7WUd0zR6UT8a7u2drhNHzYcsFL_qShNJIZK22Jy_jxHIKu5Dr5e7UoY5J3XQt4f_EB2v5uPMlP-B49WkhXjqANOcHQnJTdFPCY75V2P3V2jlK8zYtiRqA07p")
            
                        message = "This person is not in your allowed list."

                        registration_id = "cjrjOH1wQFS9DvfzTDfuYf:APA91bHG3xis5_0GkBzjjqWa86fRPBlOrf0Te9JmJq31MBCS2kXmJ3TOswSRpc4iu5K0iU8ahWdGBWUduzOUe0L3FvsQokqvaT9TKyg86f0i8g2hgjgI7hW7D0mBRuGnhJz7Jh2kXoiI"
                
                        result1 = push_service.single_device_data_message(registration_id=registration_id,data_message={"test": "Spy Eye","message":msg})

                        result = push_service.notify_topic_subscribers(topic_name="global", message_body=message)
                       
                        current_name = ["fake"]
                        print("Notification sent")
                        
                    
                    else:
                        print("Real")
                        
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"

                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                        face_names.append(name)

            process_this_frame = not process_this_frame

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Face Detector and Recognizer', frame)
            #print(face_names)
            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            cv2.imwrite("captured_frame.jpg", frame)

        
            
            path_on_cloud = "images/"+"img"+currDate+currTime+".jpg"
            path_local = "captured_frame.jpg"

            result = storage.child(path_on_cloud).put(path_local)
            url = storage.child(path_on_cloud).get_url(user['idToken'])
            
            
            #fetching docs storing in a variable
            docs = []
            collecs = db.collection(u'notification').stream()
            for every_doc in collecs:
                docs.append(every_doc.to_dict())


            #inserting data to firestore
            doc_ref = db.collection('notification').document(get_random_string(10))
            
            if spoof == 'real':

                for x in range(len(face_names)):

                    if face_names[x] == "Unknown":

                        if face_names[x] not in current_name:
                        
                            print("var="+str(current_name))
                            
                            msg="Alert! Unauthorized Person Detected."
                            
                            doc_ref.set({
                            'currDate': currDate,
                            'currTime': currTime,
                            'image_url':url,
                            'key':str(generate_random_key(docs)),
                            'title':"Unauthorized person",
                            'message':'This person is not in your recognized registered list.',
                            })  
                            current_name = face_names[x]
                            print("Now ",str(current_name))
                            print('unknown here')
                            print("Notification sent")
                            push_service = FCMNotification(api_key="AAAA_j6c0hQ:APA91bGoNVAui9SeOrrr7WUd0zR6UT8a7u2drhNHzYcsFL_qShNJIZK22Jy_jxHIKu5Dr5e7UoY5J3XQt4f_EB2v5uPMlP-B49WkhXjqANOcHQnJTdFPCY75V2P3V2jlK8zYtiRqA07p")
                
                            message = "This person is not in your allowed list."

                            registration_id = "cjrjOH1wQFS9DvfzTDfuYf:APA91bHG3xis5_0GkBzjjqWa86fRPBlOrf0Te9JmJq31MBCS2kXmJ3TOswSRpc4iu5K0iU8ahWdGBWUduzOUe0L3FvsQokqvaT9TKyg86f0i8g2hgjgI7hW7D0mBRuGnhJz7Jh2kXoiI"
                    
                            result1 = push_service.single_device_data_message(registration_id=registration_id,data_message={"test": "Spy Eye","message":msg})

                            result = push_service.notify_topic_subscribers(topic_name="global", message_body=message)
                            print("notification sent")
                        
                            
                    else:
                        if face_names[x] not in current_name:   
                            print("in else") 
                            msg='Authorized Person Detected.'
                            print("var="+str(current_name))
                            print(face_names[x])

                            doc_ref.set({
                                'currDate': currDate,
                                'currTime': currTime,
                                'image_url':url,
                                'key':str(generate_random_key(docs)),
                                'title':"Authorized Person",
                                'message':'This person is not in your recognized registered list.',
                            })
                            current_name = face_names[x]  
                            print("Now: "+str(current_name))
                            push_service = FCMNotification(api_key="AAAA_j6c0hQ:APA91bGoNVAui9SeOrrr7WUd0zR6UT8a7u2drhNHzYcsFL_qShNJIZK22Jy_jxHIKu5Dr5e7UoY5J3XQt4f_EB2v5uPMlP-B49WkhXjqANOcHQnJTdFPCY75V2P3V2jlK8zYtiRqA07p")
                
                            message = "This person is not in your allowed list."

                            registration_id = "cjrjOH1wQFS9DvfzTDfuYf:APA91bHG3xis5_0GkBzjjqWa86fRPBlOrf0Te9JmJq31MBCS2kXmJ3TOswSRpc4iu5K0iU8ahWdGBWUduzOUe0L3FvsQokqvaT9TKyg86f0i8g2hgjgI7hW7D0mBRuGnhJz7Jh2kXoiI"
                    
                            result1 = push_service.single_device_data_message(registration_id=registration_id,data_message={"test": "Spy Eye","message":msg})

                            result = push_service.notify_topic_subscribers(topic_name="global", message_body=message)
                           
                            print("Notification sent")
               
                current_name = face_names        
            return ("Face detection Successful",current_name)

    except Exception as e:
        print("Cannot detect current frame: ",str(e))