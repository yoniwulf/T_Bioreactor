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
		if self.rpm < 100:
			self.infoText = self.infoText[0:9] + "  " + self.infoText[9:]
		return self.infoText
	
	def printInfoTextLine(self):
		self.infoText = " " + str(self.rpm,) + "       " + str(self.angle) + f"       {self.hour:02}:{self.min:02}:{self.sec:02}"
		if self.rpm < 100:
			self.infoText = self.infoText[0:4] + "  " + self.infoText[4:]
		return self.infoText