from analisis import Ratio,EMA,Priceman
from pricer import downloadResource,extractPrice
import time
import queue
import threading
import pymysql
import socket


def fetchprice(exchange, host, resource, q):
	while True:
		data = downloadResource(host, resource)
		price = extractPrice(data, exchange)
		print(exchange,price)
		q.put(float(price))
		time.sleep(60)

def lastnprices(n, exchange, cur_pair):
	db = pymysql.connect('localhost','root','root','pricer')
	sql = """ SELECT Price  FROM (
	SELECT * FROM (
	SELECT  a.price as Price, a.date_time_sec as Seconds
	FROM coin_price as a
	JOIN currency_pair as b
	ON a.currency_pair_id = b.id
	JOIN exchange as c
	ON a.exchange_id = c.id
	WHERE c.name = \"{}\"
	AND b.name = \"{}\"
	ORDER BY a.date_time_sec DESC
	LIMIT {} ) sub
	ORDER BY Seconds ASC) sub2 """.format(exchange,cur_pair,n)
	cursor = db.cursor()
	cursor.execute(sql)
	lines = cursor.fetchall()
	prices = [ e[0] for e in lines ]
	return prices;

def sendsignal(sgn, dst):
	soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	msg = bytes(str(sgn),'utf-8')
	for adr in dst:
		soc.sendto(msg,adr)
	soc.close()


def trade(aph,ema,dev,rsc,dst):

	gen = [0.00852, 991, 0.03177]
	aph,tm,ptg = gen
	ema = EMA(aph)
	dev = None

	rsc = []
	rsc.append(['bitfinex', 'api.bitfinex.com','/v1/pubticker/xrpusd'])
	rsc.append(['hitbtc','api.hitbtc.com','/api/2/public/ticker/XRPUSDT'])
	rsc.append(['bitstamp','www.bitstamp.net','/api/v2/ticker/xrpusd'])
	rsc.append(['bittrex','bittrex.com','/api/v1.1/public/getticker?market=USDT-XRP'])
	rsc.append(['cex.io','cex.io','/api/ticker/XRP/USD'])

	dst = []
	dst.append(('localhost',10000))

	q = queue.Queue()
	for r in rsc:
		r.append(q)
		th = threading.Thread(target=fetchprice, args=r)
		th.start()
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
			th = threading.Thread(target=sendsignal, args=(d,dst) )
			th.start()
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
	ndst = int(input()):
	dst = []
	for i in range(ndst):
		dst.append(tuple(input().split()))



	trade()

if __name__ == '__main__':
	test()

