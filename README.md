# NayanCom <image src="https://user-images.githubusercontent.com/57539040/161391234-3518c685-61e4-4acd-b602-c6e95d008362.png" align = "center" height = 60px width = 75px>

A patient monitoring and well being assistant.

- **Course** : COCSC20 | Internet of Things
- **Semester** : Spring 2022
- **Team Members** : [Tabishi Singh](https://github.com/TabishiSingh06) | [Aryaman Sharma](https://github.com/aryamansharma01) | [Harshit Gupta](https://github.com/TheGupta2012) 

This project aims to include a new layer of usability to already available automation assistants. Siri, Cortana, Alexa all have voice based input mechanisms but we aim to extend this to the human eye. Given a physically handicapped/paralysed patient, our project would enable them to perform basic daily actions and allow low-cost vital monitoring.
  
<img width="960" alt="image" src="https://user-images.githubusercontent.com/69653249/161682962-66e713ac-7335-42f5-a940-101f2abce485.png">
  
## Motivation 
The project aims to solve the human computer interaction (HCI) problem for people with temporary or permanent motion and speech disabilities. Our approach uses the blinking actions of a user to allow easy communication with their caretakers and medical services for a better patient experience. Along with the communication aspect, we also have a patient monitoring aspect where the patient’s essential vitals are tracked. For these two functionalities, an analysis of computer vision models and human vital sensors such as heart sensors are required.

## Components 
### ▶️ Blink Detection 
- The program first makes use of a facial landmark detection model to ensure that the camera is positioned properly and the face and eyes are clearly discernible. Python's **dlib** and **openCV** packages are used for facial recognition and blink detection.
- The OpenCV model uses a metric called *Eye Aspect Ratio* for the detection of the eye blinks, as proposed in the paper [Real-Time Eye Blink Detection using Facial Landmarks](http://vision.fe.uni-lj.si/cvww2016/proceedings/papers/05.pdf). 
- Our system has an initial time window of 5 seconds. During the time window, if any blink is detected, the window size is increased by a second to accomodate more blinks by a user. At the end of a time chunk, up to a limit of 12 seconds, the blinks of the user are registered.

  <img width="10%" height="25%" alt="image" src="https://user-images.githubusercontent.com/54472596/161683149-85018dec-1a04-40ac-984d-d850cc85f5aa.png">

### ▶️ Python Model
- Our model consists of two action handlers.

  1. **Data Handler** 
     - **CVDataHandler** implements a model for the CV blink detection. It receives periodic inputs from the user and updates the state of our model.
     - **VitalDataHandler** aims to model the periodic vital data coming from the user and updates model state depending on  the inputs
  2. **Action Handler** processes the state of the data models. It is responsible for the audio interface between the user and the system. Depending on the states and the inputs, it also produces an alert to the caretaker.
  
  <img width="10%" height="25%" alt="image" src="https://user-images.githubusercontent.com/54472596/161683332-be55e94d-6099-4c4f-aa14-03d3376c5772.png">


### ▶️ Vital Detection
 - For heart rate sensing, we utilised a plug-and-play heart-rate sensor for Arduino.
 - The sensor was connected to an Arduino Nano for processing, and an  HC-05 bluetooth module for communicating patient vitals to our model.
 - Data is periodically sent to the data handler, following which the appropriate action is taken.

  <img width="10%" height="25%" alt="image" src="https://user-images.githubusercontent.com/54472596/161683363-70b31bcc-db09-4e9d-9a14-909d6289ea93.png">

### ▶️ Website 
- For the user interface we made a website using the React.js framework.
- The website runs on a nodeJS server and initially reads the caretaker’s contact info from the homepage. 
- This contact info is used to alert the caretaker when the person makes a choice from the NayanCommand chart.
- The website communicates with the python model using JSON files. The site alerts the caretaker with the status of the vitals, commands which the patient issues and whether there is an emergency situation or not.
  
  <img width="960" alt="image" src="https://user-images.githubusercontent.com/69653249/161683014-b54fce1f-eea8-40e3-a9f8-994619087a28.png">


  
