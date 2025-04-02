#include <Wire.h>
#include "Adafruit_MPRLS.h"
#include <PMW3360.h>

// You dont *need* a reset and EOC pin for most uses, so we set to -1 and don't connect
#define RESET_PIN  -1  // set to any GPIO pin # to hard-reset on begin()
#define EOC_PIN    -1  // set to any GPIO pin to read end-of-conversion by pin
Adafruit_MPRLS mpr = Adafruit_MPRLS(RESET_PIN, EOC_PIN);
int pumpControl =  5; 
#define SS  10   // Slave Select pin. Connect this to SS on the module.
int timepassed = 0;
PMW3360 sensor;


void setup() {
  Serial.begin(115200);
  Serial.println("MPRLS Simple Test");
  if (! mpr.begin()) {
    Serial.println("Failed to communicate with MPRLS sensor, check wiring?");
    while (1) {
      delay(10);
    }
  }
  Serial.println("Found MPRLS sensor");
    if(sensor.begin(SS))  // 10 is the pin connected to SS of the module.
    Serial.println("Sensor initialization successed");
  else
    Serial.println("Sensor initialization failed");
  
}


void loop() {
  static unsigned long pumpStartTime = 0;  // Store pump activation time
  static bool pumpRunning = false;         // Track pump state

  // Read pressure
  float pressure_hPa = mpr.readPressure();
  float pressure_PSI = pressure_hPa / 68.947572932;

  //Serial.print("Pressure (hPa): ");
  //Serial.print(pressure_hPa);
 // Serial.println(pressure_hPa);
 // Serial.print("Pressure (PSI): ");
 // Serial.println(pressure_PSI);
 // Serial.println(pressure_PSI);

  // Check pressure and control pump
  if (pressure_PSI > 16.9 && !pumpRunning && timepassed >= 100) {
    Serial.println("Pump ON");
    analogWrite(pumpControl, 255);  // Turn on pump
    pumpStartTime = millis();       // Record the time when pump was turned on
    pumpRunning = true;             // Mark pump as running
    timepassed = 0;
  }

  // Turn off pump after 30ms
  if (pumpRunning && (millis() - pumpStartTime >= 30)) {
    Serial.println("Pump OFF");
    analogWrite(pumpControl, 0);    // Turn off pump
    pumpRunning = false;            // Reset pump state
  }

  // Read PMW3360 sensor continuously
  PMW3360_DATA data = sensor.readBurst();
  Serial.print("Max Raw Data: ");
  Serial.println(data.maxRawData);
  // Serial.print("\tMin Raw Data: ");
  // Serial.println(data.minRawData);

  delay(10); // Small delay to allow continuous readings
  timepassed++;
}