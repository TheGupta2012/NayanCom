# get handlers
from .handlers.action import ActionHandler, blink_detect
from .handlers.data import CVDataHandler

# get actors
from .models.actors import Patient, Caretaker


# cv modules and data
import dlib
from imutils import face_utils
import cv2
import imutils
from imutils.video import VideoStream
from .models.open_cv import (
    EYE_AR_CONSEC_FRAMES,
    EYE_AR_THRESH,
    TEXT_CONFIG,
    EarModel,
    get_cv_args,
    get_frame_ear,
)

# os
import os
import time
import json

# save the pid for killing
pid = {"id": os.getpid()}

with open(
    r"data/pid_cv.json",
    "w",
) as f:
    json.dump(pid, f)

f.close()

caretaker = Caretaker()

# define models and args
cv_args = get_cv_args()
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(cv_args["shape_predictor"])

# cv data
ear_model = EarModel()
cv_data_model = CVDataHandler()


# action
action_model = ActionHandler(caretaker)

Patient.in_view = False
action_model.update_model_vars(Patient, vitals=False, blinks=False)


# cv model initial
# vs = VideoStream(src=1).start()
# vs = VideoStream(src=0).start()
vs = VideoStream(src=2).start()
# vs.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
# vs.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# vs.start()
while True:

    try:
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        ear_model.frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        # this is to be updated as right now
        # we are only having the in_view
        # property for the last frame before the right
        # threshold
        if len(rects) > 0:
            # no face
            ear_model.views += 1

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
                if (
                    ear_model.counter >= EYE_AR_CONSEC_FRAMES[0]
                    and ear_model.counter <= EYE_AR_CONSEC_FRAMES[1]
                ):
                    ear_model.total_blinks += 1
                    # play a small sound
                    blink_detect()
                    ear_model.right_threshold = min(
                        ear_model.right_threshold + 25, ear_model.right_limit
                    )
                # reset the eye frame counter
                ear_model.counter = 0

        cv2.putText(
            frame,
            "Blinks: {}".format(ear_model.total_blinks),
            TEXT_CONFIG[0],
            TEXT_CONFIG[1],
            TEXT_CONFIG[2],
            TEXT_CONFIG[3],
            TEXT_CONFIG[4],
        )

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
        # if we have exhausted the time limit
        if ear_model.frame_count > ear_model.right_threshold:
            # more than 50% of the times we are in view
            if ear_model.views >= int(0.5 * ear_model.right_threshold):
                Patient.in_view = True
            else:
                Patient.in_view = False

            # TRY TO REGISTER THE NUMBER OF BLINKS
            cv_data = {
                "in_view": Patient.in_view,
                "idle": (ear_model.total_blinks == 0),
                "num_blinks": ear_model.total_blinks,
            }
            cv_data_model.receive_data(Patient, data=cv_data)

            ear_model.reset_data()
            Patient.blink_registered = True

    except:
        Patient.in_view = False
        time.sleep(10)

    if Patient.blink_registered:
        action_model.handle_blinks(Patient, ear_model.previous_view, cv_data_model)
        Patient.blink_registered = False
        ear_model.previous_view = Patient.in_view
        action_model.update_model_vars(Patient, vitals=False, blinks=True)
