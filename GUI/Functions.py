#---------------------#
#------Functions------#
#---------------------#

from tkinter import*
from tkinter import ttk
#from GUI_Rev1 import *


# function to update selected rpm value
def setRpm(rpmScaleIn, rpmVar):
	#global rpmVal 
	rpmVar = rpmScaleIn.get()
	print("rpm set button clicked, scale rpm is " + str(rpmScaleIn.get())
			+ " rpmVal is " + str(rpmVar))

# function to update selected angle value
def setAngle(angleScaleIn):
	global angleVal
	angleVal = angleScaleIn.get()
	print("angle set button clicked, scale angle is " + str(angleScaleIn.get())
			+ " angleVal is " + str(angleVal))

# function to send rpmVal, angleVal, and start command (needed?) to arduino
def startPressed():
	# send rpmVal and angleVal to arduino
	print("Start Button pressed, rpmVal: " + str(rpmVal) + ", angleVal: " + str(angleVal))

# function to send stop command to arduino
def stopPressed():
	global rpmVal, angleVal
	rpmVal = 0
	angleVal = 0
	print("Stop Button pressed, slowing down")

# function to send e-stop command to arduino
def eStopPressed():
	print("Emergency Stop Button pressed, shutting down all systems")
