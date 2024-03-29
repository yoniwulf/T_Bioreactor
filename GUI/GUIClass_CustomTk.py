"""
Title: GUIClass_CustomTK.py
Author: Jonathan Wulf
Description: This file contains the GUIClass definition and code. This class is responsable for setting up a GUI window to provide control of the T-bioreactor.
"""
#!/usr/bin/env python

# Imports
from tkinter import*
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkdial import*
from MixingProfileClass import *
import pandas as pd
import customtkinter
import openpyxl
import serial
import copy
import threading
import time

# Constants 
SSEButtonHeight = 107
SSEButtonWidth = 107
SSEButtonTextSize = 24
plusMinButtonWidth = 50
plusMinTextSize = 18
curProfTextSize = 20
LocalTest = True

# region NOTES/IDEAS
""" 

"""
# endregion

class GUIClass:
	#----------------------------#
	#------Setup GUI Window------#
	#----------------------------#
	def __init__(self, master, serialCon):
		# setup class basics
		self.master = master
		customtkinter.set_appearance_mode("light")
		master.title("T-BioReactor Controls")

		# declare tabView to allow different tabs
		self.tabView = customtkinter.CTkTabview(self.master, width=780)

		#declare manual and automatic control tabs, add to tabView
		self.manControlTab = customtkinter.CTkFrame(self.tabView)
		self.autoControlTab = customtkinter.CTkFrame(self.tabView)
		self.tabView.add("Manual Control")
		self.tabView.add("Automatic Control")
		self.tabView.pack(expand= TRUE)

		# general variables
		self.rpmVal = 0 #set rpm value
		self.angleVal = 15 #set angle value

		# manual control variables
		self.rpmEntryText = StringVar() #stringVar for rpm displayed in self.rpmEntry widget
		self.angleEntryText = StringVar() #stringVar for angle displayed in self.angleEntry widget
		self.rpmDialVal = 0 #actual rpm value (can be set for testing)
		self.angleDialVal = 15 #actual angle value (can be set for testing)
		self.rpmSetText = StringVar() #stringVar for text in rpm "SET" button
		self.angleSetText = StringVar() #stringVar for text in angle "SET" button
		self.manRunning = False

		# automatic control variables
		self.profileList = [] #list for mixing profiles
		self.curProfIndex = 0 #index of current mixing profile
		self.numProfs = 0 #number of profiles
		self.curProfRPMText = StringVar() #stringVar for current profile rpm
		self.curProfAngleText = StringVar() #stringVar for current profile angle
		self.curProfTimeText = StringVar() #stringVar for current profile total time
		self.curProfTimeLeftText = StringVar() #stringVar for current profile time left
		self.curProfile = MixProfile(0,0,0,0,0)
		self.autoRunning = False

		# timer variables
		self.startTime = None
		self.timerLength = None
		self.stopTime = None

		#set StringVars
		self.curProfRPMText.set("0")
		self.curProfAngleText.set("0")
		self.curProfTimeText.set("00:00:00")
		self.curProfTimeLeftText.set("00:00:00")
		self.rpmEntryText.set("0")
		self.angleEntryText.set("15")
		self.rpmSetText.set("SET")
		self.angleSetText.set("SET")
		
		#open serial communication port
		if LocalTest:
			try:
				self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)
		
			except serial.serialutil.SerialException:
				print("no serial connection")
		
		else:
			try:
				self.ser = serialCon
			except:
				print("no serial connection")


		#------------------------------#
		#------Manual Control Tab------#
		#------------------------------#

		# region MANUAL CONTROL TAB
		
		#------RPM Control------#

		#RPM control section frame
		self.rpmFrame = customtkinter.CTkFrame(self.tabView.tab("Manual Control"), 
					 							fg_color= "transparent")
		self.rpmFrame.pack(side= LEFT, fill= 'both', expand= True)

		#RPM control section label
		self.rpmLabel = customtkinter.CTkLabel(self.rpmFrame, 
					 							text= "RPM", 
												font= ('Arial', 24, 'bold'))
		self.rpmLabel.pack(pady= 2)

		#RPM dial
		self.rpmDial = Meter(self.rpmFrame, 
								start= 0, 
								end= 200, 
								major_divisions= 20, 
								minor_divisions= 5,
								radius= 190,
								border_width= 0,
								start_angle= 205,
								end_angle= -230,
								text_font= ('Arial', 14, 'bold'),
								text= " RPM",
								scroll= False,
								bg= "#DBDBDB")
		self.rpmDial.pack(pady= 4)
		self.rpmDial.set(self.rpmDialVal)

		#rpm entry box label
		self.rpmEntryLabel = customtkinter.CTkLabel(self.rpmFrame, 
					      							text= "Set RPM:", 
													font= ('Arial', 18))
		self.rpmEntryLabel.pack()

		#rpm entry frame
		self.rpmEntryFrame = customtkinter.CTkFrame(self.rpmFrame, 
					      							fg_color= "transparent")
		self.rpmEntryFrame.pack()

		#rpm -10 button
		self.rpmDecButton = customtkinter.CTkButton(self.rpmEntryFrame, 
													text= "-10",
													font= ('Arial', plusMinTextSize, 'bold'),
													command= self.decRpmEntry,
													width= plusMinButtonWidth,
													border_spacing= 4)
		self.rpmDecButton.pack(side= LEFT, padx= 5)

		#rpm entry box
		self.rpmEntry = customtkinter.CTkEntry(self.rpmEntryFrame, 
												font= ('Arial', 20), 
												width= 80,
												height= 30,
												textvariable= self.rpmEntryText,
												justify= CENTER)
		self.rpmEntry.pack(side= LEFT)

		#rpm +10 button
		self.rpmIncButton = customtkinter.CTkButton(self.rpmEntryFrame, 
													text= "+10",
													font= ('Arial', plusMinTextSize, 'bold'),
													command= self.incRpmEntry,
													width= plusMinButtonWidth,
													border_spacing= 4)
		self.rpmIncButton.pack(side= LEFT, padx= 5)

		#RPM set button
		self.rpmSetButton = customtkinter.CTkButton(self.rpmFrame,
													width= 190,
													height= 40,
													textvariable= self.rpmSetText,
													font= ('Arial', 18, 'bold'),
													command= self.setRpm,
													border_width= 2,
													fg_color= 'green')
		self.rpmSetButton.pack(pady= 6)


		#------Angle Control------#

		#angle control section frame
		self.angleFrame = customtkinter.CTkFrame(self.tabView.tab("Manual Control"), 
					   								fg_color= "transparent")
		self.angleFrame.pack(side= LEFT, fill= 'both', expand= True)

		#angle control section label
		self.angleLabel = customtkinter.CTkLabel(self.angleFrame, 
													text= "ANGLE", 
													font= ('Arial', 24, 'bold'), 
													width= 7)
		self.angleLabel.pack(pady= 2)

		#angle dial
		self.angleDial = Meter(self.angleFrame, 
								start= 0, 
								end= 90, 
								major_divisions= 15, 
								minor_divisions= 5,
								radius= 190,
								border_width= 0,
								start_angle= 0,
								end_angle= 90,
								text= " Degrees",
								text_font= ('Arial', 14, 'bold'),
								bg= "#DBDBDB",
								scroll= False)
		self.angleDial.pack(pady= 4)
		self.angleDial.set(self.angleDialVal)

		#angle entry box label
		self.angleEntryLabel = customtkinter.CTkLabel(self.angleFrame, 
														text= "Set Angle:", 
														font= ('Arial', 18))
		self.angleEntryLabel.pack()

		#angle entry frame
		self.angleEntryFrame = customtkinter.CTkFrame(self.angleFrame, 
														fg_color= "transparent")
		self.angleEntryFrame.pack()

		#angle -15 button
		self.angleDecButton = customtkinter.CTkButton(self.angleEntryFrame, 
														text= "-15",
														font= ('Arial', plusMinTextSize, 'bold'),
														command= self.decAngleEntry,
														width= plusMinButtonWidth,
														border_spacing= 4)
		self.angleDecButton.pack(side= LEFT, padx= 5)

		#angle entry box
		self.angleEntry = customtkinter.CTkEntry(self.angleEntryFrame, 
													font= ('Arial', 20), 
													width= 80,
													height= 30,
													textvariable= self.angleEntryText,
													justify= CENTER)
		self.angleEntry.pack(side= LEFT)

		#angle +15 button
		self.angleIncButton = customtkinter.CTkButton(self.angleEntryFrame, 
														text= "+15",
														font= ('Arial', plusMinTextSize, 'bold'),
														command= self.incAngleEntry,
														width= plusMinButtonWidth,
														border_spacing= 4)
		self.angleIncButton.pack(side= LEFT, padx= 5)

		#Angle set button
		self.angleSetButton = customtkinter.CTkButton(self.angleFrame, 
														width= 190,
														height= 40,
														textvariable= self.angleSetText,
														font= ('Arial', 18, 'bold'),
														command= self.setAngle,
														border_width= 2,
														fg_color= 'green')
		self.angleSetButton.pack(pady= 6)


		#------Start/Stop Control------#

		#Start/stop frame
		self.manStartStopFrame = customtkinter.CTkFrame(self.tabView.tab("Manual Control"), 
						  								fg_color= "transparent")
		self.manStartStopFrame.pack(side= LEFT, fill= 'both', expand= True)

		#Start button
		self.manStartButton = customtkinter.CTkButton(self.manStartStopFrame, 
														width= SSEButtonWidth,
														height= SSEButtonHeight,
														fg_color= 'green',
														text= "START", 
														font= ('Arial', SSEButtonTextSize, 'bold'),
														text_color= "Black",
														command= lambda: self.startPressed(True),
														border_width= 2)
		self.manStartButton.pack(pady= 4)

		#Stop button
		self.manStopButton = customtkinter.CTkButton(self.manStartStopFrame, 
														width= SSEButtonWidth,
														height= SSEButtonHeight,
														fg_color= 'red',
														text= "STOP",
														font= ('Arial', SSEButtonTextSize, 'bold'),
														text_color= "Black",
														command= lambda: self.stopPressed(True),
														border_width= 2)
		self.manStopButton.pack(pady= 4)


		#E-stop button
		self.manEStopButton = customtkinter.CTkButton(self.manStartStopFrame, 
														width= SSEButtonWidth,
														height= SSEButtonHeight,
														fg_color= 'yellow',
														text= "E-STOP", 
														font= ('Arial', SSEButtonTextSize, 'bold'),
														text_color= "Black",
														command= lambda: self.eStopPressed(True),
														border_width= 2)
		self.manEStopButton.pack(pady= 4)

		# endregion

		#----------------------------------#
		#------Automation Control Tab------#
		#----------------------------------#

		# region AUTOMATION CONTROL TAB
		

		#------All Profiles display------#

		#all profiles frame
		self.autoAllProfFrame = customtkinter.CTkFrame(self.tabView.tab("Automatic Control"),
						 								fg_color= "transparent")
		self.autoAllProfFrame.pack(side= LEFT, fill= 'both', expand= True)

		#all profiles Label
		self.allProfLabel = customtkinter.CTkLabel(self.autoAllProfFrame, 
					     							text= "All Profiles", 
													font= ('Arial', 24, 'bold'))
		self.allProfLabel.pack(pady= 5)

		#all profiles list box columns Label
		self.allProfColLabel = customtkinter.CTkLabel(self.autoAllProfFrame, 
														text= "RPM         Angle             Time     ", 
														font= ('Arial', 16, 'bold'))
		self.allProfColLabel.pack(pady= 2)

		#all profiles list box
		self.allProfListBox = Listbox(self.autoAllProfFrame, 
										height= 8, 
										width= 20, 
										font= ('Arial', 16),
										activestyle= 'dotbox',
										selectbackground= 'green',
										highlightthickness= 3,
										selectmode= SINGLE)
		self.allProfListBox.pack()

		#import and clear all frame
		self.importClearFrame = customtkinter.CTkFrame(self.autoAllProfFrame,
						 								fg_color= "transparent")
		self.importClearFrame.pack(pady= 10)

		#import profiles button
		self.importProfButton = customtkinter.CTkButton(self.importClearFrame, 
														text= "Import",
														font= ('Arial', 16, 'bold'),
														width= 100,
														height= 30, 
														command= self.importPressed)
		self.importProfButton.pack(side= LEFT, padx= 12)

		#clear profiles button
		self.clearProfButton = customtkinter.CTkButton(self.importClearFrame, 
														text= "Clear All", 
														font= ('Arial', 16, 'bold'),
														height= 30,
														width= 100,
														command= self.clearAllPressed)
		self.clearProfButton.pack(side= RIGHT, padx= 12)


		#------Current Profile display------#

		#current profile frame
		self.autoCurProfFrame = customtkinter.CTkFrame(self.tabView.tab("Automatic Control"),
						 								fg_color= "transparent")
		self.autoCurProfFrame.pack(side= LEFT, fill= 'both', expand= False)

		#current profile Label
		self.curProfLabel = customtkinter.CTkLabel(self.autoCurProfFrame, 
					     							text= "Current Profile", 
													font= ('Arial', 24, 'bold'))
		self.curProfLabel.pack(pady= 6)

		#current profile RPM frame
		self.curProfRPMFrame = customtkinter.CTkFrame(self.autoCurProfFrame,
														fg_color= "transparent")
		self.curProfRPMFrame.pack(fill= 'x', pady= 3)

		#current profile RPM label
		self.curProfRPMLabel = customtkinter.CTkLabel(self.curProfRPMFrame, 
														text= "RPM:", 
														font= ('Arial', curProfTextSize + 2, 'bold'), 
														justify= 'left')
		self.curProfRPMLabel.pack(side= LEFT)

		#current profile RPM message
		self.curProfRPMMes = Message(self.curProfRPMFrame, 
										textvariable= self.curProfRPMText,
										justify= 'right',
										font= ('Arial', curProfTextSize),
										bg= "#DBDBDB")
		self.curProfRPMMes.pack(side= RIGHT)

		#current profile Angle frame
		self.curProfAngleFrame = customtkinter.CTkFrame(self.autoCurProfFrame,
						  								fg_color= "transparent")
		self.curProfAngleFrame.pack(fill= 'x', pady= 3)

		#current profile Angle label
		self.curProfAngleLabel = customtkinter.CTkLabel(self.curProfAngleFrame, 
														text= "Angle:", 
														font= ('Arial', curProfTextSize + 2, 'bold'), 
														justify= 'left')
		self.curProfAngleLabel.pack(side= LEFT)

		#current profile Angle message
		self.curProfAngleMes = Message(self.curProfAngleFrame, 
										textvariable= self.curProfAngleText,
										justify= 'right',
										font= ('Arial', curProfTextSize),
										bg= "#DBDBDB")
		self.curProfAngleMes.pack(side= RIGHT)

		#current profile Time frame
		self.curProfTimeFrame = customtkinter.CTkFrame(self.autoCurProfFrame,
						 								fg_color= "transparent")
		self.curProfTimeFrame.pack(fill= 'x', pady= 3)

		#current profile Time label
		self.curProfTimeLabel = customtkinter.CTkLabel(self.curProfTimeFrame, 
														text= "Time:", 
														font= ('Arial', curProfTextSize + 2, 'bold'), 
														justify= 'left')
		self.curProfTimeLabel.pack(side= LEFT)

		#current profile Time message
		self.curProfTimeMes = Message(self.curProfTimeFrame, 
										textvariable= self.curProfTimeText,
										justify= 'right',
										font= ('Arial', curProfTextSize),
										width= 120,
										bg= "#DBDBDB")
		self.curProfTimeMes.pack(side= RIGHT)

		#current profile Time left frame
		self.curProfTimeLeftFrame = customtkinter.CTkFrame(self.autoCurProfFrame,
						     								fg_color= "transparent")
		self.curProfTimeLeftFrame.pack(fill= 'x', pady= 3)

		#current profile Time left label
		self.curProfTimeLeftLabel = customtkinter.CTkLabel(self.curProfTimeLeftFrame, 
															text= "Remaining:", 
															font= ('Arial', curProfTextSize + 2, 'bold'), 
															justify= 'left')
		self.curProfTimeLeftLabel.pack(side= LEFT)

		#current profile Time left message
		self.curProfTimeLeftMes = Message(self.curProfTimeLeftFrame, 
											textvariable= self.curProfTimeLeftText,
											justify= 'right',
											font= ('Arial', curProfTextSize),
											width= 120,
											bg= "#DBDBDB")
		self.curProfTimeLeftMes.pack(side= RIGHT)


		#create frame for next/prev profile options
		self.profNexPrevFrame1 = customtkinter.CTkFrame(self.autoCurProfFrame,
						  								fg_color= "transparent")
		self.profNexPrevFrame1.pack(pady= 5)

		#create previous profile button
		self.prevProfButton = customtkinter.CTkButton(self.profNexPrevFrame1, 
														text= "PREV",
														font= ('arial', 16, 'bold') ,
														width= 100,
														height= 30,
														command= self.prevProf)
		self.prevProfButton.pack(side= LEFT, padx= 12, pady= 5)

		#create next profile button
		self.nextProfButton = customtkinter.CTkButton(self.profNexPrevFrame1, 
														text= "NEXT",
														font= ('arial', 16, 'bold') ,
														width= 100,
														height= 30,
														command= self.nextProf)
		self.nextProfButton.pack(side= LEFT, padx= 12, pady= 5)

		#create frame for restart profile
		self.profRestFrame = customtkinter.CTkFrame(self.autoCurProfFrame,
					      							fg_color= "transparent")
		self.profRestFrame.pack(pady= 1)

		#create restart profile button
		self.restartProfButton = customtkinter.CTkButton(self.profRestFrame, 
						   									text= "RESTART",
															font= ('arial', 16, 'bold') , 
															width= 225,
															height= 30,
															command= self.restartProf)
		self.restartProfButton.pack(pady= 3)


		#------Start/Stop Control------#

		self.autoStartStopFrame = customtkinter.CTkFrame(self.tabView.tab("Automatic Control"),
						   									fg_color= "transparent")
		self.autoStartStopFrame.pack(side= RIGHT, fill= 'both', expand= True)

		#Start button
		self.autoStartButton = customtkinter.CTkButton(self.autoStartStopFrame, 
														width= SSEButtonWidth,
														height= SSEButtonHeight,
														fg_color= 'green',
														text= "START", 
														font= ('Arial', SSEButtonTextSize, 'bold'),
														text_color= "Black",
														command= lambda: self.startPressed(False),
														border_width= 2)
		self.autoStartButton.pack(pady= 4)

		#Stop button
		self.autoStopButton = customtkinter.CTkButton(self.autoStartStopFrame, 
														width= SSEButtonWidth,
														height= SSEButtonHeight,
														fg_color= 'red',
														text= "STOP",
														font= ('Arial', SSEButtonTextSize, 'bold'),
														text_color= "Black",
														command= lambda: self.stopPressed(False),
														border_width= 2)
		self.autoStopButton.pack(pady= 4)


		#E-stop button
		self.autoEStopButton = customtkinter.CTkButton(self.autoStartStopFrame, 
														width= SSEButtonWidth,
														height= SSEButtonHeight,
														fg_color= 'yellow',
														text= "E-STOP", 
														font= ('Arial', SSEButtonTextSize, 'bold'),
														text_color= "Black",
														command= lambda: self.eStopPressed(False),
														border_width= 2)
		self.autoEStopButton.pack(pady= 4)


		# endregion

		#----------------------------------#
		#------Window Startup Actions------#
		#----------------------------------#

		# region WINDOW STARTUP ACTIONS

		#calibrate linear actuator
		messagebox.showwarning(title= "Calibrate Linear Actuator", 
								message= "Linear Actuator will now calibrate")
		data = "0,0,4"

		if LocalTest:
			doNothing = True
	
		else:
			self.ser.write(data.encode())
		
		#endregion
	

		#---------------------#
		#------Functions------#
		#---------------------#

		# region FUNCTIONS

	#--- General Functions ---#
	
	# function to send rpmVal, self.angleVal, and start command to arduino
	def startPressed(self, man):
		# if in the manual control mode
		if man:
			# check if the rpm and angle have been set
			if int(self.rpmEntry.get()) != self.rpmVal or int(self.angleEntry.get()) != self.angleVal:
				result = messagebox.askquestion(title= "Values Not Set", 
			   									message= "Set button was not pressed \nclick Yes to set current RPM and Angle values \nclick No to cancel")
				if result == 'yes':
					self.setRpm()
					self.setAngle()
				
				elif result == 'no':
					return
				
			
			# set variable values and update text in set buttons
			self.rpmEntryText.set(str(self.rpmVal))
			self.angleEntryText.set(str(self.angleVal))
			self.rpmSetText.set("UPDATE")
			self.angleSetText.set("UPDATE")
			self.manRunning = True
			self.autoRunning = False
			self.rpmDial.set(self.rpmVal)
			print("Manual Start Button pressed, rpmVal: " + str(self.rpmVal) + ", self.angleVal: " + str(self.angleVal))

		# if in the automatic control mode
		else:
			# set variable values and start timer
			self.manRunning = False
			self.autoRunning = True
			self.rpmVal = self.curProfile.rpm
			self.angleVal = self.curProfile.angle
			self.rpmDial.set(self.curProfile.rpm)
			self.startTime = time.time()
			print("Automatic Start Button pressed, rpmVal: " + str(self.rpmVal) + ", self.angleVal: " + str(self.angleVal))


		# send self.rpmVal and self.angleVal to arduino
		try:
			data = str(self.rpmVal) + "," + str(self.angleVal) + ",1"
			self.ser.write(data.encode())
		
		except AttributeError:
			print("no serial connection")


	# function to send stop command to arduino
	def stopPressed(self, man):
		# if in the manual control mode, update text in set buttons
		if man:
			self.rpmSetText.set("SET")
			self.angleSetText.set("SET")
			print("Manual Stop Button pressed, slowing down")
		
		# if in the automatic control mode, pause the timer
		else:
			self.timerLength = self.timerLength + (self.startTime - time.time())
			print("Automatic Stop Button pressed, slowing down")

		# set variable values and RPM dial value
		self.rpmVal = 0
		self.angleVal = 0
		self.rpmDial.set(self.rpmVal)
		self.manRunning = False
		self.autoRunning = False

		# send self.rpmVal and self.angleVal to arduino
		try:
			data = str(self.rpmVal) + "," + str(self.angleVal) + ",2"
			self.ser.write(data.encode())
		
		except AttributeError:
			print("no serial connection")
	

	# function to send e-stop command to arduino
	def eStopPressed(self, man):
		# if in the manual control mode, update text in set buttons
		if man:
			print("Manual Emergency Stop Button pressed, shutting down all systems")
			self.rpmSetText.set("SET")
			self.angleSetText.set("SET")

		else:
			# if in the automatic control mode, pause the timer
			print("Automatic Emergency Stop Button pressed, shutting down all systems")
			#pause timer
			self.timerLength = self.timerLength + (self.startTime - time.time())

		# set variable values and RPM dial value
		self.rpmVal = 0
		self.angleVal = 0
		self.rpmDial.set(self.rpmVal)
		self.manRunning = False
		self.autoRunning = False

		# send self.rpmVal and self.angleVal to arduino and Estop command 
		try:
			data = str(self.rpmVal) + "," + str(self.angleVal) + ",3"
			self.ser.write(data.encode())
		
		except AttributeError:
			print("no serial connection")

	
	# function to update the timer
	def updateTimer(self):
		# exit function if a mixing profile is not currently running
		if not self.autoRunning:
			return
		
		# if a mixing profile is running, update curTime variable
		curTime = time.time()

		# if the countdown timer has not reached 0
		if self.startTime + self.timerLength > curTime:
			# calculate time remaining
			tempHrLeft = int(self.timerLength + (self.startTime - curTime)) // 3600
			tempMinLeft = (int(self.timerLength + (self.startTime - curTime)) // 60) % 60
			tempSecLeft = int(self.timerLength + (self.startTime - curTime)) % 60

			# update time remaining text
			self.curProfTimeLeftText.set(f"{tempHrLeft:02}:{tempMinLeft:02}:{tempSecLeft:02}")
			return
		
		# if the last profile countdown timer has reached 0
		if self.curProfIndex == self.numProfs - 1:
			# set time reminaing text to 0, stop mixing, and send profile set complete message
			self.curProfTimeLeftText.set("00:00:00")
			self.stopPressed(False)
			messagebox.showinfo(title= "Profile Set Complete", 
		       					message= "All profiles have been completed")
			return

		# if time left is 0 and there are more profiles in the queue, move to the next profile
		if self.curProfIndex < self.numProfs - 1:
			self.nextProf()
			return


	#--- Manual Control Mode Functions ---#

	# function to increment value displayed in rpm entry box
	def incRpmEntry(self):
		# if the entry is at 200, keep entry at 200
		if (int(self.rpmEntryText.get()) + 10) > 200:
			self.rpmEntryText.set('200')
		
		# else add 10 
		else:
			self.rpmEntryText.set(str(int(self.rpmEntry.get()) + 10))


	# function to decrement value displayed in rpm entry box
	def decRpmEntry(self):
		# if the entry is at 0, keep entry at 0
		if (int(self.rpmEntryText.get()) - 10) < 0:
			self.rpmEntryText.set('0')
		
		# else subtract 10
		else:
			self.rpmEntryText.set(str(int(self.rpmEntry.get()) - 10))


	# function to increment value displayed in rpm entry box
	def incAngleEntry(self):
		# if the entry is at 90, keep entry at 90
		if (int(self.angleEntryText.get()) + 15) > 90:
			self.angleEntryText.set('90')
		
		# else add 15
		else:
			self.angleEntryText.set(str(int(self.angleEntry.get()) + 15))


	# function to decrement value displayed in rpm entry box
	def decAngleEntry(self):
		# if the entry is at 15, keep entry at 15
		if (int(self.angleEntryText.get()) - 15) < 15:
			self.angleEntryText.set('15')
		
		# else subtract 15
		else:
			self.angleEntryText.set(str(int(self.angleEntry.get()) - 15))


	# function to update selected rpm value
	def setRpm(self):
		# try block to validate entry value
		try:
			setInt = int(self.rpmEntry.get())

			# range check
			if (setInt > 200) or (setInt < 0):
				messagebox.showwarning(title= "RPM out of range", message= "RPM must be between 0 and 200")
				self.rpmEntryText.set('0')
				self.rpmVal = 0

			# increment check
			elif setInt % 10 != 0:
				messagebox.showwarning(title= "RPM increment error", message= "RPM must be in increments of 10")
				self.rpmEntryText.set('0')
				self.rpmVal = 0

			# if checks pass, set rpm value
			else:
				self.rpmVal = setInt
				print("rpm set button clicked, entry rpm is " + str(setInt)
							+ " rpmVal is " + str(self.rpmVal))

				# if manual mode is running, set dial value and send start command
				if(self.manRunning):
					self.rpmDial.set(setInt)
					try:
						data = str(self.rpmVal) + "," + str(self.angleVal) + ",1"
						self.ser.write(data.encode())
					
					except AttributeError:
						print("no serial connection")
		
		#if a decimal or non integer value is entered, throw error
		except ValueError:
			messagebox.showwarning(title= "Non-whole number RPM", message= "RPM must be a whole number")
			self.rpmEntryText.set('0')
			self.rpmVal = 0


	# function to update selected angle value
	def setAngle(self):
		# try block to validate entry value
		try:
			setInt = int(self.angleEntry.get())

			# range check
			if (setInt > 90) or (setInt < 15):
				messagebox.showwarning(title= "Angle out of range", message= "Angle must be between 15 and 90")
				self.angleEntryText.set('15')
				self.angleVal = 15
			
			# increment check
			elif setInt % 15 != 0:
				messagebox.showwarning(title= "Angle increment error", message= "Angle must be in increments of 15")
				self.angleEntryText.set('15')
				self.angleVal = 15

			# if checks pass, set angle value
			else:
				self.angleVal = setInt
				print("angle set button clicked, entry angle is " + str(setInt)
						+ " self.angleVal is " + str(self.angleVal))

				# if manual mode is running, send start command
				if(self.manRunning):
					try:
						data = str(self.rpmVal) + "," + str(self.angleVal) + ",1"
						self.ser.write(data.encode())
					
					except AttributeError:
						print("no serial connection")
		
		#if a decimal or non integer value is entered, throw error
		except ValueError:
			messagebox.showwarning(title= "Non-whole number Angle", message= "Angle must be a whole number")
			self.angleEntryText.set('15')
			self.angleVal = 15


	#--- Automatic Control Mode Functions ---#

	# function to import data from excel sheet
	def importPressed(self):
		try: 
			#open file dialog box, set filePath to string path of selected file
			filePath = filedialog.askopenfilename()

			#import excel file as pandas dataset
			profileDF = pd.read_excel(filePath, engine= 'openpyxl')
			
			#print(profileDF) #for testing

			#check if any cells are blank
			if profileDF.isnull().any().any():
				print("found a NaN")
				messagebox.showwarning(title= "Invalid Data",
										message= "found a NaN")

			#check if any cells are negative
			elif (profileDF < 0).any().any():
				print("found a negative number")
				messagebox.showwarning(title= "Invalid Data",
										message= "found a negative number")

			#check if RPM over 200
			elif (profileDF['RPM'] > 200).any():
				print("RPM over 200")
				messagebox.showwarning(title= "Invalid Data",
										message= "RPM over 200")
				
			#check if Angle over 90
			elif (profileDF['Angle'] > 90).any():
				print("Angle over 90")
				messagebox.showwarning(title= "Invalid Data",
										message= "Angle over 90")

			#check if Angle under 15
			elif (profileDF['Angle'] < 15).any():
				print("Angle under 15")
				messagebox.showwarning(title= "Invalid Data",
										message= "Angle under 15")

			#check if Angle increments of 15
			elif (profileDF['Angle'] % 15 != 0).any():
				print("Angle must be in increments of 15")
				messagebox.showwarning(title= "Invalid Data",
										message= "Angle must be in increments of 15")

			#check if RPM increments of 10
			elif (profileDF['RPM'] % 10 != 0).any():
				print("RPM must be in increments of 10")
				messagebox.showwarning(title= "Invalid Data",
										message= "RPM must be in increments of 10")

			#else if all data valid, create MixProfile class for each profile
			#and add to profile list and listbox
			else:
				self.numProfs = len(profileDF)
				for i in range(self.numProfs):	
					tempProf = MixProfile(profileDF.iat[i,0], 
												profileDF.iat[i,1],
												profileDF.iat[i,2],
												profileDF.iat[i,3],
												profileDF.iat[i,4])
					self.profileList.append(tempProf)
					self.allProfListBox.insert(i, self.profileList[i].printInfoTextLine())

				#set current provile to profile at self.curProfIndex
				self.curProfile = copy.deepcopy(self.profileList[self.curProfIndex])
				self.curProfRPMText.set(self.curProfile.rpm)
				self.curProfAngleText.set(self.curProfile.angle)
				self.curProfTimeText.set(f"{self.curProfile.hour:02}:{self.curProfile.min:02}:{self.curProfile.sec:02}")
				self.timerLength = self.curProfile.hour * 3600 + self.curProfile.min * 60 + self.curProfile.sec
				self.curProfTimeLeftText.set(f"{self.curProfile.hour:02}:{self.curProfile.min:02}:{self.curProfile.sec:02}")
				self.allProfListBox.selection_set(self.curProfIndex)

		# catch cancel button pressed
		except FileNotFoundError:
			donothing = True


	# function to clear all profiles from the profile list box
	def clearAllPressed(self):
		# stop current profile if running
		self.stopPressed(False)

		# clear listbox and profileList
		self.profileList.clear()
		self.allProfListBox.delete(0, END)
		self.numProfs = 0

		# reset profile text to default
		self.curProfRPMText.set("0")
		self.curProfAngleText.set("0")
		self.curProfTimeText.set("00:00:00")
		self.curProfTimeLeftText.set("00:00:00")
	
	
	# function to select previous profile in listbox
	def prevProf(self):
		# check if at the first profile and notify user 
		if self.curProfIndex == 0:
			messagebox.showinfo(title= "First Profile", 
		       					message= "This is the first profile in the set")
			return
		
		# else deep copy previous profile to current profile
		if self.curProfIndex > 0 and self.numProfs != 0:
			self.curProfIndex = self.curProfIndex - 1
			# print(self.curProfIndex)
			self.curProfile = copy.deepcopy(self.profileList[self.curProfIndex])

			# set rpm, angle, and time values
			self.curProfRPMText.set(self.curProfile.rpm)
			self.curProfAngleText.set(self.curProfile.angle)
			self.curProfTimeText.set(f"{self.curProfile.hour:02}:{self.curProfile.min:02}:{self.curProfile.sec:02}")
			self.curProfTimeLeftText.set(f"{self.curProfile.hour:02}:{self.curProfile.min:02}:{self.curProfile.sec:02}")
			self.timerLength = self.curProfile.hour * 3600 + self.curProfile.min * 60 + self.curProfile.sec
			self.startTime = time.time()

			# update listbox selection
			self.allProfListBox.see(self.curProfIndex)
			self.allProfListBox.selection_clear(0, END)
			self.allProfListBox.selection_set(self.curProfIndex)

		# if already running, send run signal to arduino (start the profile)
		if self.autoRunning:
			self.startPressed(False)


	# function to select next profile in listbox
	def nextProf(self):
		# check if at the last profile and notify user
		if self.curProfIndex == self.numProfs - 1:
			messagebox.showinfo(title= "Last Profile", 
		       					message= "This is the last profile in the set")
			return

		# else deep copy next profile to current profile
		if self.curProfIndex < self.numProfs - 1 and self.numProfs != 0:
			self.curProfIndex = self.curProfIndex + 1
			#print(self.curProfIndex)
			self.curProfile = copy.deepcopy(self.profileList[self.curProfIndex])

			# set rpm, angle, and time values
			self.curProfRPMText.set(self.curProfile.rpm)
			self.curProfAngleText.set(self.curProfile.angle)
			self.curProfTimeText.set(f"{self.curProfile.hour:02}:{self.curProfile.min:02}:{self.curProfile.sec:02}")
			self.curProfTimeLeftText.set(f"{self.curProfile.hour:02}:{self.curProfile.min:02}:{self.curProfile.sec:02}")
			self.timerLength = self.curProfile.hour * 3600 + self.curProfile.min * 60 + self.curProfile.sec
			self.startTime = time.time()

			# update listbox selection
			self.allProfListBox.see(self.curProfIndex)
			self.allProfListBox.selection_clear(0, END)
			self.allProfListBox.selection_set(self.curProfIndex)

		# if already running, send run signal to arduino (start the profile)
		if self.autoRunning:
			self.startPressed(False)
		

	# function to restart the current profile
	def restartProf(self):

		# if profiles have been added, reset the time to the current profiles total time
		if self.numProfs != 0:
			self.curProfTimeLeftText.set(f"{self.curProfile.hour:02}:{self.curProfile.min:02}:{self.curProfile.sec:02}")
			self.startTime = time.time()
		
		# if already running, send run signal to arduino (restart the profile)
		if self.autoRunning:
			self.startPressed(False)

		# endregion


#built in main

#function to continuously receive and parse feedback data from Arduino
def getFeedback():
	while True:
		try:
			# read and parse data from serial
			data = mainSer.readline().decode().strip()
			RPMFeedback, angleFeedback = data.split(',')
			RPMFeedback = int(RPMFeedback)
			angleFeedback = int(angleFeedback)

			# print reading and set angleDial
			print("Received Angle feedback:", angleFeedback)
			#guiObj.rpmDial.set(RPMFeedback)
			guiObj.angleDial.set(angleFeedback)

		except ValueError:
			pass

# function to update the timer ever 1 second
def task():
	guiObj.updateTimer()
	window.after(1000, task)


# function to stop reactor and clear gui window on close
def windowClose():
	guiObj.stopPressed(True)
	window.destroy()


#open serial communication port
try:
	mainSer = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)

except serial.serialutil.SerialException:
	print("no serial connection")
	mainSer = NONE


# set up customTk window
window = customtkinter.CTk()
customtkinter.set_appearance_mode("light")
window.protocol("WM_DELETE_WINDOW", windowClose)

# declare GUIClass object of size 800x400 px
guiObj = GUIClass(window, mainSer)
window.geometry("800x400")
window.after(1000, task)

#if not using LocalTest, thread feedback
if not LocalTest:
	receive_thread = threading.Thread(target=getFeedback)
	receive_thread.start()

#start main loop of window (open GUI)
window.mainloop()