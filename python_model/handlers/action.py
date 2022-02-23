
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

# for text 
import twilio 

# for locking
from fasteners import InterProcessLock
from json import dump  

# for tts 
from gtts import gTTS
import random 
from os import system


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
    
    def check_patient_status(self, patient):
        
        view = patient.in_view 
        vitals = patient.vitals_detected 
        return (vitals and view)
    
    
    def update_model_vars(self, patient):
        
        # here, we need to lock the file 
        # model_vars.json and then update it 
        
        lock = InterProcessLock("../data/model_vars.json")   
        acquired = lock.acquire()
    
        # site may be reading the file
        while not acquired:
            acquired = lock.acquire(timeout=2)
        
        try:
            # update the data 
            data = {    "patient":
                        {
                        "in_view" : patient.in_view, 
                        "vitals_detected" : patient.vitals_detected
                        }
                    }
            file = open("../data/model_vars.json", "w")
            dump(data, file)
            file.close()    
            
        finally:
            lock.release()
        
    
    def handle_blinks(self, cv_model):
        # this will handle the state of cv model
        
        # only called when we are in_view
        # here we have an interface based on sound 
        prev_state = cv_model.prev_state
        curr_state = cv_model.curr_state
        
        text = {"play" : "", 
                "send" : ""}
        em_state = False
        
        if curr_state == "IDLE":
            if prev_state != "IDLE":
                # need to inform them 
                text["play"] = "Not sure if you're there. Deactivating model for now"
                cv_model.reset_model()
        else:
            
            greeting = random.choice(self.greets)
            confirmation = random.choice(self.confirms)
            
            if cv_model.row is not None:
                row_selected = cv_model.row 
            if cv_model.col is not None:
                col_selected = cv_model.col 
                
            if curr_state == "ACTIVATE":
                if prev_state == "IDLE":
                    text["play"] = "Model is activated."
                else:
                    text["play"] = "Not sure if we understood that. Could you "
                
            elif curr_state == "GOT ROW":
                text["play"] = greeting + ", you have selected row " + str(row_selected)
                text["play"] += "Please blink once to confirm"
                
            elif curr_state == "CONFIRM ROW":
                text["play"] = confirmation + " Row " + str(row_selected) + " confirmed!"
            
            elif curr_state == "GOT COL":
                text["play"] = greeting + ", you have selected " + REQUEST_MAP[row_selected][col_selected]
                text["play"] += "Please blink once to confirm"
            
            elif curr_state == "ALERT":
                if row_selected == 1:
                    # discomfort does not entail a greeting
                    text["play"] = confirmation + ". Someone will be here with you shortly!"
                    text["text"] = "Patient requires " + REQUEST_MAP[row_selected][col_selected] + ". Please reach out to them."
                else:
                    text["play"] = "Sorry to know that, someone will be here shortly to attend to you."
                    text["text"] = "The patient is experiencing " + REQUEST_MAP[row_selected][col_selected] + ". Please reach out to them."
                
                # here, the alert is sent and we need to reset our models
                cv_model.reset_model()
            else:
                # patient in state of emergency
                text["play"] = "Please stay calm. Help is on the way."
                text["text"] = "Patient requires immediate attention. Please hurry."
                em_state = True 
                
                cv_model.reset_model()
            
            self.play_sound(text["play"])
            self.send_alerts(text["text"], em_state)
    
    def handle_vitals(self, patient, vital_model):
        # there is no sound here 
        # only the text or the alert to the em 
        # services 
        
        curr_state = vital_model.state 
        
        if curr_state == "NORMAL":
            # do not send the data 
            pass 
        else:
            text = ""
            em_state = False 
            if curr_state == "ATTENTION":
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
              
            self.send_alerts(text, em_state)
        
        vital_model.reset_model()
        # not required to send the text to em service directly 
        
    def play_sound(self, text):
        sound_fp = "../data/sound.mp3"
        tts = gTTS(text, lang = 'en')
        
        # save and play
        tts.save(sound_fp)
        system("mpg123 " + sound_fp)
        
        
    def send_alerts(self, text, em_state):
        # uses the text module to send the alert
        # email or phone 
        
        # try to send text messages only 
        
        # first need to set the env vars 
        # then, verify the caretaker's number 
        # after that, you can send the message alerts 
        
        pass 
        
    
                
    
        