# get handlers
from .handlers.action import ActionHandler
from .handlers.data import VitalDataHandler

# get actors
from .models.actors import Patient, Caretaker


caretaker = Caretaker()


# vitals data
vital_readings = []
update_vitals = False
total_readings = 0

vital_data_model = VitalDataHandler()

# action
action_model = ActionHandler(caretaker)


# for vitals
import serial

serialPort = serial.Serial(port="/dev/rfcomm1", baudrate=9600, timeout=4)

# cv model initial
# vs = VideoStream(src=0).start()

while True:
    # Try to read the data from the serial port
    try:
        sensor_data = serialPort.readline()
        vitals = sensor_data.decode("utf-8").split(":")
        heart_rate = max(55, int(vitals[-1]) - 120)  # some calibration error
        vital_readings.append(heart_rate)

        total_readings += 1

        if len(vital_readings) == 10:
            vital_data = {
                "has_vitals": True,
                "heart_rate": sum(vital_readings) // 10,
            }
            print("Avg. Vitals registered :", vital_data)

            vital_readings.clear()
            Patient.vitals_registered = True

            vital_data_model.receive_data(Patient, data=vital_data)

            # data handler will update the value of Patient vitals detected inside
            # the model, here just keep on sending vitals in interval of 30 seconds

        if total_readings >= 40:
            update_vitals = True
            total_readings = 0

    except:
        Patient.vitals_detected = False

    if Patient.vitals_registered:
        action_model.handle_vitals(Patient, vital_data_model, update_vitals)
        Patient.vitals_registered = False

        if update_vitals:
            update_vitals = False

    action_model.update_model_vars(Patient)
