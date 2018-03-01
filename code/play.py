import socket as skt
import sys
import time
import pickle
import threading

def send(soc,obj):
	msg = pickle.dumps(obj)
	size = str(len(msg)).zfill(15).encode()
	snt = 0
	while snt<10:
		n = soc.send(size[snt:])
		snt += n
	snt = 0
	while snt<len(msg):
		n = soc.send(msg[snt:min(snt+4096,len(msg))])
		snt += n

def recv(soc):
	size = b''
	rcv = 0
	while rcv<10:
		buf = soc.recv(15)
		rcv += len(buf)
		size += buf
	size = int(size.decode())
	msg = b''
	rcv = 0
	while rcv<size:
		buf = soc.recv(min(size-rcv,4096))
		if len(buf)==0:
			break
		rcv += len(buf)
		msg += buf
	obj = pickle.loads(msg)
	return obj
	
def mkthread(f,p):
	th = threading.Thread(target=f,args=p)
	th.start()
	return th

