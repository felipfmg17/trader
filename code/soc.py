import socket
import sys


def client():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	srv = ('localhost',10000)
	msg = b'hola soy felipe'
	sock.sendto(msg,srv)
	data, adr = sock.recvfrom(4096)
	print('echo:',data)


def server():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	srv = ('localhost',10000)
	sock.bind(srv)
	while True:
		print('waiting...')
		data, cli = sock.recvfrom(4096)
		print('message received:',cli,data)
		sock.sendto(b'me llego tu mensaje',cli)


def listen():
	soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	srv = ('localhost',10000)
	soc.bind(srv)
	while True:
		print('waiting')
		data, cli = soc.recvfrom(4096)
		sgn = str(data,'utf-8')
		print('message received:',cli,sgn)
		print(type(cli[0]),cli[0])




listen()
