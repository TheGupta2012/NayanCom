# get handlers
from .handlers.action import ActionHandler 
from .handlers.data import CVDataHandler, VitalDataHandler 

# get actors
from .models.actors import Patient, Caretaker 

# for vitals
import serial

# cv modules and data
import dlib
from imutils import face_utils
import cv2 
import imutils
from imutils.video import VideoStream
from .models.open_cv import EYE_AR_CONSEC_FRAMES, EYE_AR_THRESH, TEXT_CONFIG, EarModel, get_cv_args, get_frame_ear


# generate the actors 
patient = Patient()
caretaker = Caretaker()

# define models and args
cv_args = get_cv_args()
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(cv_args['shape_predictor'])

# data
ear_model = EarModel()
cv_data_model = CVDataHandler()
vital_data_model = VitalDataHandler()

# action
action_model = ActionHandler(caretaker)


# 1. connect using the bluetooth manager 

# 2. Then, connect the port by the command - 
# rfcomm bind rfcomm0 < MAC addr >

# 3. after that access from python, that's it

# first, it will detect the vitals 

serialPort = serial.Serial(port = '/dev/rfcomm1', baudrate = 9600, timeout = 2)
vs = VideoStream(src=0).start()

while True:
    # Try to read the data from the serial port
    try:
        # we will send data like 
        
        """ "BPM " """
        while serialPort.in_waiting():
            continue 

        sensor_data = serialPort.readline()
        vitals = sensor_data.decode('utf-8').split(":")
        
        # Since we will send data in a specific format
        # the following code works 
        vital_data = {"has_vitals" : True, 
                      "heart_rate" : int(vitals[-1])}
                      
        vital_data_model.receive_data(patient, data = vital_data)
        
    except:
        patient.vitals_detected = False 
        
    try:
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        ear_model.frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        if len(rects) == 0:
            # no face 
            patient.in_view = False 
        
        # when the allotted time has passed, then only we have to 
        # register those number of blinks 

        # also, we have to update the number of blinks to 0 
        # update the ear_model.counter of the time 

        for rect in rects:
            shape = face_utils.shape_to_np(predictor(gray, rect))

            ear = get_frame_ear(shape)

            if ear < EYE_AR_THRESH:
                ear_model.counter += 1
            else:
                if ear_model.counter >= EYE_AR_CONSEC_FRAMES[0] and ear_model.counter <= EYE_AR_CONSEC_FRAMES[1]:
                    ear_model.total_blinks += 1
                    ear_model.right_threshold = min(ear_model.right_threshold + 25, ear_model.right_limit) 
                
                # reset the eye frame counter
                ear_model.counter = 0
        
        cv2.putText(frame, "Blinks: {}".format(ear_model.total_blinks),TEXT_CONFIG[0],TEXT_CONFIG[1],TEXT_CONFIG[2],TEXT_CONFIG[3],TEXT_CONFIG[4])
        cv2.putText(frame, "EAR: {:.2f}".format(
            ear), (300, 30), TEXT_CONFIG[1],TEXT_CONFIG[2],TEXT_CONFIG[3],TEXT_CONFIG[4])
        cv2.putText(frame, "FC: {}".format(ear_model.frame_count),
                   (150,30), TEXT_CONFIG[1], TEXT_CONFIG[2], TEXT_CONFIG[3], TEXT_CONFIG[4])
        cv2.imshow("Frame", frame)
        
        
        key = cv2.waitKey(1) & 0xFF
        
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
        
        # if we have exhausted the time limit
        if ear_model.frame_count > ear_model.right_threshold:
            
            # TRY TO REGISTER THE NUMBER OF BLINKS
            cv_data = {
                "in_view" : True, 
                "idle": (ear_model.total_blinks == 0), 
                "num_blinks" : ear_model.total_blinks
            }
            cv_data_model.receive_data(patient, data = cv_data)
            
            ear_model.reset_data()
            patient.blink_registered = True 
    
    except:
        patient.in_view = False 
        
    # if patient.vitals_detected:
    #     action_model.handle_vitals(patient, vital_data_model)
    
    if patient.blink_registered:
        action_model.handle_blinks(cv_data_model)
        patient.blink_registered = False 
         
    action_model.update_model_vars(patient)
