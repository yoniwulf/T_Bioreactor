from tkinter import*
from tkinter import ttk

#------Notes/Ideas------#
""" 
Ideas:
* set buttons change variables (global?) of rpm and angle
* once user presses start, new values will be sent to arduino
* change set buttons to different color when user has changed value
	* user must click set to update value
* change start button to "update" when new values for rpm or angle are set
 """

#------Setup------#

# declare main window
window = Tk()

# declare notebook to allow different tabs
notebook = ttk.Notebook(window)

#declare manual and automatic control tabs, add to notebook and grid
manControlTab = Frame(notebook)
autoControlTab = Frame(notebook)
notebook.add(manControlTab, text= "Manual Control")
notebook.add(autoControlTab, text= "Automatic Control")
notebook.grid(row=0, column= 0)

#declare variables
rpmVal = 0
angleVal = 0



#------Functions------#

# function to update selected rpm value
def setRpm():
	rpmVal = rpmScale.get()
	print("rpm set button clicked, scale rpm is " + str(rpmScale.get())
			+ " rpmVal is " + str(rpmVal))

# function to update selected angle value
def setAngle():
	angleVal = angleScale.get()
	print("angle set button clicked, scale angle is " + str(angleScale.get())
			+ " angleVal is " + str(angleVal))

# function to send rpmVal, angleVal, and start command (needed?) to arduino
def startPressed():
	# send rpmVal and angleVal to arduino
	print("Start Button pressed, rpmVal: " + str(rpmVal) + ", angleVal: " + str(angleVal))

# function to send stop command to arduino
def stopPressed():
	print("Stop Button pressed, slowing down")

# function to send e-stop command to arduino
def eStopPressed():
	print("Emergency Stop Button pressed, shutting down all systems")





#------RPM Control------#

# label for RPM control section
rpmLabel = Label(manControlTab, text= "RPM", font= ('Arial', 30, 'bold'), width= 7)

# add label to grid
rpmLabel.grid(row= 0, column= 0)

# define scale to choose RPM
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

# add scale to grid
rpmScale.grid(row= 1, column= 0, rowspan= 3)

# define set button to call setRpm function
rpmSetButton = Button(manControlTab, 
						text= "SET", 
						command= setRpm,
						padx= 10,
						pady= 10,
						border= 5,
						background= 'green')

# add set button to grid
rpmSetButton.grid(row= 5, column= 0, pady= 5)


#------Angle Control------#

# label for angle control section
angleLabel = Label(manControlTab, text= "ANGLE", font= ('Arial', 30, 'bold'), width= 7)

# add label to grid
angleLabel.grid(row= 0, column= 1)

# define scale to choose Angle
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
					showvalue= 0
					)

# add scale to grid
angleScale.grid(row= 1, column= 1, rowspan= 3)

# define set button to call setAngle function
angleSetButton = Button(manControlTab, 
						text= "SET", 
						command= setAngle,
						padx= 10,
						pady= 10,
						border= 5,
						background= 'green')

# add set button to grid
angleSetButton.grid(row= 5, column= 1, pady= 5)

#------Start/Stop/E-Stop Control------#

# define start button to call startPressed function
startButton = Button(manControlTab, 
						width= 6,
						height= 3,
						background= 'green',
						text= "START", 
						font= ('Arial', 20, 'bold'),
						command= startPressed,
						border= 5)

# add start button to grid
startButton.grid(row= 1, column= 2, padx= 5)

# define stop button to call stopPressed function
stopButton = Button(manControlTab, 
						width= 6,
						height= 3,
						background= 'red',
						text= "STOP",
						font= ('Arial', 20, 'bold'),
						command= stopPressed,
						border= 5)

# add stop button to grid
stopButton.grid(row= 2, column= 2, padx= 5)

# define e-stop button to call eStopPressed function
eStopButton = Button(manControlTab, 
						width= 6,
						height= 3,
						background= 'yellow',
						text= "E-STOP", 
						font= ('Arial', 20, 'bold'),
						command= eStopPressed,
						border= 5)

# add e-stop button to grid
eStopButton.grid(row= 3, column= 2, padx= 5)


#main window loop
window.mainloop()
