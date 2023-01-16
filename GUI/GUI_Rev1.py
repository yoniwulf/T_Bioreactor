from tkinter import*
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkdial import*
from MixingProfileClass import *
import pandas as pd

#------Notes/Ideas------#
""" 
Ideas:
* set buttons change variables (global?) of rpm and angle
* once user presses start, new values will be sent to arduino
* change set buttons to different color when user has changed value
	* user must click set to update value
* change start button to "update" when new values for rpm or angle are set


cancel import
 """




#----------------------------#
#------Setup GUI Window------#
#----------------------------#

# declare main window
window = Tk()
window.geometry("800x480")

# declare notebook to allow different tabs
notebook = ttk.Notebook(window)

#declare manual and automatic control tabs, add to notebook and grid
manControlTab = Frame(notebook)
autoControlTab = Frame(notebook)
#testTab = Frame(notebook)
notebook.add(manControlTab, text= "Manual Control")
notebook.add(autoControlTab, text= "Automatic Control")
#notebook.add(testTab, text= "test tab ")
notebook.pack(expand= TRUE)

#declare variables
rpmVal = 0 #set rpm value
angleVal = 0 #set angle value
profileList = [] #list for mixing profiles
curProfIndex = 0 #index of current mixing profile
curProfText = StringVar() #stringVar for current profile
rpmEntryText = StringVar() #stringVar for rpm displayed in rpmEntry widget
angleEntryText = StringVar() #stringVar for angle displayed in angleEntry widget
timeRemainingText = StringVar() #stringVar for text displayed in current profile message 2
rpmDialVal = 50 #actual rpm value (can be set for testing)
angleDialVal = 15 #actual angle value (can be set for testing)

#set StringVars
curProfText.set("RPM:           Angle:  \nTime:           00:00:00")
rpmEntryText.set("0")
angleEntryText.set("0")
timeRemainingText.set("Remaining:  00:00:00")



#---------------------#
#------Functions------#
#---------------------#


# function to update selected rpm value
def setRpm():
	global rpmVal
	global rpmDialVal
	global rpmEntryText

	#try block to validate entry value
	try:
		setInt = int(rpmEntry.get())

		if (setInt > 200) or (setInt < 0):
			messagebox.showwarning(title= "RPM out of range", message= "RPM must be between 0 and 200")

		if setInt % 10 != 0:
			messagebox.showwarning(title= "RPM increment error", message= "RPM must be in increments of 10")

		else:
			rpmVal = setInt
			print("rpm set button clicked, entry rpm is " + str(setInt)
					+ " rpmVal is " + str(rpmVal))
			
			rpmDial.set(setInt) #for testing
	
	#if a decimal or non integer value is entered
	except ValueError:
		messagebox.showwarning(title= "Non-whole number RPM", message= "RPM must be a whole number")
		rpmEntryText.set('0')

# function to update selected angle value
def setAngle():
	global angleVal
	global angleEntryText
	
	#try block to validate entry value
	try:
		setInt = int(angleEntry.get())

		if (setInt > 90) or (setInt < 0):
			messagebox.showwarning(title= "Angle out of range", message= "Angle must be between 0 and 90")
		
		if setInt % 15 != 0:
			messagebox.showwarning(title= "Angle increment error", message= "Angle must be in increments of 15")

		else:
			angleVal = setInt
			print("angle set button clicked, entry angle is " + str(setInt)
					+ " angleVal is " + str(angleVal))

			angleDial.set(setInt) #for testing
	
	#if a decimal or non integer value is entered
	except ValueError:
		messagebox.showwarning(title= "Non-whole number Angle", message= "Angle must be a whole number")
		angleEntryText.set('0')

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

# function to import data from excel sheet
def importPressed():
	#insure access to variables 
	global profileList
	global curProfText
	global allProfListBox
	
	#open file dialog box, set filePath to string path of selected file
	filePath = filedialog.askopenfilename()

	#import excel file as pandas dataset
	profileDF = pd.read_excel(filePath)
	#print(profileDF)

	#check if any cells are blank
	if profileDF.isnull().any().any():
		print("found a NaN")

	#check if any cells are negative
	elif (profileDF < 0).any().any():
		print("found a negative number")

	#check if RPM over 200
	elif (profileDF['RPM'] > 200).any():
		print("RPM over 200")
	
	#check if Angle over 90
	elif (profileDF['Angle'] > 90).any():
		print("Angle over 90")

	#else if all data valid, create MixProfile class for each profile
	#and add to profile list and listbox
	else:
		for i in range(len(profileDF)):	
			tempProf = MixProfile(profileDF.iat[i,0], 
										profileDF.iat[i,1],
										profileDF.iat[i,2],
										profileDF.iat[i,3],
										profileDF.iat[i,4])
			profileList.append(tempProf)
			allProfListBox.insert(i, profileList[i].printInfoTextLine())
			#print(profileList[i].rpm)

		#set current provile to profile at curProfIndex
		curProfText.set(profileList[curProfIndex].printInfoTextReturn())

# function to increment value displayed in rpm entry box
def incRpmEntry():
	if (int(rpmEntryText.get()) + 10) > 200:
		rpmEntryText.set('200')
		
	else:
		rpmEntryText.set(str(int(rpmEntry.get()) + 10))

# function to decrement value displayed in rpm entry box
def decRpmEntry():
	if (int(rpmEntryText.get()) - 10) < 0:
		rpmEntryText.set('0')
	
	else:
		rpmEntryText.set(str(int(rpmEntry.get()) - 10))

# function to increment value displayed in rpm entry box
def incAngleEntry():
	if (int(angleEntryText.get()) + 15) > 90:
		angleEntryText.set('90')
	
	else:
		angleEntryText.set(str(int(angleEntry.get()) + 15))

# function to decrement value displayed in rpm entry box
def decAngleEntry():
	if (int(angleEntryText.get()) - 15) < 0:
		angleEntryText.set('0')
	
	else:
		angleEntryText.set(str(int(angleEntry.get()) - 15))



#------------------------------#
#------Manual Control Tab------#
#------------------------------#

#------RPM Control------#

rpmFrame = Frame(manControlTab)
rpmFrame.pack(side= LEFT, fill= 'y', padx= 30)

#RPM control section label
rpmLabel = Label(rpmFrame, text= "RPM", font= ('Arial', 30, 'bold'))
rpmLabel.pack(pady= 5)

#RPM dial
rpmDial = Meter(rpmFrame, 
					start= 0, 
					end= 200, 
					major_divisions= 20, 
					minor_divisions= 5,
					radius= 230,
					border_width= 0,
					start_angle= 205,
					end_angle= -230,
					text= " RPM")
rpmDial.pack(pady= 10)
rpmDial.set(rpmDialVal)

#rpm entry box label
rpmEntryLabel = Label(rpmFrame, text= "Set RPM:", font= ('Arial', 16))
rpmEntryLabel.pack()

#rpm entry frame
rpmEntryFrame = Frame(rpmFrame)
rpmEntryFrame.pack()

#rpm -10 button
rpmDecButton = Button(rpmEntryFrame, 
						text= "-10",
						command= decRpmEntry,
						padx= 5,
						pady= 5)
rpmDecButton.pack(side= LEFT, padx= 5)

#rpm entry box
rpmEntry = Entry(rpmEntryFrame, 
					font= ('Arial', 20), 
					width= 5, 
					textvariable= rpmEntryText,
					justify= CENTER)
rpmEntry.pack(side= LEFT)

#rpm +10 button
rpmIncButton = Button(rpmEntryFrame, 
						text= "+10",
						command= incRpmEntry,
						padx= 5,
						pady= 5)
rpmIncButton.pack(side= LEFT, padx= 5)

#RPM set button
rpmSetButton = Button(rpmFrame, 
						text= "SET", 
						command= setRpm,
						padx= 30,
						pady= 5,
						border= 5,
						background= 'green')
rpmSetButton.pack(pady= 10)


#------Angle Control------#

angleFrame = Frame(manControlTab)
angleFrame.pack(side= LEFT, fill= 'y', padx= 20)

#angle control section label
angleLabel = Label(angleFrame, text= "ANGLE", font= ('Arial', 30, 'bold'), width= 7)
angleLabel.pack(pady= 5)

#angle dial
angleDial = Meter(angleFrame, 
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
angleDial.pack(pady= 10)
angleDial.set(angleDialVal)

#angle entry box label
angleEntryLabel = Label(angleFrame, text= "Set Angle:", font= ('Arial', 16))
angleEntryLabel.pack()

#angle entry frame
angleEntryFrame = Frame(angleFrame)
angleEntryFrame.pack()

#rpm -10 button
angleDecButton = Button(angleEntryFrame, 
						text= "-15",
						command= decAngleEntry,
						padx= 5,
						pady= 5)
angleDecButton.pack(side= LEFT, padx= 5)

#rpm entry box
angleEntry = Entry(angleEntryFrame, 
					font= ('Arial', 20), 
					width= 5, 
					textvariable= angleEntryText,
					justify= CENTER)
angleEntry.pack(side= LEFT)

#rpm +10 button
angleIncButton = Button(angleEntryFrame, 
						text= "+15",
						command= incAngleEntry,
						padx= 5,
						pady= 5)
angleIncButton.pack(side= LEFT, padx= 5)


#Angle set button
angleSetButton = Button(angleFrame, 
						text= "SET", 
						command= setAngle,
						padx= 30,
						pady= 5,
						border= 5,
						background= 'green')
angleSetButton.pack(pady= 10)


#------Start/Stop/E-Stop Control------#

manStartStopFrame = Frame(manControlTab)
manStartStopFrame.pack(side= LEFT, fill= 'y', padx= 30)

#Start button
manStartButton = Button(manStartStopFrame, 
						width= 6,
						height= 3,
						background= 'green',
						text= "START", 
						font= ('Arial', 20, 'bold'),
						command= startPressed,
						border= 5)
manStartButton.pack(pady= 10)

#Stop button
manStopButton = Button(manStartStopFrame, 
						width= 6,
						height= 3,
						background= 'red',
						text= "STOP",
						font= ('Arial', 20, 'bold'),
						command= stopPressed,
						border= 5)
manStopButton.pack(pady= 10)

#E-stop button
manEStopButton = Button(manStartStopFrame, 
						width= 6,
						height= 3,
						background= 'yellow',
						text= "E-STOP", 
						font= ('Arial', 20, 'bold'),
						command= eStopPressed,
						border= 5)
manEStopButton.pack(pady= 10)


#----------------------------------#
#------Automation Control Tab------#
#----------------------------------#

#------Current Profile display------#

#profiles frame
autoProfFrame = Frame(autoControlTab)
autoProfFrame.pack(side= LEFT, fill= 'y', padx= 30, expand= True)

#current profile Label
curProfLabel = Label(autoProfFrame, text= "Current Profile", font= ('Arial', 30, 'bold'))
curProfLabel.pack()

#create message for current profile, pack into curProfFrame
curProfMes = Message(autoProfFrame, 
							textvariable= curProfText,
							justify= 'left',
							font= ('Arial', 16),
							width= 500)
curProfMes.pack()

#create message for remaining time
curProfMes = Message(autoProfFrame, 
							textvariable= timeRemainingText,
							justify= 'left',
							font= ('Arial', 16),
							width= 500)
curProfMes.pack()

#create frame for profile options
profOptFrame = Frame(autoProfFrame)
profOptFrame.pack()

#create previous profile button
prevProfButton = Button(profOptFrame, text= "PREV", width= 6)
prevProfButton.pack(side= LEFT, padx= 12, pady= 5)

#create restart profile button
restartProfButton = Button(profOptFrame, text= "RESTART", width= 10)
restartProfButton.pack(side= LEFT)

#create next profile button
nextProfButton = Button(profOptFrame, text= "NEXT", width= 6)
nextProfButton.pack(side= LEFT, padx= 12)



#------All Profiles display------#

#all profiles Label
allProfLabel = Label(autoProfFrame, text= "All Profiles", font= ('Arial', 30, 'bold'))
allProfLabel.pack(pady= 10)

#all profiles list box
allProfListBox = Listbox(autoProfFrame, height= 8, width= 32, font= ('Arial', 11))
allProfListBox.pack()

#import and clear all frame
importClearFrame = Frame(autoProfFrame)
importClearFrame.pack(pady= 10)

#import profiles button
importProfButton = Button(importClearFrame, 
							text= "Import", 
							width= 15, 
							command= importPressed)
importProfButton.pack(side= LEFT, padx= 12)

#clear profiles button
clearProfButton = Button(importClearFrame, text= "Clear All", width= 15)
clearProfButton.pack(side= RIGHT, padx= 12)


#------Start/Stop/E-Stop Control------#

autoStartStopFrame = Frame(autoControlTab)
autoStartStopFrame.pack(side= RIGHT, fill= 'y', padx= 30)

#Start button
autoStartButton = Button(autoStartStopFrame, 
						width= 6,
						height= 3,
						background= 'green',
						text= "START", 
						font= ('Arial', 20, 'bold'),
						#command= startPressed, # change to new func
						border= 5)
autoStartButton.pack(pady= 10)

#Stop button
autoStopButton = Button(autoStartStopFrame, 
						width= 6,
						height= 3,
						background= 'red',
						text= "STOP",
						font= ('Arial', 20, 'bold'),
						#command= stopPressed, # change to new func
						border= 5)
autoStopButton.pack(pady= 10)

#E-stop button
autoEStopButton = Button(autoStartStopFrame, 
						width= 6,
						height= 3,
						background= 'yellow',
						text= "E-STOP", 
						font= ('Arial', 20, 'bold'),
						#command= eStopPressed, # change to new func
						border= 5)
autoEStopButton.pack(pady= 10)


#---------------------#
#------Main Loop------#
#---------------------#

window.mainloop()



#----- OLD CODE -----#
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



curProfTextBox = Text(autoControlTab, height= 3, width= 50)
curProfTextBox.insert(index= END, chars= "RPM = ... \nAngle = ... \n Time = ...")
curProfTextBox.grid(row = 1, column= 0, rowspan= 3, columnspan= 6)
curProfTextBox.configure(state='disabled')

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
						text= profileList[0].printInfoText() + "\n\n" + profileList[1].printInfoText() + "\n\n" + profileList[2].printInfoText(),
						justify= 'left',
						font= ('Arial', 16),
						width= 500)
#allProfMes.pack()


#create scroll bar for all profiles frame
allProfScroll = Scrollbar(allProfFrame, orient= 'vertical')
allProfScroll.pack(side= RIGHT, fill= Y)
#allProfScroll.config(command= t.xview)  # add some text object 

"""