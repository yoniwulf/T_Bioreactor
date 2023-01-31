import serial

# Open a serial connection to the Arduino
ser = serial.Serial('COM3', 9600)

# Function to control the motor
def control_motor(speed):
    # Send the speed command to the Arduino
    ser.write(b'm ' + str(speed).encode())

# Function to control the linear actuator
def control_actuator(position):
    # Send the position command to the Arduino
    ser.write(b'a ' + str(position).encode())

# Example usage
control_motor(255)
control_actuator(50)
