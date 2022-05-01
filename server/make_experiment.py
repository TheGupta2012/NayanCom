import os

# get actors
from python_model.models.actors import Patient
from copy import copy

# cv modules and data
import dlib
from imutils import face_utils
import cv2
import imutils
from imutils.video import VideoStream

from python_model.models.open_cv import (
    EYE_AR_CONSEC_FRAMES,
    EYE_AR_THRESH,
    TEXT_CONFIG,
    EarModel,
    get_cv_args,
    get_frame_ear,
)

# define models and args
cv_args = get_cv_args()
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(cv_args["shape_predictor"])

# cv data
ear_model = EarModel()

REQUEST_MAP = {
    1: {1: "water", 2: "food", 3: "wash_room"},
    2: {1: "bodyache", 2: "cold_and_cough", 3: "head_ache"},
    3: {1: "lights", 2: "fan", 3: "chest_pain"},
}

for i in range(1, 4):
    for j in range(1, 4):
        os.makedirs("test/" + REQUEST_MAP[i][j], exist_ok=True)

print("Options are : \n")
for k, v in REQUEST_MAP.items():
    print(k, v)

print()

# enter the details for the experiment
row = int(input("Enter the row id :"))
col = int(input("Enter the col id :"))

path = "test/" + REQUEST_MAP[row][col]
os.makedirs(path, exist_ok=True)
start = input("Start experiment : (Y/N)")


if start == "Y":
    print("Starting script...")

    # save the experiment here
    exp_path = path + "/" + str(len(os.listdir(path))) + ".avi"
    print("Path for experiment is :", exp_path)
    # Create an object to read camera video
    # cap = cv2.VideoCapture(0)
    vs = VideoStream(src=0).start()

    steps = 0

    # Set resolutions of frame.
    # convert from float to integer.
    # frame_width = int(cap.get(3))
    # frame_height = int(cap.get(4))

    # Create VideoWriter object.
    # and store the output in 'captured_video.avi' file.
    video_cod = cv2.VideoWriter_fourcc(*"XVID")
    video_output = cv2.VideoWriter(exp_path, video_cod, 20.0, (640, 480))

    while True:
        frame = vs.read()
        frame2 = copy(frame)
        video_output.write(frame2)

        # process it
        frame = imutils.resize(frame, width=450)
        ear_model.frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)
        for rect in rects:
            shape = face_utils.shape_to_np(predictor(gray, rect))

            ear = get_frame_ear(shape)
            if ear < EYE_AR_THRESH:
                ear_model.counter += 1
            else:
                if (
                    ear_model.counter >= EYE_AR_CONSEC_FRAMES[0]
                    and ear_model.counter <= EYE_AR_CONSEC_FRAMES[1]
                ):
                    ear_model.total_blinks += 1
                    ear_model.right_threshold = min(
                        ear_model.right_threshold + 25, ear_model.right_limit
                    )
                # reset the eye frame counter
                ear_model.counter = 0
        framet = copy(frame)
        cv2.putText(
            framet,
            "Frame Count: {}".format(ear_model.frame_count),
            TEXT_CONFIG[0],
            TEXT_CONFIG[1],
            TEXT_CONFIG[2],
            TEXT_CONFIG[3],
            TEXT_CONFIG[4],
        )
        cv2.imshow("Frame count", framet)
        del framet
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # if we have exhausted the time limit
        if ear_model.frame_count > ear_model.right_threshold:
            print("Blinks : ", ear_model.total_blinks)
            ear_model.reset_data()
            steps += 1
            print("Steps : ", steps)

        if Patient.blink_registered:
            Patient.blink_registered = False
            ear_model.previous_view = Patient.in_view

    video_output.release()

    # Closes all the frames
    cv2.destroyAllWindows()
    final = input("If desired video enter Y : ")

    if final != "Y":
        os.remove(exp_path)
        print("Okay, restart script then")
    else:
        print(f"The video was successfully saved at {exp_path}")

else:
    print("Okay, finishing up")
