
from enum import Enum

REQUEST_MAP = {
    1 : {1 : "water", 2 : "food", 3 : "lights"}, 
    2 : {1 : "bodyache", 2 : "cold and cough", 3 : "head ache"},
    3 : {1 : "limb pain", 2 : "fatigue", 3 : "chest pain"}
}

class CV(Enum):
    IDLE = 0
    ACTIVATE = 1
    GOT_ROW = 2
    CONFIRM_ROW = 3
    GOT_COL = 4
    ALERT = 5
    EM = 6
    
class Vitals(Enum):
    NORMAL = 0 
    ALERT = 1 
    EM = 2 

class VitalLevels:
    """Class to classify the vitals into different 
       levels and based on the classification, 
       either send alert to caretaker or em services"""
    heart_rates = [
        (0,39,"DANGER-LOW"), # DANGEROUS
        (40,100,"NORMAL"),
        (101,130,"ATTENTION"),
        (131,200,"DANGER-HIGH") # DANGEROUS
    ]
    
    o2_levels = [
        # IN %AGE 
        (96,100, "NORMAL"), 
        (95,96, "ATTENTION"),
        (93,95, "ATTENTION"),
        (50,92, "DANGER-LOW") #DANGEROUS
    ]
    
    @staticmethod
    def classify_heart_rate(cls, beats):
        for rate in cls.heart_rates:
            if beats >= rate[0] and beats <= rate[1]:
                status = rate[2]
                break
        return status 
    
    
    @staticmethod
    def classify_o2_level(cls,o2_level):
        for level in cls.o2_levels:
            if o2_level >= level[0] and o2_level <= level[1]:
                status = level[2]
                break 
        return status 