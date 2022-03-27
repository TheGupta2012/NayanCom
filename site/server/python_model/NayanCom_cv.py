# get handlers
from .handlers.action import ActionHandler
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

# for vitals

# cv model initial
vs = VideoStream(src=0).start()
while True:

    try:
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        ear_model.frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        if len(rects) == 0:
            # no face
            Patient.in_view = False

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
        # cv2.putText(frame, "EAR: {:.2f}".format(
        #     ear), (300, 30), TEXT_CONFIG[1],TEXT_CONFIG[2],TEXT_CONFIG[3],TEXT_CONFIG[4])
        # cv2.putText(frame, "FC: {}".format(ear_model.frame_count),
        #            (150,30), TEXT_CONFIG[1], TEXT_CONFIG[2], TEXT_CONFIG[3], TEXT_CONFIG[4])

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # if we have exhausted the time limit
        if ear_model.frame_count > ear_model.right_threshold:

            # TRY TO REGISTER THE NUMBER OF BLINKS
            cv_data = {
                "in_view": True,
                "idle": (ear_model.total_blinks == 0),
                "num_blinks": ear_model.total_blinks,
            }
            cv_data_model.receive_data(Patient, data=cv_data)

            ear_model.reset_data()
            Patient.blink_registered = True

    except:
        Patient.in_view = False

    # if Patient.vitals_registered:
    #     action_model.handle_vitals(Patient, vital_data_model, update_vitals)
    #     Patient.vitals_registered = False

    if Patient.blink_registered:
        action_model.handle_blinks(cv_data_model)
        Patient.blink_registered = False

    action_model.update_model_vars(Patient)
