import sys 
import re
if __name__ =="__main__":
	args_passed = "Null"
	print(len(sys.argv))
	try:  #See if arguments are passed.  
		args_passed = sys.argv[1]
	except: 
		args_passed = "No arguments passed" 
	finally: 
		lineContent = args_passed
		print(lineContent)
		
