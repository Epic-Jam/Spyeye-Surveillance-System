from PIL import Image
import face_recognition
import cv2
import pickle

def croper(img,name):   
    try:
        # Load the jpg file into a numpy array
        image = face_recognition.load_image_file(img)

        face_locations = face_recognition.face_locations(image)

        if len(face_locations) >= 2:
            #return only one face can register at once on application.
            print("Only one person can register at once")

        if len(face_locations) == 0:
            #return only no face found on application.
            print("Face Not found")
       
        for face_location in face_locations:

            # Print the location of each face in this image
            top, right, bottom, left = face_location
            print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

            # You can access the actual face itself like this:
            face_image = image[top:bottom, left:right]
            pil_image = Image.fromarray(face_image)

            pil_image.save('crop_images\\'+name+'.jpg')

            user_names = pickle.load(open("User_names.p","rb"))
            print("Existing user:",user_names)
            user_names.append(name)
            print("New users: ",user_names)
            pickle.dump(user_names, open("User_names.p", "wb"))
            print("Dumped")

            #return successfully register on app
            return "Successful"

    except Exception as e:
        print("Unable to register new user: ",str(e))        

