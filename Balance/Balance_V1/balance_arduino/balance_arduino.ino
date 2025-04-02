// IGEN 430 Balance Testing with ADX345 and GY-521 (MPU6050)

//TODO: Replace the filtering code when Stephanie updates it (UPDATED Feb 6)

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

  Serial.println("Serial Connection Init.");

}

void loop() {
    // Wait for a start character from the Pi
    while (Serial.available() == 0 || Serial.read() != 's') {
        // Do nothing, just wait for 's' to be received
    }
    float distance = getDistance();
    Serial.println(String(distance));
}

float getDistance() {

    // Outputs for ADXL345
    float X_ADX, Y_ADX, Z_ADX;
    // Outputs for MPU6050
    float X_MPU, Y_MPU, Z_MPU;
    // Averaged values
    float X_avg, Y_avg, Z_avg;
    float Acceleration =0, OldVelocity = 0, Distance = 0;
    float Filt_ADX_X = 0, Filt_ADX_Y = 0, Filt_ADX_Z = 0;
    float Filt_MPU_X = 0, Filt_MPU_Y = 0, Filt_MPU_Z = 0;
    float Adj_MPU_X = 0, Adj_MPU_Y = 0, Adj_MPU_Z = 0;
    float timestep_sec = 0, NormalizedAcc = 0;
    float fixGravAccel = 0;
    float threshold = 0.01;
    const float dt = 0.1;

    //Duration can be modified here, it is in milliseconds
    unsigned long duration = 20000, startMillis, previousMillis = 0, timestep = 0;

    Serial.println("Starting Distance Measurement");

    startMillis = millis();
    while (true) {

        unsigned long now = millis();

        if (now - startMillis >= duration) {
            Distance = Distance * 10;
            return Distance;
            break;
        }

        // Read ADXL345 Data
        Wire.beginTransmission(ADXL345);
        Wire.write(0x32);
        Wire.endTransmission(false);
        Wire.requestFrom(ADXL345, 6, true);

        X_ADX = (Wire.read() | Wire.read() << 8) / 256.0;
        Y_ADX = (Wire.read() | Wire.read() << 8) / 256.0;
        Z_ADX = (Wire.read() | Wire.read() << 8) / 256.0;
        
        Filt_ADX_X = X_ADX-(0.10);
        Filt_ADX_Y = Y_ADX-(-0.02);
        Filt_ADX_Z = Z_ADX-(-0.04);
        
        // Read MPU6050 Data
        Wire.beginTransmission(MPU6050);
        Wire.write(0x3B);
        Wire.endTransmission(false);
        Wire.requestFrom(MPU6050, 6, true);

        X_MPU = (Wire.read() << 8 | Wire.read())/ 16384.0;
        Y_MPU = (Wire.read() << 8 | Wire.read()) / 16384.0;
        Z_MPU = (Wire.read() << 8 | Wire.read())/ 16384.0;

        Filt_MPU_X = X_MPU-(-0.08);
        Filt_MPU_Y = Y_MPU-(0.03);
        Filt_MPU_Z = Z_MPU-(0.05);

        Adj_MPU_X = Filt_MPU_X*-1;
        Adj_MPU_Y = Filt_MPU_Y;
        Adj_MPU_Z = Filt_MPU_Z*-1;

        // Compute Averaged Values
        X_avg = (Filt_ADX_X + Adj_MPU_X) / 2.0;
        Y_avg = (Filt_ADX_Y + Adj_MPU_Y) / 2.0;
        Z_avg = (Filt_ADX_Z + Adj_MPU_Z) / 2.0;

        // Compute Acceleration Magnitude
        Acceleration = sqrt((X_avg * X_avg) + (Y_avg * Y_avg) + (Z_avg * Z_avg));

        // Time Calculation
        timestep_sec = timestep / 1000.0;
        NormalizedAcc = abs(Acceleration-1); // in g
        if (NormalizedAcc > threshold) {
          fixGravAccel = NormalizedAcc*9.81;
          Distance += OldVelocity * timestep_sec + 0.5 * fixGravAccel * timestep_sec * timestep_sec;
          OldVelocity = fixGravAccel * timestep_sec;
        } else {
          OldVelocity = 0;
        }

        timestep = millis() - now;
    }
}