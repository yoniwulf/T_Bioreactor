from tkinter import Tk
from GUIClass import*

#----------------------------#
#--------main window---------#
#----------------------------#
window = Tk()
guiObj = GUIClass(window)
window.geometry("800x480")
window.mainloop()