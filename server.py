#!/usr/bin/python3 -u
# -u ... unbuffered output for service

import socket, config
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

# Configuration
https = False

# Generate certificates for HTTPS
# openssl genrsa 2048 > data/host.key
# openssl req -new -x509 -nodes -sha256 -days 365 -key data/host.key -out data/host.cert

class StoreHandler(BaseHTTPRequestHandler):
	def do_GET(s):
		if s.path == '/':
			s.send_response(200)
			s.send_header('Content-type', 'text/html')
			s.end_headers()
			s.wfile.write(getForm().encode())
		elif s.path == '/display':
			s.send_response(200)
			s.send_header('Content-type', 'image/png')
			s.end_headers()
			fh = open(config.image, 'rb')
			s.wfile.write(fh.read())
			fh.close()
		else:
			s.send_response(204)
			s.end_headers()

	def do_POST(s):
		length = s.headers['content-length']
		data = s.rfile.read(int(length))
		data = parse_qs(data.decode())

		action = data['action'][0];
		print('Action: ' + action);
		if action == 'save':
			content = data['content'][0];

			if content != '':
				fh = open(config.textFile, 'w')
				fh.write(content)
				fh.close()

			# Force Update
			if 'force' in data and data['force'][0]=='true':
				print('Forcing update')
				import os
				command = 'sudo -u pi sh -c "cd ' +  os.getcwd() + '/ && ./runme.sh"'
				os.system(command + ' &')
		elif action == 'reboot':
			print('Rebooting')
			import os
			command = 'sudo reboot'
			os.system(command + ' &')
		elif action == 'poweroff':
			print('Power off')
			import os
			command = 'sudo powerdown'
			os.system(command + ' &')

		s.do_GET()

def getForm():
	global form
	# Read form first
	if form=='':
		fh = open(config.template)
		form = fh.read()
		fh.close()
	# Inject content
	formTemp = form
	fh = open(config.textFile)
	formTemp = formTemp.replace('<!-- textarea -->', fh.read())
	fh.close()
	return(formTemp)

# Start Webserver
form = ''
# Check Permissions
if config.port < 1024:
	import os, sys
	if os.geteuid()!=0:
		exit("You need root privileges to run a server with a port < 1024.\nPlease try again with: sudo " + sys.argv[0])

server = HTTPServer(('', config.port), StoreHandler)

# Protocol
if config.https==True:
	import ssl
	server_protocol = 'https'
	server.socket = ssl.wrap_socket(server.socket, keyfile=config.https_keyfile, certfile=config.https_certfile, server_side=True)
else:
	server_protocol = 'http'

# Port
if (config.port==80 and https==False) or (config.port==443 and https==True):
	server_port=''
else:
	server_port=':' + str(port)

print('Starting Webserver at ' + server_protocol + '://' + socket.gethostname() + server_port + '/')
print('Press CTRL+C to end')
server.serve_forever()
