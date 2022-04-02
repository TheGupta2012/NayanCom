# NayanCom <image src="https://user-images.githubusercontent.com/57539040/161391234-3518c685-61e4-4acd-b602-c6e95d008362.png" align = "center" height = 60px width = 75px>

A patient monitoring and well being assistant.

- **Course** : COCSC20 | Internet of Things
- **Semester** : Spring 2022
- **Team Members** : [Tabishi Singh](https://github.com/TabishiSingh06) | [Aryaman Sharma](https://github.com/aryamansharma01) | [Harshit Gupta](https://github.com/TheGupta2012) 

This project aims to include a new layer of usability to the already available automation assistants. Siri, Cortana, Alexa all have voice based input mechanisms but we aim to extend this to the human eye. Given a physically handicapped/paralysed patient, our project would enable them to perform basic daily actions and allow low-cost vital monitoring.

## Motivation 
The project aims to  solve the human computer interaction (HCI) problem for people with temporary or permanent motion and speech disabilities. Our approach uses the blinking actions of a user to allow easier communication with their caretakers and medical services for a better patient experience. Along with the communication aspect, we also have a patient monitoring aspect where the patient’s essential vitals are tracked. For these two functionalities, an analysis of computer vision models and human vital sensors such as heart sensors are required.

## Components 
### ▶️ Blink Detection 
- The model first makes use of a facial landmark detection dataset to ensure that the camera is positioned properly and the face and eyes are clearly discernible. Python's **dlib** and **openCV** packages are used for the facial regonition and blink detection
- OpenCV model uses a metric called *Eye Aspect Ratio* for the detection of the eye blinks. 
- Our system has an initial time window of 5 seconds. During the time window, if any blink is detected, the window size is increased by a second to accomodate more blinks by a user. At the end of a time chunk, the blinks of the user are registered.

  
### ▶️ Python Model
  
### ▶️ Vital Detection
  
### ▶️ Website 
  
