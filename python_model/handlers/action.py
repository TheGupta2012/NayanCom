
# 1. Reads the data of the - 
        # a. Patient
        # b. VitalDataHandler
        # c. CVDataHandler
        
# and acc to the states of the models, generates a text field for the 
# vitals and a text field for the request (if any)

# 2. Uses the patient's in_view and vital_detected property 
#    to reset the models, if set. If any one of the property is not
#    set, both models are reset and a notification to the caretaker sent
#    (only when the CHANGE happens, from True to False)
#    After this, the site is updated so that when the person comes, they can 
#    see while re-adjusting the elements

# if the in_view and vital_detected are True ( both ) then - 

# 3. Uses the text fields and sends the message to the caretaker via the 
#    smtp server or the twilio API for the message. If there is an emergency 
#    situation, also sends a call to the emergency services with the 
#    LOCATION of the request and the vitals of the patient.


# 4. After the optional sending of the messages, it will update the states of 
#    the models accordingly by calling the reset_model function 

# 5. Repeat

from ..models.mappers import REQUEST_MAP 
from ..models.mappers import VitalLevels, CV, Vitals
from .alert import send_alerts

# for locking
# from fasteners import InterProcessLock # platform agnostic
from json import dump  

#for tts 
from gtts import gTTS
import random 
import os
import pygame
import time
from mutagen.mp3 import MP3
class ActionHandler:
    
    greets = ["Hey there", "Hi", "Hey", "Hi there"]
    
    # confirm = ["Are you sure about that?", "Is this what you selected?", "Please confirm once!",
    #             "Is that it?", "For sure?", "Are you sure?", "Confirm your choice!"]
    
    confirms = ["Alright!", "Perfect!", "Okay sure!", "Sure!",
                "Okay!", "Awesome!"]
        
    def __init__(self, caretaker) -> None:
        # network details
        self.email = caretaker.email
        self.phone = caretaker.phone
        
        # not really sure...
        # self.em_phone = caretaker.em_service
    

    def update_model_vars(self, patient):
        
        # here, we need to lock the file 
        # model_vars.json and then update it 
        
        # lock = InterProcessLock("../data/model_vars.json")   
        # acquired = lock.acquire()
    
        # # site may be reading the file
        # while not acquired:
        #     acquired = lock.acquire(timeout=2)
        
        # try:
        #     # update the data 
        #     
        data = {    "patient":
                    {
                    "in_view" : patient.in_view, 
                    "vitals_detected" : patient.vitals_detected
                    }
                }
        file = open(r"C:\Users\aryam\NayanCom\python_model\data\patient_detected.json", "w")
        dump(data, file)
        file.close()    
            
        # finally:
        #     lock.release()
        
    
    def handle_blinks(self, cv_model):
        # this will handle the state of cv model
        
        # only called when we are in_view
        # here we have an interface based on sound 
        prev_state = cv_model.prev_state
        curr_state = cv_model.curr_state
        
        text = {"play" : "", 
                "text" : ""}
        em_state = False
        
        if curr_state == CV.IDLE:
            if prev_state != CV.IDLE:
                # need to inform them 
                text["play"] = "Not sure if you're there. Deactivating model for now."
            else:
                text["play"] = "Not started now."
            cv_model.reset_model()
        else:
            
            greeting = random.choice(self.greets)
            confirmation = random.choice(self.confirms)
            
            if cv_model.row is not None:
                row_selected = cv_model.row 
            if cv_model.col is not None:
                col_selected = cv_model.col 
                
            if curr_state == CV.ACTIVATE:
                if prev_state == CV.IDLE:
                    text["play"] = "Model is activated.\n"
                else:
                    text["play"] = "Not sure if we understood that. Please try to select again.\n"
                
            elif curr_state == CV.GOT_ROW:
                text["play"] = greeting + ", you have selected row " + str(row_selected) +".\n"
                text["play"] += "Please blink once to confirm.\n"
                
            elif curr_state == CV.CONFIRM_ROW:
                text["play"] = confirmation + " Row " + str(row_selected) + " confirmed!\n"
            
            elif curr_state == CV.GOT_COL:
                text["play"] = greeting + ", you have selected " + \
                    REQUEST_MAP[row_selected][col_selected] + ".\n"
                text["play"] += "Please blink once to confirm.\n"
            
            elif curr_state == CV.ALERT:
                if row_selected == 1:
                    # discomfort does not entail a greeting
                    text["play"] = confirmation + " Someone will be here with you shortly!"
                    text["text"] = "Patient requires " + REQUEST_MAP[row_selected][col_selected] + ". Please reach out to them.\n"
                else:
                    text["play"] = "Sorry to know that, someone will be here shortly to attend to you."
                    text["text"] = "The patient is experiencing " + REQUEST_MAP[row_selected][col_selected] + ". Please reach out to them.\n"
                
                # here, the alert is sent and we need to reset our models
                cv_model.reset_model()
            else:
                
                # patient in state of emergency
                text["play"] = "Please stay calm. Help is on the way.\n"
                text["text"] = "Patient requires immediate attention. Please hurry.\n"
                
                # means we send 3-4 messages to the person themselves
                em_state = True 
                
                cv_model.reset_model()
            
        if len(text["text"]) > 0:
            send_alerts(text["text"], self.email, em_state)
        
        # say the confirmation sounds 
        self.play_sound(text["play"])
        
    
    def handle_vitals(self, patient, vital_model):
        # there is no sound here 
        # only the text or the alert to the em 
        # services 
        
        curr_state = vital_model.state 
        print("Current state of model :", curr_state)

        if curr_state == Vitals.NORMAL:
            # do not send the data 
            pass 
        else:
            text = ""
            em_state = False 
            if curr_state == Vitals.ALERT:
                # need to send the text 
                text = f"""Patient requires attention.
                            Heart Rate - {patient.heart_rate} bpm 
                            Oxygen level - {patient.o2_level}%"""
            else:
                # need to send and alert the em services 
                text = f"""Alert! Patient vitals critical""" 
                if patient.heart_danger:
                    text+= f"\nHeart Rate critical : {patient.heart_rate} bpm"
                if patient.o2_danger:
                    text+= f"\nOxygen level critical : {patient.o2_level}%"
                em_state = True 
              
            send_alerts(text, self.email, em_state)
        
        vital_model.reset_model()

    def play_sound(self, text):

        print(text)
        randf = int((random.random()*2600)%2101)
        sound_fp = rf"C:\Users\aryam\NayanCom\python_model\data\{str(randf)}.mp3"
        open(sound_fp,'w').close()
        tts = gTTS(text, lang = 'en')

        #save and play
        tts.save(sound_fp)
        audio = MP3(sound_fp)
        t = audio.info.length
        pygame.mixer.init()
        pygame.mixer.music.load(sound_fp)
        pygame.mixer.music.play()
        
        time.sleep(t)
        pygame.quit()
        os.remove(sound_fp)
        
        
        
    
                
    
        
