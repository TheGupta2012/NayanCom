from asyncio import subprocess
from .handlers.action import ActionHandler 
from .handlers.data import CVDataHandler, VitalDataHandler 

# # get the actors
from .models.actors import Patient, Caretaker 

# # # get the serial module
# import serial

# cv modules
from scipy.spatial import distance as dist
import dlib
from imutils import face_utils
import cv2 
from imutils.video import VideoStream
import imutils
import os 
import argparse

def get_cv_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--shape-predictor', required=True,
                    help='path to facial landmark predictor')
    ap.add_argument('-v', '--video', type=str, default="",
                    help='path to input video file')
    args = vars(ap.parse_args())
    return args

def eye_aspect_ratio(eye):
    	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)

	# return the eye aspect ratio
	return ear

def get_frame_ear(shape):
    
    # extract the left and right eye coordinates, then use the
    # coordinates to compute the eye aspect ratio for both eyes
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    # average the eye aspect ratio together for both eyes
    ear = (leftEAR + rightEAR) / 2.0

    # compute the convex hull for the left and right eye, then
    # visualize each of the eyes
    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
    cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

    return ear 


# # generate the actors 
patient = Patient()
caretaker = Caretaker()

# # start the data recording 
total_blinks = 0
counter = 0 

right_threshold = 150 
right_limit = 450

frame_count = 0

cv_args = get_cv_args()
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = [20, 45]



detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(cv_args['shape_predictor'])


# data

cv_data_model = CVDataHandler()
vital_data_model = VitalDataHandler()

# action
action_model = ActionHandler(caretaker)


# 1. connect using the bluetooth manager 

# 2. Then, connect the port by the command - 
# rfcomm bind rfcomm0 < MAC addr >

# 3. after that access from python, that's it

# first, it will detect the vitals 
# cv_model_command = ''
# os.system(cv_model_command)
# serialPort = serial.Serial(port = '/dev/rfcomm1', baudrate = 9600, timeout = 2)

vs = VideoStream(src=0).start()
while True:
    # Try to read the data from the serial port
    # try:
    #     # we will send data like 
        
    #     """ "BPM,O2_LEVEL" 
    #     sensor_data = serialPort.readline()
    #     vitals = sensor_data.decode('utf-8').split(",")
        
    #     # Since we will send data in a specific format
    #     # the following code works """
    #     vital_data = {"has_vitals" : True, 
    #                   "heart_rate" : 0, #int(sensor_data[0]),
    #                   "o2_level" : 0 }#int(sensor_data[1])}
    #     vital_data_model.receive_data(patient, data = vital_data)
        
    # except:
    #     patient.vitals_detected = False 
        
    try:
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        if len(rects) == 0:
            # no face 
            patient.in_view = False 
        
        
        # when the allotted time has passed, then only we have to 
        # register those number of blinks 

        # also, we have to update thhe number of blinks to 0 
        # udpate the counter of the time 

	    # loop over the face detections
        for rect in rects:
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = face_utils.shape_to_np(predictor(gray, rect))

            ear = get_frame_ear(shape)

            if ear < EYE_AR_THRESH:
                counter += 1
            else:
                # if the eyes were closed for a sufficient number of
                # then increment the total number of blinks
                if counter >= EYE_AR_CONSEC_FRAMES[0] and counter <= EYE_AR_CONSEC_FRAMES[1]:
                    total_blinks += 1
                    right_threshold = min(right_threshold + 40, right_limit) 
                # reset the eye frame counter
                counter = 0

        if frame_count > right_threshold:

            cv_data = {
                "in_view" : True, 
                "idle": total_blinks > 0, 
                "num_blinks" : total_blinks
            }

            # cv_data = get_cv_data(frame, frame_count, RET_TIME) # TO DO:  recieve data from aryaman's model 

            cv_data_model.receive_data(patient, data = cv_data)

            cv2.putText(frame, "Blinks: {}".format(total_blinks), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "EAR: {:.2f}".format(
                ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # reset the slot of the model detection 

            counter = 0
            frame_count = 0 
            total_blinks = 0 
            right_threshold = 150 

            patient.blink_registered = True 

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
    except:
        patient.in_view = False 
        
    
    # if patient.vitals_detected:
    #     action_model.handle_vitals(patient, vital_data_model)

    if patient.blink_registered :
        action_model.handle_blinks(cv_data_model)
        patient.blink_registered = False 
         
    action_model.update_model_vars(patient)
