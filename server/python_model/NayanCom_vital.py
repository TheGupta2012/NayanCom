# get handlers
from .handlers.action import ActionHandler
from .handlers.data import VitalDataHandler

# get actors
from .models.actors import Patient, Caretaker

# os
import os
import json
import time

# save the pid for killing process
pid = {"id": os.getpid()}

with open(
    r"data/pid_vitals.json",
    "w",
) as f:
    json.dump(pid, f)
f.close()

caretaker = Caretaker()


# vitals data
vital_readings = []
update_vitals = False
total_readings = 0

vital_data_model = VitalDataHandler()
REPORTING_TIME = 10  # if there is anything

# action
action_model = ActionHandler(caretaker)

# Initiate
Patient.vitals_detected = False
action_model.update_model_vars(Patient, vitals=False, blinks=False)  # as False


# for vitals
import serial

serialPort = serial.Serial(port="/dev/rfcomm1", baudrate=9600, timeout=4)


while True:
    # Try to read the data from the serial port
    try:
        sensor_data = serialPort.readline()
        vitals = sensor_data.decode("utf-8").split(":")
        heart_rate = max(55, int(vitals[-1]) - 120)  # some calibration error
        vital_readings.append(heart_rate)

        Patient.vitals_detected = True
        total_readings += 1

        if len(vital_readings) == REPORTING_TIME:
            vital_data = {
                "has_vitals": True,
                "heart_rate": sum(vital_readings) // REPORTING_TIME,
            }
            print("Avg. Vitals registered :", vital_data)

            vital_readings.clear()
            Patient.vitals_registered = True

            vital_data_model.receive_data(Patient, data=vital_data)

            # data handler will update the value of Patient vitals detected inside
            # the model, here just keep on sending vitals in interval of 30 seconds

        if total_readings >= 300:  # every 5 minutes force update
            update_vitals = True
            total_readings = 0

    except:
        # if not detected attach a delay
        Patient.vitals_detected = False
        time.sleep(10)
        Patient.vitals_registered = True  # no vitals is also a vital reading

    if Patient.vitals_registered:
        action_model.handle_vitals(Patient, vital_data_model, update_vitals)
        Patient.vitals_registered = False

        if update_vitals:
            update_vitals = False

        action_model.update_model_vars(Patient, vitals=True, blinks=False)
