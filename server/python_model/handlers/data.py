from ..models.mappers import VitalLevels, CV, Vitals

# assuming that the cv model will return the
# number of blinks and whether the face is in view or
# not


class CVDataHandler:
    """Updates the model data with respect
    to the CV model"""

    def __init__(self) -> None:
        self.prev_state = CV.IDLE
        self.curr_state = CV.IDLE
        self.row = None
        self.col = None

    def receive_data(self, patient, data):
        # data is present as :
        # face_in_view : Boolean
        # number of blinks : Int
        # idle : Boolean

        in_view = data["in_view"]
        patient.in_view = in_view

        if patient.in_view:
            # try to do something
            blinks = data["num_blinks"]
            idle = data["idle"]
            patient.requesting = not idle
            self._update_states(self.curr_state, blinks, idle)
        else:
            self.reset_model()

    # based on the CV Blink model on paper

    def _update_states(self, curr_state, blinks, idle):
        # when this is updated, immediately the action handler
        # is called which acts upon this state
        # if idle, every option is reset

        # update the state of the model
        if idle:
            self.col = None
            if curr_state == CV.GOT_COL:
                self.curr_state = CV.CONFIRM_ROW
            elif curr_state == CV.ACTIVATE:
                self.curr_state = CV.IDLE
            elif curr_state != CV.IDLE:
                self.curr_state = CV.ACTIVATE
                self.row = None
            else:
                self.curr_state = CV.IDLE
                self.row = None

        elif blinks >= 5:
            self.curr_state = CV.EM
            self.row = self.col = None

        elif self.curr_state == CV.IDLE:
            if blinks <= 4 and blinks >= 2:
                self.curr_state = CV.ACTIVATE

        elif curr_state == CV.ACTIVATE:
            if blinks <= 3:
                self.curr_state = CV.GOT_ROW
                self.row = blinks
            else:
                # what ?
                # go to activate if the blinks are not constrained
                self.curr_state = CV.ACTIVATE

        elif curr_state == CV.GOT_ROW:
            if blinks >= 1:
                self.curr_state = CV.CONFIRM_ROW

        elif curr_state == CV.CONFIRM_ROW:
            if blinks <= 3:
                self.curr_state = CV.GOT_COL
                self.col = blinks
            else:
                # what ?
                # loop to same with some output
                self.curr_state = CV.CONFIRM_ROW

        elif curr_state == CV.GOT_COL:
            if blinks >= 1:
                self.curr_state = CV.ALERT

        # don't need to handle the last states as the ActionHandler
        # will reset the model

        self.prev_state = curr_state

    # after this, action handler is used
    def reset_model(self):
        """Resets the model after the request has been sent
        to the caretaker / EM services"""
        self.prev_state = CV.IDLE
        self.curr_state = CV.IDLE
        self.row = None
        self.col = None


class VitalDataHandler:
    """Updates the model data with respect to
    the Vital Model"""

    def __init__(self) -> None:
        self.state = Vitals.NORMAL
        self.heart_danger = False
        self.classifier = VitalLevels()

    def receive_data(self, patient, data):
        # data is present as :
        # heart rate : Int

        vitals_detected = data["has_vitals"]
        patient.vitals_detected = vitals_detected

        if vitals_detected:
            heart_rate = data["heart_rate"]
            patient.heart_rate = heart_rate
            self._update_state(heart_rate)

    def _update_state(self, heart_rate):

        heart_status = self.classifier.classify_heart_rate(heart_rate)
        # o2_status = VitalLevels.classify_o2_level(o2_level)

        # if we have idle state
        self.heart_danger = False

        if heart_status == "NORMAL":
            pass
        else:
            if "DANGER" not in heart_status:
                self.state = Vitals.ALERT
            else:
                # danger
                self.state = Vitals.EM
                self.heart_danger = True

    def reset_model(self):
        """Tries to reset the state of the model for the
        receiving of new data"""
        # it will be called when the text field is sent OR
        # the request to EM services is sent OR
        self.state = Vitals.NORMAL
        self.heart_danger = False
