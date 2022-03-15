from scipy.spatial import distance as dist
import time
import argparse
import cv2


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)
    return ear

def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--shape-predictor', required=True, help='path to facial landmark predictor')
    ap.add_argument('-v', '--video', type=str, default="", help='path to input video file')
    args = vars(ap.parse_args())
    
    return args 

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = [15, 45]




# print('[INFO] Loading facial landmark predictor...')

print('[INFO] Starting video stream thread...')

vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
time.sleep(1.0)

RETURN_THRESH = {
                    "MIN" : 150,
                    "MAX" : 360
                }

def get_cv_data(frame, frame_count, RET_TIME):
    data = {
        "in_view" : False, 
        "idle" : False, 
        "num_blinks" : 0
    }
    
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = face_detector(gray, 0)
        data['in_view'] = True 
    except:
        # face is not detected here 
        #cv2.putText(frame, "FACE NOT DETECTED FOOL", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return data 
    
    if frame_count >= RET_TIME:
        #IDLE STATE
        data["idle"] = True
    else:            

        for rect in rects:
            shape = predictor(gray, rect)
            shape = imutils.face_utils.shape_to_np(shape)

            leftEye = shape[lStart: lEnd]
            rightEye = shape[rStart: rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            """To enhance"""
            if ear < EYE_AR_THRESH:
                COUNTER += 1
            else:
                if COUNTER >= EYE_AR_CONSEC_FRAMES[0] and COUNTER <= EYE_AR_CONSEC_FRAMES[1]:
                    TOTAL += 1
                    if (RET_TIME + 60 <=RETURN_THRESH.MAX):
                        RET_TIME += 60
                    else:
                        RET_TIME = RETURN_THRESH.MAX 
                    frame_count = 0
            
                COUNTER = 0
            """To enhance"""
        data["num_blinks"] = TOTAL 
        
        # cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # cv2.putText(frame, "FC: {:.2f}".format(frame_count), (150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    return data 


    # cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


cv2.destroyAllWindows()
vs.stop()
