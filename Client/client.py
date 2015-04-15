# -*- coding: utf-8 -*-
#!/usr/bin/python3
import uuid
import urllib
# import urllib2
import time, threading
import os
import rsa
# from M2Crypto import RSA


def crypt(data, is_encrypt=True):
	# publickey = rsa.importKey(open('pub.pem', 'r').read())
	# privatekey = rsa.importKey(open('pri.pem', 'r').read())
	# with open('pri.pem') as privatefile:
	# 	keydata = privatefile.read()
	# print(keydata)
	# keydata = keydata.encode(encoding="utf-8")
	privatekey = rsa.PrivateKey.load_pkcs1(open('pri.pem', 'r').read())
	# privatekey = rsa.pem.load_pem(open('pri.pem', 'r').read(), 'RSA PRIVATE KEY')
	publickey = rsa.PublicKey.load_pkcs1(open('pub.pem', 'r').read())
	# publickey = rsa.pem.load_pem(open('pub.pem', 'r').read().encode(encoding="utf-8"), "RSA PUBLIC KEY")
	# publickey = privatekey
	# with open('pub.pem') as publickfile:
	# 	p = publickfile.read()
	# publickey = rsa.PublicKey.load_pkcs1(p)
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
	# rsa_Pub_Obj = RSA.load_pub_key("pub.pem")
	# rsa_Priv_Obj = RSA.load_key("pri.pem")

	# if is_encrypt:
	# 	encrypt_msg_pri = rsa_Priv_Obj.private_encrypt(msg, RSA.pkcs1_padding)
	# 	# encrypt_msg64_pri = encrypt_msg_pri.encode('base64').replace('\n','')
	# 	return encrypt_msg_pri
	# else:
	# 	plain = rsa_Pub_Obj.public_decrypt(encrypt_msg64, RSA.pkcs1_padding)
	# 	# plain = rsa_Pub_Obj.public_decrypt(encrypt_msg64.decode('base64'), RSA.pkcs1_padding)
	# 	return plain
		


result = crypt("12345678", True)
# print(result)
result = crypt(result, False)
print(result)

class Client(object):
	status = 0		#0 offline 1; 1 online
	tickDuration = 6
	requestDuration = 10
	captureDuration = 5;
	tickThread = None
	captureThread = None
	captureTimerThread = None
	lastCommand = None

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
			# if lastCommand != command:
				
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
	# if i == 1:
# 		client.captureThread.start()
# 		client.captureTimerThread.start()

	time.sleep(client.requestDuration)
# 	i = i + 1
	




