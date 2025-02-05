// IGEN 430 Balance Testing with ADX345 and GY-521 (MPU6050)

//TODO: Replace the filtering code when Stephanie updates it

#include <Wire.h>


int ADXL345 = 0x53;  // ADXL345 I2C address
int MPU6050 = 0x68;  // Default MPU6050 I2C address

void setup() {
  Serial.begin(9600);
  Wire.begin();

  // Setup ADXL345
  Wire.beginTransmission(ADXL345);
  Wire.write(0x2D);
  Wire.write(8); // Enable measurement
  Wire.endTransmission();
  delay(10);

  // Setup MPU6050
  Wire.beginTransmission(MPU6050);
  Wire.write(0x6B); 
  Wire.write(0); // Wake up the MPU6050
  Wire.endTransmission();
  delay(10);

  startMillis = millis();
}

void loop() {
    // Wait for a start character from the Pi
    while (Serial.available() == 0 || Serial.read() != 'start') {
        // Do nothing, just wait for 'start' to be received
    }
    float distance == getDistance();
    Serial.println(String(distance));
}

float getDistance() {

    // Outputs for ADXL345
    float X_ADX, Y_ADX, Z_ADX;
    // Outputs for MPU6050
    float X_MPU, Y_MPU, Z_MPU;
    // Averaged values
    float X_avg, Y_avg, Z_avg;
    float Acceleration, OldVelocity = 0, Distance = 0;
    float timestep_sec = 0, NormalizedAcc = 0;
    float threshold = 0.0;
    const float dt = 0.1;

    //Duration can be modified here, it is in milliseconds
    unsigned long duration = 120000, startMillis, previousMillis = 0, timestep = 0;

    while true {

        unsigned long now = millis();

        if (now - startMillis >= duration) {
            return Distance;
        }

        // Read ADXL345 Data
        Wire.beginTransmission(ADXL345);
        Wire.write(0x32);
        Wire.endTransmission(false);
        Wire.requestFrom(ADXL345, 6, true);

        X_ADX = (Wire.read() | Wire.read() << 8) / 256.0;
        Y_ADX = (Wire.read() | Wire.read() << 8) / 256.0;
        Z_ADX = (Wire.read() | Wire.read() << 8) / 256.0;

        // Read MPU6050 Data
        Wire.beginTransmission(MPU6050);
        Wire.write(0x3B);
        Wire.endTransmission(false);
        Wire.requestFrom(MPU6050, 6, true);

        X_MPU = (Wire.read() << 8 | Wire.read())/ 16384.0;
        Y_MPU = (Wire.read() << 8 | Wire.read()) / 16384.0;
        Z_MPU = (Wire.read() << 8 | Wire.read())/ 16384.0;

        // Compute Averaged Values
        X_avg = (X_ADX + X_MPU) / 2.0;
        Y_avg = (Y_ADX + Y_MPU) / 2.0;
        Z_avg = (Z_ADX + Z_MPU) / 2.0;

        // Compute Acceleration Magnitude
        Acceleration = sqrt((X_avg * X_avg) + (Y_avg * Y_avg) + (Z_avg * Z_avg));

        // Time Calculation
        timestep_sec = timestep / 1000.0;
        NormalizedAcc = abs(Acceleration - 1); // in g

        if (NormalizedAcc > threshold) {
            Distance += OldVelocity * timestep_sec + 0.5 * NormalizedAcc * timestep_sec * timestep_sec;
            OldVelocity = NormalizedAcc * timestep_sec;
        } 
        else {
            OldVelocity = 0;
        }

        timestep = millis() - now;
    }
}