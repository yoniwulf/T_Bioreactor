""" import GUI_Sandbox

def setRpm():
	print("rpm set button clicked, rpm is " + str(rpmScale.get()))

def setAngle():
	print("angle set button clicked, angle is " + str(angleScale.get()))

def startPressed():
	print("Start Button pressed, RPM: " + str(rpmScale.get()) + ", Angle: " + str(angleScale.get()))

def stopPressed():
	print("Stop Button pressed, slowing down")

def eStopPressed():
	print("Emergency Stop Button pressed, shutting down all systems")
	
 """