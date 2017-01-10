import urllib.request
import urllib.error
import sys


PRINT_LEVEL=1
def myprint(str, level=0):
	if (level >= PRINT_LEVEL):
		print(str)

def bleh():
	a = [1,2]
	b = [1,2]
	c = [1,2]
	
	return a,b,c

		
if __name__ == '__main__':
	training_data = {}
	training_data["a"] = [1,2]
	training_data["b"] = [1,2]
	a,b = training_data["a"], training_data["b"]
	