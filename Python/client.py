#!/usr/bin/python3
import uuid
import urllib
# import urllib2
import time, threading
import os

class Client(object):
	status = 0		#0 offline 1; 1 online
	tickDuration = 10
	requestDuration = 10
	captureDuration = 5;
	tickThread = None
	captureThread = None
	captureTimerThread = None

	def __init__(self):
		super(Client, self).__init__()


	def __getMac(self):
		node = uuid.getnode()
		mac = uuid.UUID(int = node).hex[-12:]
		print(mac)
		return mac

	def sendTick(self):
		try:
			print("Sending Tick...")
			url = ''
			values = {}
			data = urllib.urlencode(values)
			req = urllib2.Request(url, data, timeout=5)
			response = urllib2.urlopen(req)
			return True
		except Exception:
			return False

	def getCommandFromServer(self):
		try:
			# url = 'http://www.baidu.c'
			# values = {}
			# data = urllib.urlencode(values)
			# req = urllib2.Request(url, data, timeout=5)
			# response = urllib2.urlopen(req)
			print("Get command from server...")
			self.__execShellCommand("ls -al")
			return True
		except Exception:
			return False

	def capturePackets(self, keyword, timeout):
		# print(timeout)
		# command = "sudo tcpdump -w target.cap '(((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'"
		self.captureDuration = timeout
		print("Capture packets...")
		self.__execShellCommand("sudo tcpdump -w target2.cap")
		return

	def killCapturePackets(self):
		os.popen("killall -9 tcpdump")
		self.captureThread.terminnate()
		self.captureThread.kill()

	def __execShellCommand(self, command):
		try:
			result = os.popen(command).read()
			return True
		except Exception:
			return False

		
def sendTickThread(client):
	#Tick Thread
	while True:
		client.sendTick()
		time.sleep(client.tickDuration)

def capturePacketsThread(client):
	try:
		client.capturePackets("keyword", 5)
		print("Capture finished.")
	except Exception:
		return False

def killCapturePacketsThread(client):
	try:
		time.sleep(client.captureDuration)
		client.killCapturePackets()
		print("Capture thread killed.")
		return True
	except Exception:
		return False

client = Client()

client.tickThread = threading.Thread(target=sendTickThread, args=(client,), name='tickThread')
client.tickThread.start()

client.captureThread = threading.Thread(target=capturePacketsThread, args=(client,), name='captureThread')

client.captureTimerThread = threading.Thread(target=killCapturePacketsThread, args=(client,), name='killCaptureThread')



i = 0
#Main thread
while True:
	client.getCommandFromServer()
	if i == 1:
		client.captureThread.start()
		client.captureTimerThread.start()

	time.sleep(client.requestDuration)
	i = i + 1
	




