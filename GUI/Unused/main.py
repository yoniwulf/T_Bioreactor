from TimerClass import *
from GUIClass import *
import customtkinter
import serial
import threading




def runGUI():
	window = customtkinter.CTk()
	customtkinter.set_appearance_mode("light")
	guiObj = GUIClass(window)
	window.geometry("800x400")
	#use threading to separate serial receiving and main loop
	window.mainloop()
	#add popup to calibrate actuator

def runTimer():
	profTimer = ProfileTimer(0, 0, 0)
	
		


GUIThread = threading.Thread(target= runGUI, args=())
GUIThread.start()

timerThread = threading.Thread(target= runTimer, args=())
timerThread.start()
