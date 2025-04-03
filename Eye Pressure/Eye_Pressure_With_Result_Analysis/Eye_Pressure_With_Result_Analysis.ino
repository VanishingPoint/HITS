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
PMW3360 sensor;
bool teststarted = false;
bool pufffired = false;
bool puffended = false;
int puffindex = 0;
int i;
const int buttonPin = 2;  // the number of the pushbutton pin
int buttonState;
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 50;    // the debounce time; increase if the output flickers

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

  pinMode(buttonPin, INPUT);

  analogWrite(powerPump, 255);
  
}

void startPressure() {

  float pressure_hPa = mpr.readPressure();
  float pressure_PSI = pressure_hPa / 68.947572932;

  while (pressure_PSI < 19 && !isnan(pressure_PSI)) {
    analogWrite(powerPump, 0);
    pressure_hPa = mpr.readPressure();
    pressure_PSI = pressure_hPa / 68.947572932;
  }

  analogWrite(powerPump, 255);

  Serial.print("Pressure (PSI): ");
  Serial.println(pressure_PSI);

}

float findMin(float arr[], int n) {
  
    // Assume first element as minimum
    float min = arr[0];
    for (int i = 1; i < n; i++) {
      
      	// Update m if arr[i] is smaller
        if (arr[i] < min) {
            min = arr[i]; 
        }
    }
    return min;
}

void loop() {

  if (teststarted == false) {
    while(true) {
      if (digitalRead(buttonPin) == LOW){
        teststarted = true;
        break;
      }
    }
  }

  float prepuffsum = 0;
  startPressure();

  for (i=0; i<=4; i++) {
    PMW3360_DATA data = sensor.readBurst();
    Serial.print("Max Raw Data: ");
    Serial.println(data.maxRawData);
    prepuffsum += data.maxRawData;
    delay(10);
  }

  float averageprepuff = prepuffsum/5;

  float postpuffvals[8];

  Serial.println("Puff Started");
  analogWrite(puffControl, 255);  // Turn on puff

  for (i=0; i<=2; i++) {
    PMW3360_DATA data = sensor.readBurst();
    Serial.print("Max Raw Data: ");
    Serial.println(data.maxRawData);
    postpuffvals[i] = data.maxRawData;
    delay(10);
  }

  analogWrite(puffControl, 0);
  Serial.println("Puff Ended");

  for (i=0; i<=4; i++) {
    PMW3360_DATA data = sensor.readBurst();
    Serial.print("Max Raw Data: ");
    Serial.println(data.maxRawData);
    postpuffvals[i+3] = data.maxRawData;
    delay(10);
  }

  int n = sizeof(postpuffvals) / sizeof(postpuffvals[0]);
  float minpuffval = findMin(postpuffvals, n);

  float difference = averageprepuff - minpuffval;

  Serial.print("Results: Average Before Puff: ");
  Serial.println(averageprepuff);

  Serial.print("Minimum Post-Puff Value:");
  Serial.println(minpuffval);

  Serial.print("Delta:");
  Serial.println(difference);

  Serial.print("Determination:");
  //Add high/low here

  delay(200); //button lockout, can change
  teststarted = false;

}

