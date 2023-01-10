import math
import argparse
from imutils import face_utils
import cv2

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

EYE_AR_THRESH = 0.05
EYE_AR_CONSEC_FRAMES = [18, 40]

# for drawing
TEXT_CONFIG_1 = [(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2]
TEXT_CONFIG_2 = [(100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2]
# define data for the running of model
class EarModel:
    def __init__(self) -> None:
        self.total_blinks = 0
        self.counter = 0
        self.views = 0
        self.right_threshold = 150
        self.right_limit = 360
        self.frame_count = 0
        self.previous_view = False

    def reset_data(self):
        self.counter = 0
        self.views = 0
        self.frame_count = 0
        self.total_blinks = 0
        self.right_threshold = 150


# utilities
def euclidean(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]

    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = euclidean(eye[1], eye[5])
    B = euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear


def get_cv_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-p",
        "--shape-predictor",
        required=True,
        help="path to facial landmark predictor",
    )
    ap.add_argument(
        "-v", "--video", type=str, default="", help="path to input video file"
    )
    args = vars(ap.parse_args())
    return args


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

    # leftEyeHull = cv2.convexHull(leftEye)
    # rightEyeHull = cv2.convexHull(rightEye)
    # cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
    # cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

    return ear
