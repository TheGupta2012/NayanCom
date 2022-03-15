from json import load

class Patient:
    def __init__(self) -> None:
        self.in_view = False

        # vitals
        self.vitals_detected = False 
        self.blink_registered = False 
        self.heart_rate = None 
        self.o2_level = None 
        
    def detected(self, patient):
 
        view = patient.in_view 
        vitals = patient.vitals_detected 
        return (vitals and view)
    

class Caretaker:
    def __init__(self) -> None:
        self.email, self.phone, self.em_service = self._generate_details()
        
    def _generate_details(self):
        
        # no locks required as this is done only after the model is 
        # initiated by the website
        # with open("../data/contact_details.json") as file:
        #     data = load(file)
        
        email = "harshit.11235@gmail.com"
        phone = "7289947376"
        
        # this is not sure...
        em_service = "abc@gmail.com"
        
        return (email, phone, em_service)
        
   
 