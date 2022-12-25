from tkinter import*

class MixProfile:
	def __init__(self, rpmIn, angleIn, hourIn, minIn, secIn):
		self.rpm = rpmIn
		self.angle = angleIn
		self.hour = hourIn
		self.min = minIn
		self.sec = secIn
		self.infoText = ""

	def printInfoTextReturn(self):
		self.infoText = "RPM: " + str(self.rpm,) + "    Angle: " + str(self.angle) + f"\nTime:           {self.hour:02}:{self.min:02}:{self.sec:02}"
		return self.infoText
	
	def printInfoTextLine(self):
		self.infoText = "RPM: " + str(self.rpm,) + "    Angle: " + str(self.angle) + f"    Time: {self.hour:02}:{self.min:02}:{self.sec:02}"
		return self.infoText