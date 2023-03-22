// Main Arduino file controlling the main driver/agitation motor and the linear actuator

//Includes
#include <ezButton.h>

//define constants
#define MAX_USER_RPM 200
#define MIN_USER_RPM 0
#define MAX_MOTOR_RPM 2200.0 //max RPM setting in Clearpath software
#define STROKE_LENGTH 1.8161 //stroke length of linear actuator (do not change)
#define LA_SPEED 100
#define ABS_MAX_LA_READING 1000
#define ABS_MIN_LA_READING 1000
#define IN_PER_ANALOG_READING 0.00211174
#define ANALOG_READING_PER_IN 473.5422
#define TEST_MODE False


//Set pins
#define AM_Feedback_Pin 5
#define AM_PWM_Input_Pin 4
#define AM_Dir_Pin 35
#define AM_Enable_Pin 37
#define LA_RPWM_Pin 3
#define LA_LPWM_Pin 2
#define LA_Sensor_Pin A8
#define LS_Max_Pin 43
#define LS_Min_Pin 45
#define RC_Button1_Pin 53
#define RC_Button2_Pin 51
#define RC_Button3_Pin 49
#define RC_Button4_Pin 47


//define limit switch buttons
ezButton maxLimSwitch(LS_Max_Pin);
ezButton minLimSwitch(LS_Min_Pin);

//define remote control buttons
ezButton extendActuatorBtn(RC_Button1_Pin);
ezButton retractActuatorBtn(RC_Button2_Pin);
ezButton increaseRPMBtn(RC_Button3_Pin);
ezButton decreaseRPMBtn(RC_Button4_Pin);


//define states
enum states {calibrateLA, standby, startPressed, stopPressed, eStopPressed, changeRPM, changeAngle, testMode};
states curState = calibrateLA;


//Agitation Motor (AM) variables
double PWM_TOn, PWM_TOff, PWM_Tot, PWM_Duty; //used to produce PWM output to AM
double RPMPerPWM = 0.0; //calculated value of RPM for each percentage PWM
int RPMOut = 0;
int curSetRPM = 0;


//Linear Actuator (LA) variables
int sensorVal; //reading from sensor pin
float extensionLength; //length of extention for printing
int maxLSAnalogReading; //analog reading at max limit switch
int minLSAnalogReading; //analog reading at min limit switch




void setup() {
  //begin serial communication
  Serial.begin(9600);

  //AM pin input/output
  pinMode(AM_Feedback_Pin, INPUT_PULLUP);
  pinMode(AM_PWM_Input_Pin, OUTPUT);
  pinMode(AM_Dir_Pin, OUTPUT);
  pinMode(AM_Enable_Pin, OUTPUT);

  //LA pin input/output
  pinMode(LA_RPWM_Pin, OUTPUT); 
  pinMode(LA_LPWM_Pin, OUTPUT);
  pinMode(LA_Sensor_Pin, INPUT); 

  //set debounce values for limit switches and buttons
  maxLimSwitch.setDebounceTime(50);
  minLimSwitch.setDebounceTime(50);
  extendActuatorBtn.setDebounceTime(50);
  retractActuatorBtn.setDebounceTime(50);
  increaseRPMBtn.setDebounceTime(50);
  decreaseRPMBtn.setDebounceTime(50);

}

void loop() {
  //initialize buttons
  maxLimSwitch.loop();
  minLimSwitch.loop();
  extendActuatorBtn.loop();
  retractActuatorBtn.loop();
  increaseRPMBtn.loop();
  decreaseRPMBtn.loop();
  
  
  
  //main state machine switch
  switch (curState) {

    case calibrateLA: 
      //run through linear actuator setup: define limits, center at 45 degrees   //Done?//
      
      maxLSAnalogReading = moveToLimSwitch(1);
      minLSAnalogReading = moveToLimSwitch(-1);
      driveActuator(0, 0);
      
      curState = standby;
            
    break;

    case standby:
      //wait for signal (change in signal?) from RPi, calculate and send current angle and rpm to RPi


      //check if top and bottom buttons are pressed to enter test mode state      
      if((!extendActuatorBtn.getState()) && (!decreaseRPMBtn.getState())) {
        curState = testMode;
        while((!extendActuatorBtn.getState()) && (!decreaseRPMBtn.getState())){
          extendActuatorBtn.loop();
          decreaseRPMBtn.loop();
          delay(20);
        }
      }

    break;

    case startPressed:
      //check current angle and rpm, then move to change RPM

    break;

    case stopPressed: 
      //move to change rpm with a value of 0
      
      driveActuator(0, 0);
      //set motor rpm and rpm variable to 0

    break;

    case eStopPressed:
      //disable motor, reset rpm to 0
      driveActuator(0, 0);

    break;

    case changeRPM:
      //calculate pwm signal and send to motor 

    break;

    case changeAngle:
      //calculate angle and send to actuator 

    break;

    case testMode: 
      //allow control of LA and AM via buttons

      // get sensor value for LA
      sensorVal = analogRead(sensorPin);

      //if the extend actuator button is pressed
      if ((!extendActuatorBtn.getState()) && (sensorVal < maxLSAnalogReading)){
        driveActuator(1, LA_SPEED);
      }

      //if the retract actuator button is pressed
      else if ((!retractActuatorBtn.getState()) && (sensorVal > minLSAnalogReading)){
        driveActuator(-1, LA_SPEED);
      }

      else {
        driveActuator(0, LA_SPEED);
      }

      //insert code to increase/decrease rpm


      //check if top and bottom buttons are pressed to exit test mode state
      if((!extendActuatorBtn.getState()) && (!decreaseRPMBtn.getState())) {
        curState = standby;
        
        while((!extendActuatorBtn.getState()) && (!decreaseRPMBtn.getState())){
          extendActuatorBtn.loop();
          decreaseRPMBtn.loop();
          delay(20);
        }
      }

    break;

    default:

    break;
  }

}


//Agitation motor functions


//Linear actuator functions//

// function to move in "Direction" until the corresponding limit switch is triggered then return sensor val
int moveToLimSwitch(int Direction){
  //get states of limit switches
  int maxSwitchState = maxLimSwitch.getState();
  int minSwitchState = minLimSwitch.getState();
  
  //set current reading value
  sensorVal = analogRead(LA_Sensor_Pin);

  //backoff if at ABS_MAX_LA_READING
  if (sensorVal >= ABS_MAX_LA_READING) {
    for (int i = 0; i < 10; i++){
      driveActuator(-1, LA_SPEED);
      delay(100);
    }
  }

  //backoff if at ABS_MIN_LA_READING
  else if (sensorVal <= ABS_MIN_LA_READING) {
    for (int i = 0; i < 10; i++){
      driveActuator(1, LA_SPEED);
      delay(100);
    }
  }
  
  // if extending
  else if (Direction == 1){
    while((sensorVal < ABS_MAX_LA_READING) & (maxSwitchState == 1)) {
      maxLimSwitch.loop();
      minLimSwitch.loop();

      //extend actuator
      driveActuator(1, LA_SPEED);
      
      //wait 100ms
      delay(100);

      //read sensor val
      sensorVal = analogRead(LA_Sensor_Pin);
      //Serial.print("Analog Reading: ");
      //Serial.println(sensorVal);

      //get switch state
      maxSwitchState = maxLimSwitch.getState();
      //Serial.print("maxLimSwitch status:  ");
      //Serial.println(maxSwitchState);

      ///* for testing
      if(maxSwitchState == 0){
        Serial.print("Max Limit Switch Pressed,  Analog Reading: ");
        Serial.println(sensorVal);
      }
      //*/
    }

    
  }

  else {
    while((sensorVal > ABS_MIN_LA_READING) & (minSwitchState == 1)) {
      maxLimSwitch.loop();
      minLimSwitch.loop();

      //retract actuator
      driveActuator(-1, LA_SPEED);
      
      //wait 200ms
      delay(100);

      //read sensor val
      sensorVal = analogRead(LA_Sensor_Pin);
      //Serial.print("Analog Reading: ");
      //Serial.println(sensorVal);

      //get switch state
      minSwitchState = minLimSwitch.getState();
      //Serial.print("minLimSwitch status:  ");
      //Serial.println(minSwitchState);

      ///*
      if(minSwitchState == 0){
        Serial.print("Min Limit Switch Pressed,  Analog Reading: ");
        Serial.println(sensorVal);
      }
      //*/
    }
  }
  return sensorVal;
}

//function to extend or retract actuator based on a passed in direction and speed
void driveActuator(int Direction, int speed){
  switch(Direction){
    case 1:       //extension
      analogWrite(LA_RPWM_Pin, speed);
      analogWrite(LA_LPWM_Pin, 0);
      break;
   
    case 0:       //stopping
      analogWrite(LA_RPWM_Pin, 0);
      analogWrite(LA_LPWM_Pin, 0);
      break;

    case -1:      //retraction
      analogWrite(LA_RPWM_Pin, 0);
      analogWrite(LA_LPWM_Pin, speed);
      break;
  }
}

//function to move the linear actuator to the given/desired sensor reading
void moveToSensorVal(int reading){
  int tolerance = 2;

  //if the desired reading is outside of the safe range
  if ((reading >= maxLSAnalogReading) || (reading <= minLSAnalogReading)) {
    Serial.println("desired sensor reading is out of safe range");
  }

  else{
    //while the sensor value is not within the range of the desired reading +- the tolerance
    while ((sensorVal < (reading - tolerance)) || (sensorVal > (reading + tolerance))){
  
      //extend
      if (sensorVal < reading){
        driveActuator(1, LA_SPEED);
      }

      //retract
      else{
        driveActuator(-1, LA_SPEED);
      }

      //read sensor value
      sensorVal = analogRead(LA_Sensor_Pin);
    }
    Serial.println("at desired sensor reading");
  }
}

//function to move the linear actuator to the given/desired angle
void moveToAngle(int Angle){
  double vertDist = 0.0;
  int readingFromTop = 0;
  
  //simple 1:1 conversion just for testing
  readingFromTop = minLSAnalogReading + (((maxLSAnalogReading - minLSAnalogReading) / 90) * Angle);


  //convert angle into vertical location of pin
    //somthing along the lines of:vertDist = 0.375*sin(Angle +- 45?)
  
  //convert vertDist (inches) into analog reading and add to minLSAnalogReading
  //readingFromTop = round(minLSAnalogReading + (vertDist * ANALOG_READING_PER_IN));

  //call move to sensor val function
  moveToSensorVal(readingFromTop);
}

