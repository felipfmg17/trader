from analisis import Ratio,EMA,Priceman
from pricer import downloadResource,extractPrice
import time
import queue
import threading
import pymysql
import socket

# download the price from a exchange every 60 seconds
# the price is pushed in to q
def fetchprice(exchange, host, resource, q):
	while True:
		data = downloadResource(host, resource)
		price = extractPrice(data, exchange)
		print(exchange,price)
		q.put(float(price))
		time.sleep(60)

# sends a datagram with a signa indicating either buy or sell
# dst is a list with ip,port pairs
def sendsignal(sgn, dst):
	soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	msg = bytes(str(sgn),'utf-8')
	for adr in dst:
		soc.sendto(msg,adr)
	soc.close()

# start a bot for trading
def trade(aph,tm,ptg,rsc,dst):
	ema,dev,q = EMA(aph),None,queue.Queue()
	for r in rsc:
		r.append(q)
		threading.Thread(target=fetchprice, args=r).start()
	time.sleep(10)
	while True:
		n,p = q.qsize(),0
		if n>0:
			for i in range(n):
				e = q.get()
				p += e
			p /= n
		if dev==None and p>0:
			dev = Ratio([p]*tm, ptg)
		if dev!=None:
			d = dev.next( ema.next(p) )
			print(d,p)
			threading.Thread(target=sendsignal, args=(d,dst) ).start()
		time.sleep(60)


def test():
	gen = input().split()
	aph = float(gen[0])
	tm = int(gen[1])
	ptg = float(gen[2])
	nrsc = int(input())
	rsc = []
	for i in range(nrsc):
		rsc.append(input().split())
	ndst = int(input())
	dst = []
	for i in range(ndst):
		adr = input().split()
		adr[1] = int(adr[1])
		dst.append( tuple(adr) )
	trade(aph,tm,ptg,rsc,dst)

if __name__ == '__main__':
	test()

