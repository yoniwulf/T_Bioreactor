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
testTab = Frame(notebook)
notebook.add(manControlTab, text= "Manual Control")
notebook.add(autoControlTab, text= "Automatic Control")
notebook.add(testTab, text= "test tab ")
notebook.pack(expand= TRUE)

#declare variables
rpmVal = 0
angleVal = 0
profileList = []
curProfIndex = 0
curProfText = StringVar()
curProfText.set("RPM:           Angle:  \nTime:           00:00:00")





#---------------------#
#------Functions------#
#---------------------#


# function to update selected rpm value
def setRpm():
	global rpmVal
	
	if (int(rpmEntry.get()) > 200) or (int(rpmEntry.get()) < 0):
		messagebox.showwarning(title= "RPM out of range", message= "RPM must be between 0 and 200")

	else:
		rpmVal = rpmEntry.get()
		print("rpm set button clicked, entry rpm is " + str(rpmEntry.get())
				+ " rpmVal is " + str(rpmVal))

# function to update selected angle value
def setAngle():
	global angleVal

	if (int(angleEntry.get()) > 90) or (int(angleEntry.get()) < 0):
		messagebox.showwarning(title= "Angle out of range", message= "Angle must be between 0 and 90")

	else:
		angleVal = angleEntry.get()
		print("angle set button clicked, entry angle is " + str(angleEntry.get())
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
					text= " RPM"
					)
rpmDial.pack(pady= 10)

#rpm entry box label
rpmEntryLabel = Label(rpmFrame, text= "Set RPM:", font= ('Arial', 16))
rpmEntryLabel.pack()

#rpm entry box
rpmEntry = Entry(rpmFrame, font= ('Arial', 20), width= 5)
rpmEntry.pack()

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

#RPM dial
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

#angle entry box label
angleEntryLabel = Label(angleFrame, text= "Set Angle:", font= ('Arial', 16))
angleEntryLabel.pack()

#angle entry box
angleEntry = Entry(angleFrame, font= ('Arial', 20), width= 5)
angleEntry.pack()

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
autoProfFrame.pack(side= LEFT, fill= 'y', padx= 30)

#current profile Label, add to grid
curProfLabel = Label(autoProfFrame, text= "Current Profile", font= ('Arial', 30, 'bold'))
curProfLabel.pack()

#create message for current profile, pack into curProfFrame
curProfMes = Message(autoProfFrame, 
							textvariable= curProfText,
							justify= 'left',
							font= ('Arial', 16),
							width= 500)
curProfMes.pack()

#create frame for current profile, add to grid
prevNextFrame = Frame(autoProfFrame)
prevNextFrame.pack()

#create previous profile button
prevProfButton = Button(prevNextFrame, text= "PREV", width= 15)
prevProfButton.pack(side= LEFT, padx= 12, pady= 5)

#create next profile button
nextProfButton = Button(prevNextFrame, text= "NEXT", width= 15)
nextProfButton.pack(side= RIGHT, padx= 12)

#create restart profile button
restartProfButton = Button(autoProfFrame, text= "RESTART", width= 35)
restartProfButton.pack()

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