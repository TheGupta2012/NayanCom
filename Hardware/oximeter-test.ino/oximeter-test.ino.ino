#include <Wire.h>
#include "MAX30100_PulseOximeter.h"

#define REPORTING_PERIOD_MS  2000

// PulseOximeter is the higher level interface to the sensor
// it offers:
//  * beat detection reporting
//  * heart rate calculation
//  * SpO2 (oxidation level) calculation

PulseOximeter pox;

uint32_t tsLastReport = 0;

// Callback (registered below) fired when a pulse is detected
void onBeatDetected()
{
  Serial.println("Beat!");
}

void setup()
{
  Serial.begin(115200);

  Serial.print("Initializing...");

  // Initialize the PulseOximeter instance
  // Failures are generally due to an improper I2C wiring, missing power supply
  // or wrong target chip
  
  if (!pox.begin()) {
    Serial.println("MAX30100 was not found. Please check the wiring/power.");
    for (;;);
  } else {
    Serial.println("SUCCESS");
  }

  // The default current for the IR LED is 50mA and it could be changed
  //   by uncommenting the following line. Check MAX30100_Registers.h for all the
  //   available options.
  
   pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);

  // Register a callback for the beat detection
  pox.setOnBeatDetectedCallback(onBeatDetected);
}

void loop()
{
  float HeartRate = 3.0, SpO2 = 3.0;

  // Make sure to call update as fast as possible
  pox.update();
  HeartRate = pox.getHeartRate();
  SpO2 = pox.getSpO2();
  
  // Asynchronously dump heart rate and oxidation levels to the serial
  // For both, a value of 0 means "invalid"
  
  if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
    
    Serial.print(HeartRate);
    Serial.print(",");
    Serial.print(SpO2);

    tsLastReport = millis();
  }
}
