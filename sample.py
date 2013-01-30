#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys
import subprocess

reload(sys)
sys.setdefaultencoding("utf-8")

def main():
	ret = subprocess.call("jshint.py --path=test", shell=True) 
	if ret == 0:
		pass
	else:
		print "your code didn't honor jshint"

if __name__ == "__main__":
    main()

