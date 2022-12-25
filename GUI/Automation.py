from tkinter import*
from tkinter import ttk

import pandas as pd


'''
* need to implement out of range detection for input values 
	(ex: rpm too high, mins > 60, angle not multiple of 15 degrees)


'''

# loop through every cell and check for NaN. send warning and stop from proceding
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

"""
	def printInfoText(self):
		self.infoText = "RPM: " + str(self.rpm,) + "    Angle: " + str(self.angle) + f"\nTime:           {self.hour:02}:{self.min:02}:{self.sec:02}" + f"\nRemaining:  {self.hour:02}:{self.min:02}:{self.sec:02}" #change to actual time left
		return self.infoText
"""



profileList = []

profileDF = pd.read_excel('test_mixing_profiles.xlsx')
#rpmVal = profileDF.iat[1,1]
#print(rpmVal)

if profileDF.isnull().any().any():
	print("found a NaN")

elif (profileDF < 0).any().any():
	print("found a negative number")

else:
	for i in range(len(profileDF)):	
		tempProf = MixProfile(profileDF.iat[i,0], 
									profileDF.iat[i,1],
									profileDF.iat[i,2],
									profileDF.iat[i,3],
									profileDF.iat[i,4])
		profileList.append(tempProf)
		print(profileList[i].rpm)

"""
numError = False
debugCnt = 0

for i in range(len(profileDF)):
	for j in range(4):
		if profileDF.iat[i,j] == NULL:
			numError = True
			break

	if (numError):
		print("found NaN, skipping profile")
	
	else:
		print ("clean profile #" + str(debugCnt))
		tempProf = MixProfile(profileDF.iat[i,0], 
								profileDF.iat[i,1],
								profileDF.iat[i,2],
								profileDF.iat[i,3],
								profileDF.iat[i,4])
		profileList.append(tempProf)
		print(profileList[debugCnt].rpm)
		debugCnt += 1
		
	
	
	numError = False
	
	
	#print(profileList[debugCnt].rpm)


"""


#-------Classes Example Code---------#
"""
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

p1 = Person("John", 36)

print(p1.name)
print(p1.age)



class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

  def myfunc(self):
    print("Hello my name is " + self.name)

p1 = Person("John", 36)
p1.myfunc()

  """