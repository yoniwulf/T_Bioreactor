// Main Arduino file controlling the main driver/agitation motor and the linear actuator

//Includes
#include <ezButton.h>
//#include String.h

//define constants
#define MAX_USER_RPM 200
#define MIN_USER_RPM 0
#define MAX_MOTOR_RPM 2200.0 //max RPM setting in Clearpath software
#define STROKE_LENGTH 1.8161 //stroke length of linear actuator (do not change)
#define LA_SPEED 50
#define ABS_MAX_LA_READING 950
#define ABS_MIN_LA_READING 100
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
int RPMFeedback = 0;
int curSetRPM = 0;


//Linear Actuator (LA) variables
int sensorVal; //reading from sensor pin
float extensionLength; //length of extention for printing
int maxLSAnalogReading = 1000; //analog reading at max limit switch
int minLSAnalogReading = 0; //analog reading at min limit switch
int curSetAngle = 0;
int angleFeedback = 0;
double sensorValsPerDeg = 0.0;

//Other variables
String receivedData;
String feedbackData;
int strLen = 0;
int rpmData = 0;
int angleData = 0;
int opData = 0;
int feedbackCount = 0;
int runCalibration = 1;




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

  //enable AM and set direction to CW
  //digitalWrite(AM_Enable_Pin, HIGH);
  digitalWrite(AM_Dir_Pin, LOW);

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

    case calibrateLA: //Done?
      //add a popup to gui to calibrate motor so it does not do it automaticaly
      if (runCalibration == 1){
        //run through linear actuator setup: define limits, center at 45 degrees   
        //serial.println("About to move to max lim switch");
        maxLSAnalogReading = moveToLimSwitch(1);
        //serial.println("finished moving to max lim switch");
        
        //serial.println("About to move to min lim switch");
        minLSAnalogReading = moveToLimSwitch(-1);
        //Serial.println("finished moving to min lim switch");

        moveToAngle(15);
        driveActuator(0, 0);
        
        //Serial.print("maxLSAnalogReading = ");
        //Serial.println(maxLSAnalogReading);

        //Serial.print("minLSAnalogReading = ");
        //Serial.println(minLSAnalogReading);

        sensorValsPerDeg = (maxLSAnalogReading - minLSAnalogReading) / 90.0;

        //Serial.print("sensorValsPerDeg = ");
        //Serial.println(sensorValsPerDeg);
        
        curState = standby;
        runCalibration = 0;
      }

      else {
        if (Serial.available() > 0) {  // if data is available on serial port
          receivedData = Serial.readStringUntil('\n');  // read string from serial port until newline character
          strLen = receivedData.length();
          opData = receivedData.substring(receivedData.lastIndexOf(',') + 1, strLen).toInt();

          if (opData == 4){
            runCalibration = 1;
          }

          //Serial.flush();
        }
      }
      //delay(200);
    break;

    case standby:
      //check if top and bottom buttons are pressed to enter test mode state      
      if((!extendActuatorBtn.getState()) && (!decreaseRPMBtn.getState())) {
        curState = testMode;
        while((!extendActuatorBtn.getState()) && (!decreaseRPMBtn.getState())){
          extendActuatorBtn.loop();
          decreaseRPMBtn.loop();
          delay(10);
        }
        //Serial.println("Going into test mode");
      }

      //check if data has been sent to the arduino (start/stop/estop pressed)
      if (Serial.available() > 0) {  // if data is available on serial port
        receivedData = Serial.readStringUntil('\n');  // read string from serial port until newline character
        //Serial.flush();

        //get string length and split data
        strLen = receivedData.length();
        rpmData = receivedData.substring(0, receivedData.indexOf(',')).toInt();
        //rpmData = 20;
        angleData = receivedData.substring(receivedData.indexOf(',') + 1, receivedData.lastIndexOf(',')).toInt();
        opData = receivedData.substring(receivedData.lastIndexOf(',') + 1, strLen).toInt();


        switch (opData) {
          case 1: //start
            curSetRPM = rpmData;
            curSetAngle = angleData;
            //serial.print("curSetAngle: ");
            //serial.println(curSetAngle);

            curState = startPressed;
            //Serial.print("moved to startPressed");
          break;

          case 2: //stop
            curSetRPM = 0;

            curState = stopPressed;
            //Serial.print("moved to stopPressed");
          break;

          case 3: //e-stop
            curSetRPM = 0;

            curState = eStopPressed;
            //serial.print("moved to estopPresed");
          break;

          default:

          break;
        }
      }

      if (feedbackCount < 10){
        RPMFeedback += int(getRPMFromDuty(getPWMDuty()));
        //angleFeedback += angleFromSensorVal();
        feedbackCount++;
      }

      else {
        //Serial.flush();
        //RPMFeedback = int(RPMFeedback / 10.0);
        //angleFeedback = int(angleFeedback / 10.0);
        //Serial.print(RPMFeedback);
        //Serial.print(",");
        //Serial.println(angleFeedback);
        //Serial.print("\n");

        //printRPMAndDuty();

        RPMFeedback = 0;
        angleFeedback = 0;
        feedbackCount = 0;
      }

      delay(100);
    break;

    case startPressed: //Done?
      //enable AM, move to angle, set rpm
      digitalWrite(AM_Enable_Pin, HIGH);
      moveToAngle(curSetAngle);

      //delay(100);
      driveActuator(0, LA_SPEED);

      setRPM(curSetRPM);
      
      curState = standby;
    break;

    case stopPressed: //Done?
      //set AM to curSetRPM (=0), stop LA
      setRPM(curSetRPM);
      driveActuator(0, 0);

      curState = standby;
    break;

    case eStopPressed: //Done?
      //disable AM, stop LA
      digitalWrite(AM_Enable_Pin, LOW);
      driveActuator(0, 0);

      curState = standby;

      //add some kind of button to reenable functionality?
    break;

    case testMode: //Done?
      //allow control of LA and AM via buttons

      // get sensor value for LA
      sensorVal = analogRead(LA_Sensor_Pin);

      //check if top and bottom buttons are pressed to exit test mode state
      if((!extendActuatorBtn.getState()) && (!decreaseRPMBtn.getState())) {
        while((!extendActuatorBtn.getState()) && (!decreaseRPMBtn.getState())){
          extendActuatorBtn.loop();
          decreaseRPMBtn.loop();
          delay(10);
        }
        curState = standby;
      }

      //if the extend actuator button is pressed
      else if ((!extendActuatorBtn.getState()) && (sensorVal < maxLSAnalogReading)){
        driveActuator(1, LA_SPEED);
      }

      //if the retract actuator button is pressed
      else if ((!retractActuatorBtn.getState()) && (sensorVal > minLSAnalogReading)){
        driveActuator(-1, LA_SPEED);
      }

      /*
      //if no actuator button is pressed
      else {
        driveActuator(0, LA_SPEED);
      }
      */

      //if the increase RPM button is pressed
      else if((!increaseRPMBtn.getState()) & (curSetRPM <= MAX_USER_RPM - 10)) {
        curSetRPM = curSetRPM + 10;
        setRPM(curSetRPM);
        while(!increaseRPMBtn.getState()){
          increaseRPMBtn.loop();
          delay(10);
        }
      }

      //if the decrease RPM button is pressed
      else if((!decreaseRPMBtn.getState()) & (curSetRPM > MIN_USER_RPM + 1)) {
        curSetRPM = curSetRPM - 10;
        setRPM(curSetRPM);
        while(!decreaseRPMBtn.getState()){
          decreaseRPMBtn.loop();
          delay(10);
        }
      }

      //if no buttons are pressed
      else{
        driveActuator(0, LA_SPEED);
        //setRPM(curSetRPM); //needed?
      }


      //delay(10);
    break;

    default:

    break;

  }

  /*  
  RPMFeedback = int(getRPMFromDuty(getPWMDuty()));
  angleFeedback = angleFromSensorVal();
  Serial.print(RPMFeedback);
  Serial.print(",");
  Serial.println(angleFeedback);
  */

  /*
  if (feedbackCount < 10){
    RPMFeedback += int(getRPMFromDuty(getPWMDuty()));
    angleFeedback += angleFromSensorVal();
    feedbackCount++;
  }

  else {
    //Serial.flush();
    RPMFeedback = int(RPMFeedback / 10.0);
    angleFeedback = int(angleFeedback / 10.0);
    Serial.print(RPMFeedback);
    Serial.print(",");
    Serial.println(angleFeedback);
    //Serial.print("\n");

    printRPMAndDuty();

    RPMFeedback = 0;
    angleFeedback = 0;
    feedbackCount = 0;
  }
  */

  
  

  
  
  
  //Serial.print("sensorVal: ");
  //Serial.println(sensorVal);

  //Serial.print("angleFeedback: ");
  //Serial.println(angleFeedback);
  //delay(10);
}


//Agitation motor functions

//function to send a duty cycle value to AM via analogWrite
void setRPM(int RPM){
  if(RPM >= MIN_USER_RPM && RPM <= MAX_USER_RPM) {
    int RPMset = RPM * (255.0 / (MAX_MOTOR_RPM/10.0));
    //int RPMset = round(RPM*RPMPerPWM);
    //serial.println(RPMset);
    analogWrite(AM_PWM_Input_Pin, RPMset);
  }
}

//function to get the PWM duty cycle percentage from AM feedback pulses
double getPWMDuty(){

  noInterrupts();
  PWM_TOn = pulseIn(AM_Feedback_Pin, HIGH);
  interrupts();
  Serial.print("PWM_TOn: ");
  Serial.print(PWM_TOn);
  delay(200);
  /*
  PWM_TOff = pulseIn(AM_Feedback_Pin, LOW);
  Serial.print(" PWM_TOff: ");
  Serial.println(PWM_TOff);
  PWM_Tot = PWM_TOn + PWM_TOff;
  if(PWM_Tot > 2000.0){
    PWM_Duty = (PWM_TOff/PWM_Tot)*100.0;
  }
  */
  delay(200);
  PWM_Duty = (PWM_TOn/2050.0)*100.0;

  //Serial.print("PWM_Tot: ");
  //Serial.print(PWM_Tot);
  Serial.print(" PWM_Duty: ");
  Serial.println(PWM_Duty);

  return PWM_Duty;
}

//function to convert PWM duty cycle percentage into RPM
double getRPMFromDuty(double Duty){
  double tempRPM = floor(Duty * (MAX_MOTOR_RPM/1000.0));

  Serial.print("tempRPM: ");
  Serial.println(tempRPM);
  return tempRPM;
}

//function to print out RPM and duty cycle percentage
void printRPMAndDuty(){
  double pDuty = getPWMDuty();
  double pRPM = getRPMFromDuty(pDuty);
  Serial.print("RPM: ");
  Serial.print(pRPM);
  Serial.print("  Duty Cycle %: ");
  Serial.println(pDuty);
}

//Linear actuator functions//

// function to move in "Direction" until the corresponding limit switch is triggered then return sensor val
int moveToLimSwitch(int Direction){
  maxLimSwitch.loop();
  minLimSwitch.loop();
  //serial.println("got into func");
  //get states of limit switches
  int maxSwitchState = maxLimSwitch.getState();
  int minSwitchState = minLimSwitch.getState();
  
  //serial.println("got past lim switch states");
  //set current reading value
  sensorVal = analogRead(LA_Sensor_Pin);
  //serial.print("Analog Reading: ");
  //serial.println(sensorVal);

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

  //serial.println("got past backoffs");

  //set current reading value
  sensorVal = analogRead(LA_Sensor_Pin);

  //serial.println("got past second reading");
  
  // if extending
  if (Direction == 1){
    //serial.println("got into direction = 1");
    //serial.println("max switch state = " + maxSwitchState);
    while((sensorVal < ABS_MAX_LA_READING) && (maxSwitchState == 1)) {
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
        driveActuator(0, LA_SPEED);
        //serial.print("Max Limit Switch Pressed,  Analog Reading: ");
        //serial.println(sensorVal);
      }
      //*/
    }

    
  }

  else if (Direction == -1) {
    while((sensorVal > ABS_MIN_LA_READING) && (minSwitchState == 1)) {
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
        driveActuator(0, LA_SPEED);
        //serial.print("Min Limit Switch Pressed,  Analog Reading: ");
        //serial.println(sensorVal);
      }
      //*/
    }
  }
  return sensorVal;
}

//function to extend or retract actuator based on a passed in direction and speed
void driveActuator(int Direction, int speed){
  sensorVal = analogRead(LA_Sensor_Pin);
  //if ((sensorVal < maxLSAnalogReading) && (sensorVal > minLSAnalogReading)) {
    switch(Direction){
      case 1:       //extension
        //if(sensorVal < maxLSAnalogReading){
          analogWrite(LA_RPWM_Pin, speed);
          analogWrite(LA_LPWM_Pin, 0);
        //}
        
        break;
    
      case 0:       //stopping
        analogWrite(LA_RPWM_Pin, 0);
        analogWrite(LA_LPWM_Pin, 0);
        break;

      case -1:      //retraction
        //if(sensorVal > minLSAnalogReading){
          analogWrite(LA_RPWM_Pin, 0);
          analogWrite(LA_LPWM_Pin, speed);
        //}
        
        break;
    }
  //}
}

//function to move the linear actuator to the given/desired sensor reading
void moveToSensorVal(int reading){
  double tolerance = 0.5;
  int safeReading = 0;

  //if the desired reading is outside of the safe range
  if (reading > maxLSAnalogReading) {
    //Serial.println("desired sensor reading is too high, setting to max reading");
    safeReading = maxLSAnalogReading;
  }

  else if(reading < minLSAnalogReading) {
    //Serial.println("desired sensor reading is too low, setting to min reading");
    safeReading = minLSAnalogReading;
  }

  else {
    safeReading = reading;
  }

  
  sensorVal = analogRead(LA_Sensor_Pin);

  //while the sensor value is not within the range of the desired reading +- the tolerance
  while ((sensorVal < (safeReading - tolerance)) || (sensorVal > (safeReading + tolerance))){

    //extend
    if (sensorVal < safeReading){
      driveActuator(1, LA_SPEED);
    }

    //retract
    else{
      driveActuator(-1, LA_SPEED);
    }

    //read sensor value
    sensorVal = analogRead(LA_Sensor_Pin);
  }
  //serial.println("at desired sensor reading");
  
}

//function to move the linear actuator to the given/desired angle
void moveToAngle(int Angle){
  double vertDist = 0.0;
  int readingFromTop = 0;
  
  //simple 1:1 conversion just for testing
  readingFromTop = minLSAnalogReading + (((maxLSAnalogReading - minLSAnalogReading) / 90.0) * Angle);
  //serial.println("Reading from top: ");
  //serial.println(readingFromTop);


  //convert angle into vertical location of pin
    //somthing along the lines of:vertDist = 0.375*sin(Angle - 45)
  
  //convert vertDist (inches) into analog reading and add to minLSAnalogReading
  //readingFromTop = round(minLSAnalogReading + (vertDist * ANALOG_READING_PER_IN));

  //call move to sensor val function
  moveToSensorVal(readingFromTop);
}

//function to turn sensorVal into an angle
int angleFromSensorVal(){
  sensorVal = analogRead(LA_Sensor_Pin);

  int sensorSum = 0;
  double numReadings = 5;

  for (int i = 0; i < int(numReadings); i++){
    sensorSum += analogRead(LA_Sensor_Pin);
    delay(1);
  }

  int avgSensorVal = round(sensorSum / numReadings);

  //Serial.print("avgSensorVal: ");
  //Serial.println(avgSensorVal);



  //simple 1:1 conversion for testing
  //int realAngle = 105 - ((maxLSAnalogReading - sensorVal) / ((maxLSAnalogReading - minLSAnalogReading) / 90));
  int realAngle = round((avgSensorVal - minLSAnalogReading) / sensorValsPerDeg);


  //Serial.print("realAngle: ");
  //Serial.println(realAngle);
 
  
  return realAngle;
}










