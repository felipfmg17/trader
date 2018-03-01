import socket as skt
import sys
import time



def send(soc,msg):
	size = str(len(msg)).zfill(10).encode()
	snt = 0
	while snt<10:
		n = soc.send(size[snt:])
		snt += n
	snt = 0
	while snt<len(msg):
		n = soc.send(msg[snt:min(snt+4096,len(msg))])
		print(n)
		snt += n


def recv(soc):
	size = b''
	rcv = 0
	while rcv<10:
		buf = soc.recv(10)
		rcv += len(buf)
		size += buf
	size = int(size.decode())
	msg = b''
	rcv = 0
	while rcv<size:
		buf = soc.recv(min(size-rcv,4096))
		if len(buf)==0:
			break
		print(len(buf))
		rcv += len(buf)
		msg += buf
	print(len(msg))
	

def client():
	soc = skt.socket()
	soc.connect(('',50001))
	msg = b'0123456789'*1000 
	send(soc,msg)

def server():
	srv = skt.socket()
	srv.bind(('',50001))
	srv.listen(1)
	soc,adr = srv.accept()
	recv(soc)

if sys.argv[1]=='0':
	server()
else:
	client()