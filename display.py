#!/usr/bin/python3

import sys
sys.path.append('waveshare/')
import epd7in5
import time, traceback
from PIL import Image,ImageDraw,ImageFont

# Argument
if len(sys.argv) < 2:
	print("Usage: " + sys.argv[0] + " picture")
	quit()

picture = sys.argv[1]
try:
	epd = epd7in5.EPD()
	epd.init()
	#print("Clearing")
	epd.Clear(0xFF)

	#print("Displaying picture " + picture)
	MyImage = Image.open(picture)
	epd.display(epd.getbuffer(MyImage))
	time.sleep(2)

	epd.sleep()
		
except:
	print('traceback.format_exc():\n%s', traceback.format_exc())
	exit()
