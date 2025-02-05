// IGEN 430 Balance Testing with ADX345 and GY-521 (MPU6050)
// Wiring: SCL to A5, SDA to A4

// need to determine orientation
// need to determine filtering 

#include <Wire.h>


int ADXL345 = 0x53;  // ADXL345 I2C address
int MPU6050 = 0x68;  // Default MPU6050 I2C address

// Outputs for ADXL345
float X_ADX, Y_ADX, Z_ADX;
// Outputs for MPU6050
float X_MPU, Y_MPU, Z_MPU;
// Averaged values
float X_avg, Y_avg, Z_avg;
float Acceleration, OldVelocity = 0, Distance = 0;
float Filt_ADX_X = 0, Filt_ADX_Y = 0, Filt_ADX_Z = 0;
float Filt_MPU_X = 0, Filt_MPU_Y = 0, Filt_MPU_Z = 0;
float timestep_sec = 0, NormalizedAcc = 0;
float threshold = 0.0;
const float dt = 0.1;
unsigned long duration = 120000, startMillis, previousMillis = 0, timestep = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  Serial.println("CLEARDATA");
  Serial.println("LABEL,Time,X_avg,Y_avg,Z_avg,Acceleration,Distance,Velocity");
  Serial.println("RESETTIMER");

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
  unsigned long now = millis();
  if (now - startMillis >= duration) {
    Serial.println("==================================");
    Serial.println("Time limit reached. Stopping execution.");
    Serial.println("Total Distance Traveled: " + String(Distance) + " meters");
    Serial.println("==================================");
    while (true);
  }

  // Read ADXL345 Data
  Wire.beginTransmission(ADXL345);
  Wire.write(0x32);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345, 6, true);

  X_ADX = (Wire.read() | Wire.read() << 8) / 256.0;
  Y_ADX = (Wire.read() | Wire.read() << 8) / 256.0;
  Z_ADX = (Wire.read() | Wire.read() << 8) / 256.0;


  Filt_ADX_X = X_ADX-(-0.9);
  Filt_ADX_Y = Y_ADX;
  Filt_ADX_Z = Z_ADX-(-0.09);

  // Read MPU6050 Data
  Wire.beginTransmission(MPU6050);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050, 6, true);

  X_MPU = (Wire.read() << 8 | Wire.read())/ 16384.0;
  Y_MPU = (Wire.read() << 8 | Wire.read()) / 16384.0;
  Z_MPU = (Wire.read() << 8 | Wire.read())/ 16384.0;

  Filt_MPU_X = X_MPU-(-0.93);
  Filt_MPU_Y = Y_MPU-(-0.10);
  Filt_MPU_Z = Z_MPU-(0.08);


  // Compute Averaged Values
  X_avg = (Filt_ADX_X + Filt_MPU_X) / 2.0;
  Y_avg = (Filt_ADX_Y + Filt_MPU_Y) / 2.0;
  Z_avg = (Filt_ADX_Z + Filt_MPU_Z) / 2.0;

  // Compute Acceleration Magnitude
  Acceleration = sqrt((X_avg * X_avg) + (Y_avg * Y_avg) + (Z_avg * Z_avg));

  // Time Calculation
  timestep_sec = timestep / 1000.0;
  NormalizedAcc = abs(Acceleration - 1); // in g

  if (NormalizedAcc > threshold) {
    Distance += OldVelocity * timestep_sec + 0.5 * NormalizedAcc * timestep_sec * timestep_sec;
    OldVelocity = NormalizedAcc * timestep_sec;
  } else {
    OldVelocity = 0;
  }

  // Print Data
  Serial.print("x_ADX: "); Serial.print(X_ADX);
  Serial.print("y_ADX: "); Serial.print(Y_ADX);
  Serial.print("z_ADX: "); Serial.print(Z_ADX);
  Serial.print("x_MPU: "); Serial.print(X_MPU);
  Serial.print("y_MPU: "); Serial.print(Y_MPU);
  Serial.print("z_MPU: "); Serial.print(Z_MPU); 
  //Serial.print("x_ADX: "); Serial.print(Filt_ADX_X);
  //Serial.print("y_ADX: "); Serial.print(Filt_ADX_Y);
  //Serial.print("z_ADX: "); Serial.print(Filt_ADX_Z);
  //Serial.print("x_MPU: "); Serial.print(Filt_MPU_X);
  //Serial.print("y_MPU: "); Serial.print(Filt_MPU_Y);
  //Serial.print("z_MPU: "); Serial.print(Filt_MPU_Z); 
  Serial.print("X_avg: "); Serial.print(X_avg);
  Serial.print(" Y_avg: "); Serial.print(Y_avg);
  Serial.print(" Z_avg: "); Serial.print(Z_avg);
  Serial.print(" A: "); Serial.print(Acceleration);
  //Serial.print(" NA: "); Serial.print(NormalizedAcc);
  Serial.print(" D [m]: "); Serial.print(Distance);
  Serial.print(" V [m/s]: "); Serial.println(OldVelocity);

  timestep = millis() - now;
}
