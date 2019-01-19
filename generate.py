#!/usr/bin/python3

import config

def checkConnection():
	timeout = 5
	import urllib.request
	try:
		response=urllib.request.urlopen(config.checkURL,timeout=timeout)
		return True
	except urllib.error.URLError as err: pass
	print('No internet connection!')
	quit()
	return False

def getTime(timeFormat):
	import locale, datetime
	locale.setlocale(locale.LC_ALL, '')
	if hasattr(config,'setToday') and config.setToday != '':
		#timeFormatTextInput
		dt = datetime.datetime.strptime(config.setToday, config.timeFormatTextInput)
	else:
		dt = datetime.datetime.now()
	return dt.strftime(timeFormat)

def getFile(src):
	import urllib.request
	if src.startswith('http'):
		return(urllib.request.urlopen(src))
	else:
		return(src)

def parseAccuweather(src):
	import xml.etree.ElementTree
	ns = {'ns0': 'http://www.accuweather.com'}
	f = getFile(src)
	e = xml.etree.ElementTree.parse(f)
	#xml.etree.ElementTree.dump(e)

	# Now: currentconditions->temperature , currentconditions->weathertext
	temp = e.findtext('./ns0:currentconditions/ns0:temperature', '/', ns)
	weather = e.findtext('./ns0:currentconditions/ns0:weathertext', '/', ns)
	weatherNow = temp + ' °C, ' + weather
	#print('Now: ' + temp + ' °C, ' + weather)

	# Today: forecast->day number="1"->daytime->lowtemperature to forecast->day number="1"->daytime->hightemperature , forecast->day number="1"->daytime->txtshort
	day = e.find('./ns0:forecast/ns0:day[@number="1"]/ns0:daytime', ns)
	#xml.etree.ElementTree.dump(day)
	templow = day.findtext('./ns0:lowtemperature', '/', ns)
	temphigh = day.findtext('./ns0:hightemperature', '/', ns)
	weatherday = day.findtext('./ns0:txtshort', '/', ns)
	if templow==temphigh:
		#print('Today: ' + templow + ' °C, ' + weatherday)
		weatherDay = templow + ' °C, ' + weatherday
	else:
		#print('Today: ' + templow + ' ' + config.weatherFromText + ' ' + temphigh + ' °C, ' + weatherday)
		weatherDay = templow + ' ' + config.weatherFromText + ' ' + temphigh + ' °C, ' + weatherday
		
	# Return
	return(weatherNow,weatherDay)

def centerPos(image, draw, text, font):
	(w, h) = draw.textsize(text, font=font)
	return(int((InkImage.size[0]-w)/2))

def removeComments(string):
	import re
	pattern = '^#.*\r?\n?'
	regex = re.compile(pattern, re.MULTILINE)
	def _replacer(match):
		if match:
			return ''
		else:
			return match
		print(match)
	return regex.sub(_replacer, string)

def removeLines(string, number):
	lines = string.splitlines(True)
	return ''.join(lines[0:number])

def dateFilter(string, filter):
	import datetime
	returnString = ''
	if hasattr(config,'setToday') and config.setToday != '':
		today = datetime.datetime.strptime(config.setToday, config.timeFormatTextInput)
	else:
		today = datetime.datetime.now()
	today = datetime.datetime(today.year, today.month, today.day) # Strip time	
	# Compare each date
	for line in string.splitlines(True):
		# dd.mm.yyyy
		startPos = 0
		endPos = config.timeFormatTextInputLen
		try:
			dateStart = datetime.datetime.strptime(line[startPos:endPos], config.timeFormatTextInput)
		except ValueError:
			returnString += line
			continue
		# Duration dd.mm.yyyy-dd.mm.yyyy
		if line[config.timeFormatTextInputLen] == '-':
			startPos = config.timeFormatTextInputLen+1
			endPos = startPos + config.timeFormatTextInputLen
			dateEnd = datetime.datetime.strptime(line[startPos:endPos], config.timeFormatTextInput)
		else:
			dateEnd = dateStart
		#print('date >= today - ' + date.strftime('%d.%m.%Y %H:%M:%S') + ' >= ' + today.strftime('%d.%m.%Y %H:%M:%S'))
		if (filter == 'today' and today >= dateStart and today <= dateEnd):
			returnString += line
			continue
		if (filter == 'future' and dateEnd >= today):
			returnString += line
			continue
		if (filter == 'output'):
			line = line.replace(dateStart.strftime(config.timeFormatTextInput) + '-' + dateEnd.strftime(config.timeFormatTextInput), dateStart.strftime(config.timeFormatTextOutput) + '-' + dateEnd.strftime(config.timeFormatTextOutput))
			line = line.replace(dateStart.strftime(config.timeFormatTextInput), dateStart.strftime(config.timeFormatTextOutput))
			returnString += line
			continue
		if (filter == 'weeks'):
			if 'prevWeekStart' not in locals():
				prevWeekStart = dateStart.strftime(config.timeFormatWeek)
				prevWeekEnd = dateEnd.strftime(config.timeFormatWeek)
				returnString += " \n"
			elif prevWeekStart <= dateStart.strftime(config.timeFormatWeek) <= prevWeekEnd or \
			prevWeekStart <= dateEnd.strftime(config.timeFormatWeek) <= prevWeekEnd:
				returnString += " \n"
			else:
				returnString += 'X' + "\n"
			prevWeekStart = dateStart.strftime(config.timeFormatWeek)				
			prevWeekEnd = dateEnd.strftime(config.timeFormatWeek)
			continue

	return returnString

def drawWeeklines(string, draw, font, startY, x1, x2):
	counter=0
	stringExploded = string.splitlines(False)
	for line in stringExploded:
		if line.startswith('X'):
			(w, h) = draw.textsize("\n".join(stringExploded[:counter])+'XX', font=font)
			draw.line([(x1,startY + h), (x2,startY + h)], fill = 0)
		counter+=1

# Main
checkConnection()
(weatherNow,weatherDay) = parseAccuweather(config.weatherSrc)
headline = getTime(config.timeFormatMain)
update  = getTime(config.timeFormatUpdate)

# Draw
from PIL import Image,ImageDraw,ImageFont,ImageOps
InkImage = Image.new('1', (config.displayWidth, config.displayHeight), 255)  # 255: clear the frame
InkImage.paste(Image.open("assets/background-landscape.bmp"))# Paste to override different color palettes
draw = ImageDraw.Draw(InkImage)
fontHeader = ImageFont.truetype(config.font, config.fontsizeHeader)
fontText = ImageFont.truetype(config.font, config.fontsizeText)
fontUpdate = ImageFont.truetype(config.font, config.fontsizeUpdate)

# Headline (bold)
draw.text((centerPos(InkImage, draw, headline, fontHeader), 5), headline, font = fontHeader, fill = 0)
draw.text((centerPos(InkImage, draw, headline, fontHeader)+1, 5), headline, font = fontHeader, fill = 0)

# Weather
draw.text((100, 40), config.weatherNowText + ':' + "\n" + config.weatherTodayText + ':', font = fontHeader, fill = 0)
draw.text((185, 40), weatherNow + "\n" + weatherDay, font = fontHeader, fill = 0)

# Text
f = open(config.textFile, 'r')
text = removeLines(dateFilter(removeComments(f.read()),'future'), config.maxLines)
draw.text((22, 110), dateFilter(text,'output'), font = fontText, fill = 0)
# Text today bold
draw.text((23, 110), dateFilter(dateFilter(text,'today'),'output'), font = fontText, fill = 0)

# Weeklines
weeks = dateFilter(text,'weeks')
drawWeeklines(weeks, draw, fontText, 110, 20, config.displayWidth-20)

# Update
draw.text((619, 375), update, font = fontUpdate, fill = 0)
	
# Generate Image
if config.inverse:
	InkImage = InkImage.convert('L')
	InkImage = ImageOps.invert(InkImage)
	InkImage = InkImage.convert('1')
InkImage.save(config.image,'PNG')
