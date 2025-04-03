#include <Wire.h>
#include "Adafruit_MPRLS.h"
#include <PMW3360.h>

// You dont *need* a reset and EOC pin for most uses, so we set to -1 and don't connect
#define RESET_PIN  -1  // set to any GPIO pin # to hard-reset on begin()
#define EOC_PIN    -1  // set to any GPIO pin to read end-of-conversion by pin
Adafruit_MPRLS mpr = Adafruit_MPRLS(RESET_PIN, EOC_PIN);
int puffControl =  5; 
int powerPump = 4;
#define SS  10   // Slave Select pin. Connect this to SS on the module.
int timepassed = 0;
PMW3360 sensor;
bool teststarted = false;
int startindex = 0;
bool pufffired = false;
bool puffended = false;
int puffindex = 0;
static bool pumpRunning = false;         // Track pump state
static unsigned long pumpStartTime = 0;  // Store pump activation time


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

  if (teststarted == false) {
    while(true) {
      if (digitalRead(2) == LOW) {
        teststarted = true;
        startindex = 0;
        break;
      }
    }
  }


  // Read pressure
  float pressure_hPa = mpr.readPressure();
  float pressure_PSI = pressure_hPa / 68.947572932;

  //Serial.print("Pressure (hPa): ");
  //Serial.print(pressure_hPa);
 // Serial.println(pressure_hPa);
  Serial.print("Pressure (PSI): ");
  Serial.println(pressure_PSI);
 // Serial.println(pressure_PSI);


  if (startindex >= 10){
    analogWrite(powerPump, 255);
  }


  // Check pressure and control pump
  if ((pressure_PSI > 16.9 || isnan(pressure_PSI)) && !pufffired && timepassed >= 10) {
    Serial.println("Puff Started");
    analogWrite(puffControl, 255);  // Turn on puff
    pumpStartTime = millis();       // Record the time when pump was turned on
    timepassed = 0;
    pufffired = true;
  }

  // Turn off pump after 30ms
  if (puffindex >= 3 && puffended == false) {
    Serial.println("Puff Ended");
    puffended = true;
    analogWrite(puffControl, 0);    // Turn off puff
    analogWrite(powerPump, 0);
    startindex = 0;
  }

  // Read PMW3360 sensor continuously
  PMW3360_DATA data = sensor.readBurst();
  Serial.print("Max Raw Data: ");
  Serial.println(data.maxRawData);
  // Serial.print("\tMin Raw Data: ");
  // Serial.println(data.minRawData);

  delay(10); // Small delay to allow continuous readings
  timepassed++;
  startindex++;
  if (pufffired == true) {
    puffindex++;
  }
  if (puffindex >= 5) {
    teststarted = false;
    startindex = 0;
    puffindex = 0;
    pufffired = false;
    puffended = false;
  }
}