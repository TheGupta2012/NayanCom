from json import load

class Patient:
    def __init__(self) -> None:
        # requests
        self.in_view = False
        self.requesting = False
        self.request = None 
        
        # vitals
        self.vitals_detected = False 
        self.heart_rate = None 
        self.o2_level = None 
        

class Caretaker:
    def __init__(self) -> None:
        self.email, self.phone, self.em_service = self._generate_details()
        
    def _generate_details(self):
        
        # no locks required as this is done only after the model is 
        # initiated by the website
        with open("../data/contact_details.json") as file:
            data = load(file)
        
        email = data["contact"]["email"]
        phone = data["contact"]["phone"]
        
        # this is not sure...
        em_service = data["contact"]["em_service"]
        
        return (email, phone, em_service)
        
   
 