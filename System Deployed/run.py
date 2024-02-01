import cv2
from facerec_from_webcam_faster import run
#from object_detector import detector
#from fight_detector import fight_detector

def combine():
     current_face_state = []
     current_object_state = []
     current_activity_state = []
     video_capture = cv2.VideoCapture(0)
     
     while True:
          ret, frame = video_capture.read()

          print("Frame send for Face recognition")
          face_result, face_state = run(frame, current_face_state)
          print("Face_result: ",face_result)
          print("Face state: ",face_state)
          current_face_state = face_state
          print(current_face_state)

          # print("Frame send for object detection")
          # object_result, object_state = detector(frame,current_object_state)
          # print("object_result: ",object_result)
          # print("object state: ",object_state)
          # current_object_state = object_state
          # print(current_object_state)

          # print("Frame send for activity detection")
          # activity_result, activity_state = fight_detector(frame,current_activity_state)
          # print("object_result: ",activity_result)
          # print("object state: ",activity_state)
          # current_object_state = activity_state
          # print(current_activity_state)

     # Hit 'q' on the keyboard to quit!
          if cv2.waitKey(1) & 0xFF == ord('q'):
               break
     
     video_capture.release()
     cv2.destroyAllWindows()

combine()