#define USE_ARDUINO_INTERRUPTS true // Set-up low-level interrupts for most acurate BPM math.
#include <PulseSensorPlayground.h> // Includes the PulseSensorPlayground Library.

// Variables
const int PulseWire = 0; // PulseSensor PURPLE WIRE connected to ANALOG PIN 0
const int LED13 = 13; // The on-board Arduino LED, close to PIN 13.
int Threshold = 550; // Determine which Signal to "count as a beat" and which to ignore.

PulseSensorPlayground pulseSensor; // Creates an instance of the PulseSensorPlayground object called "pulseSensor"
void setup() {

Serial.begin(9600); // For Serial Monitor
pulseSensor.analogInput(PulseWire);
pulseSensor.blinkOnPulse(LED13); //auto-magically blink Arduino's LED with heartbeat.
pulseSensor.setThreshold(Threshold);

// Double-check the "pulseSensor" object was created and "began" seeing a signal.
if (pulseSensor.begin()) {
Serial.println("We created a pulseSensor Object !"); //This prints one time at Arduino power-up, or on Arduino reset.
}

}
 
void loop() {
 
int myBPM = pulseSensor.getBeatsPerMinute(); // Calls function on our pulseSensor object that returns BPM as an "int".

// "myBPM" hold this BPM value now.
if (pulseSensor.sawStartOfBeat()) 
{ 
 // Constantly test to see if "a beat happened".
//Serial.println("A HeartBeat Happened ! "); // If test is "true", print a message "a heartbeat happened".
Serial.print("BPM:"); // Print phrase "BPM: "
Serial.print(myBPM); // Print the value inside of myBPM.
Serial.print("\n"); // new line
}
delay(1000); // considered best practice in a simple sketch.
}