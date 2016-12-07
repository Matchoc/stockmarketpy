import matplotlib.pyplot as plt
from eveclicker import * #import eveclicker
import numpy
import sys
from time import sleep

if __name__ == '__main__':
	
	#a = {"bleh":2}
	#b = list(a.keys())
	#print(b[0])
	#sys.exit()
	
	#handle = getWindowByTitle("EVE - Miss Tadaruwa", True)
	handle = getWindowByTitle("Paint", False)
	updateEveScreen(handle[0])
	initScreenButtons()
	data = {}
	performTests(data)
	print(data["features"]["ratio_outer_brigthness_to_center_brightness_nuclei"])
	
	sys.exit()

	#a = boardToDebugRender(data["processing"]["binaryList"])
	a = colorize(data["processing"]["greenFeatures"])
	
	a = numpy.array(a)
	a = a.reshape(395,395)
	plt.imshow(a)
	#<matplotlib.image.AxesImage object at 0x04123CD0>
	plt.show()
	
	sys.exit()
	plt.plot(x, y, 'ro', xperim, yperim, 'g^')
	#plt.plot(xperim, yperim, 'g^')
	plt.axis([335, 345, 295, 305])
	plt.show()		
	
	
	
	handle = getWindowByTitle("Paint", False)
	updateEveScreen(handle[0])
	print(getEveScreen()[0:2])
	blurImage(5)
	a = getEveScreenNumpy()
	#a = numpy.array(a)
	#a = a.reshape(getEveScreenHeight(), getEveScreenWidth(), 3)
	plt.imshow(a)
	plt.show()
	print(getEveScreenNumpy())
	
	sys.exit()
	
	#handle = getWindowByTitle("EVE - Sir Tsukaya", True)
	#handle = getWindowByTitle("Paint", False)
	#updateEveScreen(handle[0])
	#initScreenButtons()
	#data = ProcessData()
	#performTests(data)
	
	#a = colorize(data.greenFeatures)
	
	#a = numpy.array(a)
	#a = a.reshape(395,395)
	#plt.imshow(a)
	#<matplotlib.image.AxesImage object at 0x04123CD0>
	#plt.show()
	
	#print(str(data))