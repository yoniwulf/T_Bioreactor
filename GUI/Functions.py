#NOT USED#


#---------------------#
#------Functions------#
#---------------------#

from tkinter import*
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkdial import*
#from GUI import*

"""
def setRpm():
	#global rpmVal
	#global rpmDialVal
	#global rpmEntryText

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
					+ " rpmVal is " + str(GUI.rpmVal))
			
			GUI.rpmDial.set(setInt) #for testing
	
	#if a decimal or non integer value is entered
	except ValueError:
		messagebox.showwarning(title= "Non-whole number RPM", message= "RPM must be a whole number")
		GUI.rpmEntryText.set('0')
"""