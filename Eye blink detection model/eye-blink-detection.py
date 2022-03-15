from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import time
import argparse
import imutils
import cv2
import dlib


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)
    return ear

ap = argparse.ArgumentParser()
ap.add_argument('-p', '--shape-predictor', required=True, help='path to facial landmark predictor')
ap.add_argument('-v', '--video', type=str, default="", help='path to input video file')
args = vars(ap.parse_args())

# def get_args():
#     ap = argparse.ArgumentParser()
#     ap.add_argument('-p', '--shape-predictor', required=True, help='path to facial landmark predictor')
#     ap.add_argument('-v', '--video', type=str, default="", help='path to input video file')
#     args = vars(ap.parse_args())
    
#     return args 

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = [15, 45]

COUNTER = 0
TOTAL = 0

RETURN_THRESH = [150, 360]

print('[INFO] Loading facial landmark predictor...')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args['shape_predictor'])

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

print('[INFO] Starting video stream thread...')
vs = FileVideoStream(args["video"]).start()
fileStream = True
vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
fileStream = False
time.sleep(1.0)
frame_count = 0

RET_TIME = RETURN_THRESH[0]

while True:
    
    if fileStream and not vs.more():
        break

    frame = vs.read()
    frame = imutils.resize(frame, width=100)
    frame_count += 1
    if frame_count >= RET_TIME:
        #IDLE STATE
        #cv2.putText(frame, "FACE NOT DETECTED FOOL", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)

    print(len(rects))
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart: lEnd]
        rightEye = shape[rStart: rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            COUNTER += 1
        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES[0] and COUNTER <= EYE_AR_CONSEC_FRAMES[1]:
                TOTAL += 1
                if (RET_TIME + 30 <=RETURN_THRESH[1]):
                    RET_TIME += 30 
                else:
                    RET_TIME = RETURN_THRESH[1] 
                frame_count = 0

            COUNTER = 0

        cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "FC: {:.2f}".format(frame_count), (150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


cv2.destroyAllWindows()
vs.stop()
