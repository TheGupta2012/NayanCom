from ..models.mappers import REQUEST_MAP
from ..models.mappers import CV, Vitals
from .alert import send_alerts

# for locking
from fasteners import InterProcessLock  # platform agnostic
from json import dump

# for text to speech
from gtts import gTTS
import random
import os
import pygame
import time
from mutagen.mp3 import MP3


class ActionHandler:

    greets = ["Hey there", "Hi", "Hey", "Hi there"]

    confirms = ["Alright!", "Perfect!", "Okay sure!", "Sure!", "Okay!", "Awesome!"]

    def __init__(self, caretaker) -> None:
        # network details
        self.email = caretaker.email
        self.phone = caretaker.phone

    def update_model_vars(self, patient):

        # here, we need to lock the file
        # model_vars.json and then update it
        lock = InterProcessLock(
            r"/home/harshit/college/Sem-6/IOT/Project/NayanCom/server/data/vitals_face.json"
        )
        acquired = lock.acquire()

        # site may be reading the file
        while not acquired:
            acquired = lock.acquire(timeout=1)

        try:

            # update the data
            data = {
                "patient": {
                    "in_view": patient.in_view,
                    "vitals_detected": patient.vitals_detected,
                }
            }

            # this is running in the top level directory of the server
            # and we have the relative path as available in the server
            # root
            with open(
                r"/home/harshit/college/Sem-6/IOT/Project/NayanCom/server/data/vitals_face.json",
                "w",
            ) as file:
                dump(data, file)
            # print("File updated!")
            file.close()

        finally:
            lock.release()

    def handle_blinks(self, patient, previous_view, cv_model):
        # this will handle the state of cv model

        # only called when we are in_view
        # here we have an interface based on sound
        prev_state = cv_model.prev_state
        curr_state = cv_model.curr_state

        # print("Curr state is :", curr_state)
        text = {"play": "", "text": ""}

        em_state = False

        # email is to be sent only on a flip and
        # not continuously
        if not patient.in_view:
            if previous_view:
                text = """Patient's face is not in view. 
                        Please set up the device again."""
                send_alerts(text, self.email)
                cv_model.reset_model()
            else:
                cv_model.reset_model()
            return

        if curr_state == CV.IDLE:
            if prev_state != CV.IDLE:
                # need to inform them
                text["play"] = "Not sure if you're there. Deactivating model for now."
            else:
                text["play"] = "Not started."
            cv_model.reset_model()
        else:

            greeting = random.choice(self.greets)
            confirmation = random.choice(self.confirms)

            row_selected = cv_model.row
            col_selected = cv_model.col

            if curr_state == CV.ACTIVATE:
                if prev_state == CV.IDLE:
                    text["play"] = "Model is activated.\n"
                else:
                    text[
                        "play"
                    ] = "Not sure if we understood that. Please try to select again.\n"

            elif curr_state == CV.GOT_ROW:
                text["play"] = (
                    greeting + ", you have selected row " + str(row_selected) + ".\n"
                )
                text["play"] += "Please blink once to confirm.\n"

            elif curr_state == CV.CONFIRM_ROW:
                if prev_state == CV.GOT_ROW:
                    text["play"] = (
                        confirmation
                        + " Row "
                        + str(row_selected)
                        + " confirmed!\n"
                        + "Please select a column."
                    )
                elif prev_state == CV.GOT_COL:
                    text[
                        "play"
                    ] = "Sorry, we could not confirm your column selection. Can you select again?"

            elif curr_state == CV.GOT_COL:
                text["play"] = (
                    greeting
                    + ", you have selected "
                    + REQUEST_MAP[row_selected][col_selected]
                    + ".\n"
                )
                text["play"] += "Please blink once to confirm.\n"

            elif curr_state == CV.ALERT:
                if row_selected == 1:
                    # discomfort does not entail a greeting
                    text["play"] = (
                        confirmation + " Someone will be here with you shortly!"
                    )
                    text["text"] = (
                        "Patient requires "
                        + REQUEST_MAP[row_selected][col_selected]
                        + ". Please reach out to them.\n"
                    )
                else:
                    text[
                        "play"
                    ] = "Sorry to know that, someone will be here shortly to attend to you."
                    text["text"] = (
                        "The patient is experiencing "
                        + REQUEST_MAP[row_selected][col_selected]
                        + ". Please reach out to them.\n"
                    )

                # here, the alert is sent and we need to reset our models
                cv_model.reset_model()
            else:

                # patient in state of emergency
                text["play"] = "Please stay calm. Help is on the way.\n"
                text["text"] = "Patient requires immediate attention. Please hurry.\n"

                # means we send 3-4 messages to the person themselves
                em_state = True

                cv_model.reset_model()

        # say the confirmation sounds
        self.play_sound(text["play"])

        if len(text["text"]) > 0:
            send_alerts(text["text"], self.email, em_state)

    def handle_vitals(self, patient, vital_model, force_update=False):
        # there is no sound here
        # only the text or the alert to the em
        # services

        curr_state = vital_model.state

        if not patient.vitals_detected:
            text = f"""Patient vitals not being detected. 
                        Please set up the device again."""
            send_alerts(text, self.email)
            vital_model.reset_model()
            return

        if curr_state == Vitals.NORMAL:
            # do not send the data
            if force_update:
                text = f"""Patient vitals are normal.
                           Heart Rate - {patient.heart_rate} bpm """
                send_alerts(text, self.email)
        else:

            text = ""
            em_state = False
            if curr_state == Vitals.ALERT:
                # need to send the text
                text = f"""Patient requires attention.
                            Heart Rate - {patient.heart_rate} bpm """
            else:
                # need to send and alert the em services
                text = f"""Alert! Patient vitals critical"""
                text += f"\nHeart Rate critical : {patient.heart_rate} bpm"
                em_state = True
            send_alerts(text, self.email, em_state)
        vital_model.reset_model()

    def play_sound(self, text):
        """To play the sounds for the patient interaction

        NOTE : if we have an idle state, no point in
               telling that to the patient.
        """

        if "Not started" in text:
            pygame.mixer.init()
            background = pygame.mixer.Sound(r"data/sounds/constant2.wav")
            background.play(fade_ms=1000)
            time.sleep(4)
            pygame.quit()
            return

        randf = str(int((random.random() * 2600) % 2101))
        sound_fp = rf"data/sounds/{randf}.mp3"

        open(sound_fp, "w").close()
        tts = gTTS(text, lang="en")

        # save and play
        tts.save(sound_fp)
        audio = MP3(sound_fp)
        t = audio.info.length

        # play the notification
        pygame.mixer.init()
        notif = pygame.mixer.Sound(r"data/sounds/notification.wav")
        notif.play(fade_ms=500)
        time.sleep(1)

        # play the saved text
        pygame.mixer.init()
        pygame.mixer.music.load(sound_fp)
        pygame.mixer.music.play(fade_ms=500)
        time.sleep(t)
        pygame.quit()

        os.remove(sound_fp)


def blink_detect():
    pygame.mixer.init()
    notif = pygame.mixer.Sound(r"data/sounds/blink.wav")
    notif.play(fade_ms=500)
    time.sleep(1)
    return
