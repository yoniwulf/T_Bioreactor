from tkinter import*
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkdial import*
from MixingProfileClass import *
import pandas as pd
import serial

# region NOTES/IDEAS
""" 
Ideas:
* set buttons change variables (global?) of rpm and angle
* once user presses start, new values will be sent to arduino
* change set buttons to different color when user has changed value
	* user must click set to update value
* change start button to "update" when new values for rpm or angle are set


cancel import
 """
# endregion

class GUIClass:
	#----------------------------#
	#------Setup GUI Window------#
	#----------------------------#
	def __init__(self, master):
		self.master = master
		master.title("T-BioReactor Controls")

		# declare notebook to allow different tabs
		self.notebook = ttk.Notebook(master)

		#declare manual and automatic control tabs, add to notebook and grid
		self.manControlTab = Frame(self.notebook)
		self.autoControlTab = Frame(self.notebook)
		#testTab = Frame(notebook)
		self.notebook.add(self.manControlTab, text= "Manual Control")
		self.notebook.add(self.autoControlTab, text= "Automatic Control")
		#notebook.add(testTab, text= "test tab")
		self.notebook.pack(expand= TRUE)

		#declare variables
		self.rpmVal = 0 #set rpm value
		self.angleVal = 15 #set angle value
		self.profileList = [] #list for mixing profiles
		self.curProfIndex = 0 #index of current mixing profile
		self.numProfs = 0 #number of profiles
		self.curProfText = StringVar() #stringVar for current profile
		self.rpmEntryText = StringVar() #stringVar for rpm displayed in self.rpmEntry widget
		self.angleEntryText = StringVar() #stringVar for angle displayed in self.angleEntry widget
		self.timeRemainingText = StringVar() #stringVar for text displayed in current profile message 2
		self.rpmDialVal = 50 #actual rpm value (can be set for testing)
		self.angleDialVal = 15 #actual angle value (can be set for testing)

		#set StringVars
		self.curProfText.set("RPM:           Angle:  \nTime:           00:00:00")
		self.rpmEntryText.set("0")
		self.angleEntryText.set("15")
		self.timeRemainingText.set("Remaining:  00:00:00")

		self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)


		# region MANUAL CONTROL TAB
		#------------------------------#
		#------Manual Control Tab------#
		#------------------------------#

		#------RPM Control------#

		self.rpmFrame = Frame(self.manControlTab)
		self.rpmFrame.pack(side= LEFT, fill= 'y', padx= 30)

		#RPM control section label
		self.rpmLabel = Label(self.rpmFrame, text= "RPM", font= ('Arial', 30, 'bold'))
		self.rpmLabel.pack(pady= 5)

		#RPM dial
		self.rpmDial = Meter(self.rpmFrame, 
							start= 0, 
							end= 200, 
							major_divisions= 20, 
							minor_divisions= 5,
							radius= 230,
							border_width= 0,
							start_angle= 205,
							end_angle= -230,
							text= " RPM")
		self.rpmDial.pack(pady= 10)
		self.rpmDial.set(self.rpmDialVal)

		#rpm entry box label
		self.rpmEntryLabel = Label(self.rpmFrame, text= "Set RPM:", font= ('Arial', 16))
		self.rpmEntryLabel.pack()

		#rpm entry frame
		self.rpmEntryFrame = Frame(self.rpmFrame)
		self.rpmEntryFrame.pack()

		#rpm -10 button
		self.rpmDecButton = Button(self.rpmEntryFrame, 
								text= "-10",
								command= self.decRpmEntry,
								padx= 5,
								pady= 5)
		self.rpmDecButton.pack(side= LEFT, padx= 5)

		#rpm entry box
		self.rpmEntry = Entry(self.rpmEntryFrame, 
							font= ('Arial', 20), 
							width= 5, 
							textvariable= self.rpmEntryText,
							justify= CENTER)
		self.rpmEntry.pack(side= LEFT)

		#rpm +10 button
		self.rpmIncButton = Button(self.rpmEntryFrame, 
								text= "+10",
								command= self.incRpmEntry,
								padx= 5,
								pady= 5)
		self.rpmIncButton.pack(side= LEFT, padx= 5)

		#RPM set button
		self.rpmSetButton = Button(self.rpmFrame, 
								text= "SET", 
								command= self.setRpm,
								padx= 30,
								pady= 5,
								border= 5,
								background= 'green')
		self.rpmSetButton.pack(pady= 10)


		#------Angle Control------#

		self.angleFrame = Frame(self.manControlTab)
		self.angleFrame.pack(side= LEFT, fill= 'y', padx= 20)

		#angle control section label
		self.angleLabel = Label(self.angleFrame, text= "ANGLE", font= ('Arial', 30, 'bold'), width= 7)
		self.angleLabel.pack(pady= 5)

		#angle dial
		self.angleDial = Meter(self.angleFrame, 
							start= 0, 
							end= 90, 
							major_divisions= 15, 
							minor_divisions= 5,
							radius= 230,
							border_width= 0,
							start_angle= 0,
							end_angle= 90,
							text= " Degrees"
							)
		self.angleDial.pack(pady= 10)
		self.angleDial.set(self.angleDialVal)

		#angle entry box label
		self.angleEntryLabel = Label(self.angleFrame, text= "Set Angle:", font= ('Arial', 16))
		self.angleEntryLabel.pack()

		#angle entry frame
		self.angleEntryFrame = Frame(self.angleFrame)
		self.angleEntryFrame.pack()

		#angle -15 button
		self.angleDecButton = Button(self.angleEntryFrame, 
								text= "-15",
								command= self.decAngleEntry,
								padx= 5,
								pady= 5)
		self.angleDecButton.pack(side= LEFT, padx= 5)

		#angle entry box
		self.angleEntry = Entry(self.angleEntryFrame, 
							font= ('Arial', 20), 
							width= 5, 
							textvariable= self.angleEntryText,
							justify= CENTER)
		self.angleEntry.pack(side= LEFT)

		#angle +15 button
		self.angleIncButton = Button(self.angleEntryFrame, 
								text= "+15",
								command= self.incAngleEntry,
								padx= 5,
								pady= 5)
		self.angleIncButton.pack(side= LEFT, padx= 5)

		#Angle set button
		self.angleSetButton = Button(self.angleFrame, 
								text= "SET", 
								command= self.setAngle,
								padx= 30,
								pady= 5,
								border= 5,
								background= 'green')
		self.angleSetButton.pack(pady= 10)


		#------Start/Stop Control------#

		self.manStartStopFrame = Frame(self.manControlTab)
		self.manStartStopFrame.pack(side= LEFT, fill= 'y', padx= 30)

		#Start button
		self.manStartButton = Button(self.manStartStopFrame, 
								width= 6,
								height= 3,
								background= 'green',
								text= "START", 
								font= ('Arial', 20, 'bold'),
								#fg= "white",
								command= self.startPressed,
								border= 5)
		self.manStartButton.pack(pady= 10)

		#Stop button
		self.manStopButton = Button(self.manStartStopFrame, 
								width= 6,
								height= 3,
								background= 'red',
								text= "STOP",
								font= ('Arial', 20, 'bold'),
								#fg= "white",
								command= self.stopPressed,
								border= 5)
		self.manStopButton.pack(pady= 10)


		#E-stop button
		self.manEStopButton = Button(self.manStartStopFrame, 
								width= 6,
								height= 3,
								background= 'yellow',
								text= "E-STOP", 
								font= ('Arial', 20, 'bold'),
								command= self.eStopPressed,
								border= 5)
		self.manEStopButton.pack(pady= 10)

		# endregion


		# region AUTOMATION CONTROL TAB
		#----------------------------------#
		#------Automation Control Tab------#
		#----------------------------------#

		#------Current Profile display------#

		#profiles frame
		self.autoProfFrame = Frame(self.autoControlTab)
		self.autoProfFrame.pack(side= LEFT, fill= 'y', padx= 30, expand= True)

		#current profile Label
		self.curProfLabel = Label(self.autoProfFrame, text= "Current Profile", font= ('Arial', 30, 'bold'))
		self.curProfLabel.pack()

		#create message for current profile, pack into curProfFrame
		self.curProfMes = Message(self.autoProfFrame, 
									textvariable= self.curProfText,
									justify= 'left',
									font= ('Arial', 16),
									width= 500)
		self.curProfMes.pack()

		#create message for remaining time
		self.curProfMes = Message(self.autoProfFrame, 
									textvariable= self.timeRemainingText,
									justify= 'left',
									font= ('Arial', 16),
									width= 500)
		self.curProfMes.pack()

		#create frame for profile options
		self.profOptFrame = Frame(self.autoProfFrame)
		self.profOptFrame.pack()

		#create previous profile button
		self.prevProfButton = Button(self.profOptFrame, 
								text= "PREV", 
								width= 6,
								command= self.prevProf)
		self.prevProfButton.pack(side= LEFT, padx= 12, pady= 5)

		#create restart profile button
		self.restartProfButton = Button(self.profOptFrame, text= "RESTART", width= 10)
		self.restartProfButton.pack(side= LEFT)

		#create next profile button
		self.nextProfButton = Button(self.profOptFrame, 
								text= "NEXT", 
								width= 6,
								command= self.nextProf)
		self.nextProfButton.pack(side= LEFT, padx= 12)



		#------All Profiles display------#

		#all profiles Label
		self.allProfLabel = Label(self.autoProfFrame, text= "All Profiles", font= ('Arial', 30, 'bold'))
		self.allProfLabel.pack(pady= 10)

		#all profiles list box
		self.allProfListBox = Listbox(self.autoProfFrame, 
								height= 8, 
								width= 32, 
								font= ('Arial', 11),
								activestyle= 'dotbox',
								selectbackground= 'green',
								highlightthickness= 3,
								selectmode= SINGLE)
		self.allProfListBox.pack()

		#import and clear all frame
		self.importClearFrame = Frame(self.autoProfFrame)
		self.importClearFrame.pack(pady= 10)

		#import profiles button
		self.importProfButton = Button(self.importClearFrame, 
									text= "Import", 
									width= 15, 
									command= self.importPressed)
		self.importProfButton.pack(side= LEFT, padx= 12)

		#clear profiles button
		self.clearProfButton = Button(self.importClearFrame, text= "Clear All", width= 15)
		self.clearProfButton.pack(side= RIGHT, padx= 12)


		#------Start/Stop Control------#

		self.autoStartStopFrame = Frame(self.autoControlTab)
		self.autoStartStopFrame.pack(side= RIGHT, fill= 'y', padx= 30)

		#Start button
		self.autoStartButton = Button(self.autoStartStopFrame, 
								width= 6,
								height= 3,
								background= 'green',
								text= "START", 
								font= ('Arial', 20, 'bold'),
								#command= startPressed, # change to new func
								border= 5)
		self.autoStartButton.pack(pady= 10)

		#Stop button
		self.autoStopButton = Button(self.autoStartStopFrame, 
								width= 6,
								height= 3,
								background= 'red',
								text= "STOP",
								font= ('Arial', 20, 'bold'),
								#command= stopPressed, # change to new func
								border= 5)
		self.autoStopButton.pack(pady= 10)


		#E-stop button
		self.autoEStopButton = Button(self.autoStartStopFrame, 
								width= 6,
								height= 3,
								background= 'yellow',
								text= "E-STOP", 
								font= ('Arial', 20, 'bold'),
								#command= eStopPressed, # change to new func
								border= 5)
		self.autoEStopButton.pack(pady= 10)

		# endregion


		#---------------------#
		#------Main Loop------#
		#---------------------#

	

	#---------------------#
	#------Functions------#
	#---------------------#
	# region FUNCTIONS

	# function to update selected rpm value
	def setRpm(self):
		self.rpmVal
		self.rpmDialVal
		self.rpmEntryText

		#try block to validate entry value
		try:
			setInt = int(self.rpmEntry.get())

			if (setInt > 200) or (setInt < 0):
				messagebox.showwarning(title= "RPM out of range", message= "RPM must be between 0 and 200")

			if setInt % 10 != 0:
				messagebox.showwarning(title= "RPM increment error", message= "RPM must be in increments of 10")

			else:
				self.rpmVal = setInt
				print("rpm set button clicked, entry rpm is " + str(setInt)
						+ " rpmVal is " + str(self.rpmVal))
				
				self.rpmDial.set(setInt) #for testing
		
		#if a decimal or non integer value is entered
		except ValueError:
			messagebox.showwarning(title= "Non-whole number RPM", message= "RPM must be a whole number")
			self.rpmEntryText.set('0')

	# function to update selected angle value
	def setAngle(self):
		self.angleVal
		self.angleEntryText
		
		#try block to validate entry value
		try:
			setInt = int(self.angleEntry.get())

			if (setInt > 90) or (setInt < 15):
				messagebox.showwarning(title= "Angle out of range", message= "Angle must be between 15 and 90")
			
			if setInt % 15 != 0:
				messagebox.showwarning(title= "Angle increment error", message= "Angle must be in increments of 15")

			else:
				self.angleVal = setInt
				print("angle set button clicked, entry angle is " + str(setInt)
						+ " self.angleVal is " + str(self.angleVal))

				self.angleDial.set(setInt) #for testing
		
		#if a decimal or non integer value is entered
		except ValueError:
			messagebox.showwarning(title= "Non-whole number Angle", message= "Angle must be a whole number")
			self.angleEntryText.set('15')

	# function to send rpmVal, self.angleVal, and start command (needed?) to arduino
	def startPressed(self):
		# send rpmVal and self.angleVal to arduino
		print("Start Button pressed, rpmVal: " + str(self.rpmVal) + ", self.angleVal: " + str(self.angleVal))

		data = str(self.rpmVal) + "," + str(self.angleVal)
		self.ser.write(data.encode())

	# function to send stop command to arduino
	def stopPressed(self):
		self.rpmVal
		self.angleVal
		self.rpmVal = 0
		self.angleVal = 0
		print("Stop Button pressed, slowing down")


	# function to send e-stop command to arduino
	def eStopPressed(self):
		print("Emergency Stop Button pressed, shutting down all systems")

	# function to import data from excel sheet
	def importPressed(self):
		#insure access to variables 
		self.profileList
		self.curProfText
		self.allProfListBox
		self.numProfs
		
		#open file dialog box, set filePath to string path of selected file
		filePath = filedialog.askopenfilename()

		#import excel file as pandas dataset
		profileDF = pd.read_excel(filePath)
		#print(profileDF)

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

		elif (profileDF['Angle'] < 15).any():
			print("Angle under 15")
			messagebox.showwarning(title= "Invalid Data",
									message= "Angle under 15")

		elif (profileDF['Angle'] % 15 != 0).any():
			print("Angle must be in increments of 15")
			messagebox.showwarning(title= "Invalid Data",
									message= "Angle must be in increments of 15")

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
				#print(self.profileList[i].rpm)

			#set current provile to profile at self.curProfIndex
			self.curProfText.set(self.profileList[self.curProfIndex].printInfoTextReturn())

	# function to increment value displayed in rpm entry box
	def incRpmEntry(self):
		if (int(self.rpmEntryText.get()) + 10) > 200:
			self.rpmEntryText.set('200')
			
		else:
			self.rpmEntryText.set(str(int(self.rpmEntry.get()) + 10))

	# function to decrement value displayed in rpm entry box
	def decRpmEntry(self):
		if (int(self.rpmEntryText.get()) - 10) < 0:
			self.rpmEntryText.set('0')
		
		else:
			self.rpmEntryText.set(str(int(self.rpmEntry.get()) - 10))

	# function to increment value displayed in rpm entry box
	def incAngleEntry(self):
		if (int(self.angleEntryText.get()) + 15) > 90:
			self.angleEntryText.set('90')
		
		else:
			self.angleEntryText.set(str(int(self.angleEntry.get()) + 15))

	# function to decrement value displayed in rpm entry box
	def decAngleEntry(self):
		if (int(self.angleEntryText.get()) - 15) < 15:
			self.angleEntryText.set('15')
		
		else:
			self.angleEntryText.set(str(int(self.angleEntry.get()) - 15))

	#function to select previous profile in listbox
	def prevProf(self):
		self.curProfIndex
		self.curProfText
		self.profileList

		if self.curProfIndex > 0:
			self.curProfIndex = self.curProfIndex - 1
			print(self.curProfIndex)
			self.curProfText.set(self.profileList[self.curProfIndex].printInfoTextReturn())
			#self.allProfListBox.activate(self.curProfIndex)
			self.allProfListBox.see(self.curProfIndex)
			self.allProfListBox.selection_clear(0, END)
			self.allProfListBox.selection_set(self.curProfIndex)

	#function to select next profile in listbox
	def nextProf(self):
		self.curProfIndex
		self.numProfs
		self.curProfText
		self.profileList

		if self.curProfIndex < self.numProfs - 1:
			self.curProfIndex = self.curProfIndex + 1
			print(self.curProfIndex)
			self.curProfText.set(self.profileList[self.curProfIndex].printInfoTextReturn())
			#self.allProfListBox.activate(self.curProfIndex)
			self.allProfListBox.see(self.curProfIndex)
			self.allProfListBox.selection_clear(0, END)
			self.allProfListBox.selection_set(self.curProfIndex)

	# endregion


# region OLD CODE
"""

#RPM scale
rpmScale = Scale(manControlTab, 
					from_= 200, 
					to= 0,
					length= 400,
					width= 20,
					orient= VERTICAL,
					font= ('Arial', 16),
					tickinterval = 20,
					resolution= 10,
					border= 5,
					activebackground= 'red',
					showvalue= 0)
rpmScale.grid(row= 2, column= 0, rowspan= 3)

#Angle scale
angleScale = Scale(manControlTab, 
					from_= 90, 
					to= 0,
					length= 400,
					width= 20,
					orient= VERTICAL,
					font= ('Arial', 16),
					tickinterval = 15,
					resolution= 15,
					border= 5,
					activebackground= 'red',
					showvalue= 0)
angleScale.grid(row= 2, column= 1, rowspan= 3)



self.curProfTextBox = Text(autoControlTab, height= 3, width= 50)
self.curProfTextBox.insert(index= END, chars= "RPM = ... \nAngle = ... \n Time = ...")
self.curProfTextBox.grid(row = 1, column= 0, rowspan= 3, columnspan= 6)
self.curProfTextBox.configure(state='disabled')

#create message for time and time remaining, pack (WIP)
curProfTimeMes = Message(curProfFrame, 
							text= "Time:            " + curProfTime + "\nRemaining:   " + curProfTimeRem, 
							justify= 'left', 
							font= ('Arial', 16),
							width= 500)
curProfTimeMes.pack()



#create frame for all profiles, add to grid
allProfFrame = Frame(autoControlTab)
#allProfFrame.grid(row = 6, column= 0, rowspan= 3, columnspan= 2)




allProfMes = Message(allProfFrame, 
						text= self.profileList[0].printInfoText() + "\n\n" + self.profileList[1].printInfoText() + "\n\n" + self.profileList[2].printInfoText(),
						justify= 'left',
						font= ('Arial', 16),
						width= 500)
#allProfMes.pack()


#create scroll bar for all profiles frame
allProfScroll = Scrollbar(allProfFrame, orient= 'vertical')
allProfScroll.pack(side= RIGHT, fill= Y)
#allProfScroll.config(command= t.xview)  # add some text object 

"""
# endregion
