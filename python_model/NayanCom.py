from python_model.handlers.action import ActionHandler 
from python_model.handlers.data import CVDataHandler, VitalDataHandler 

# get the actors
from python_model.models.actors import Patient, Caretaker 

# get the serial module
import serial 


# generate the actors 
patient = Patient()
caretaker = Caretaker()

# start the data recording 
cv_model = None # TO DO - by aryaman, CV_Model()

cv_data_model = CVDataHandler()
vital_data_model = VitalDataHandler()

action_model = ActionHandler()

# first, it will detect the vitals 
serialPort = serial.Serial(port = 'COM5', baudrate = 9600, timeout = 1)

serialPort.open()

while True:
    # Try to read the data from the serial port
    try:
        # we will send data like 
        
        """ "BPM , O2_LEVEL" """
        sensor_data = serialPort.readline().split(",")
        
        # Since we will send data in a specific format
        # the following code works
        vital_data = {"has_vitals" : True, 
                      "heart_rate" : int(sensor_data[0]),
                      "o2_level" : int(sensor_data[1])}
        vital_data_model.recieve_data(patient, data = vital_data)
    except:
        patient.vitals_detected = False 
        
    try:
        cv_data = None # TO DO:  recieve data from aryaman's model 
        cv_data_model.recieve_data(patient, data= cv_data)
    except:
        patient.in_view = False 
        
        
    if patient.detected:
        action_model.handle_blinks(cv_data_model)
        action_model.handle_vitals(patient, vital_data_model)
    
    
    action_model.update_model_vars(patient)


