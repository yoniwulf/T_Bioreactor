//import Serial.h

int motorSpeed;
int actuatorPosition;

void setup() {
  // Start the serial communication
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming byte
    char incomingByte = Serial.read();

    if (incomingByte == 'm') {
      // Read the next incoming byte as the motor speed
      motorSpeed = Serial.parseInt();
    } else if (incomingByte == 'a') {
      // Read the next incoming byte as the actuator position
      actuatorPosition = Serial.parseInt();
    }
  }

  // Control the motor
  analogWrite(3, motorSpeed);

  // Control the actuator
  // You will need to implement the code to move the actuator depending on the actuator you are using.
}
