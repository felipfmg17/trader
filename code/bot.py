from analisis import Ratio,EMA,Priceman
from pricer import downloadResource,extractPrice
import time
import queue
import threading
import pymysql


def fetchprice(exchange, host, resource, q):
	while True:
		data = downloadResource(host, resource)
		price = extractPrice(data, exchange)
		print(exchange,price)
		q.put(float(price))
		time.sleep(60)

def getprices(n,exchange,cur_pair):
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

def trade():

	gen = [0.00852, 991, 0.03177]
	aph,tm,ptg = gen
	ema = EMA(aph)
	dev = None

	#pcs = getprices(gen[1],'bitfinex','xrp_usd')
	#dev = Ratio(pcs,gen[2])


	# start fetching threads with queue prices

	rsc = []
	rsc.append(['bitfinex', 'api.bitfinex.com','/v1/pubticker/xrpusd'])
	rsc.append(['hitbtc','api.hitbtc.com','/api/2/public/ticker/XRPUSDT'])
	rsc.append(['bitstamp','www.bitstamp.net','/api/v2/ticker/xrpusd'])
	rsc.append(['bittrex','bittrex.com','/api/v1.1/public/getticker?market=USDT-XRP'])
	rsc.append(['cex.io','cex.io','/api/ticker/XRP/USD'])

	dst = []
	dst.append(['localhost',50502])
	dst.append(['localhost',50503])

	q = queue.Queue()
	for r in rsc:
		r.append(q)
		th = threading.Thread(target=fetchprice, args=r)
		th.start()

	while True:
		n,p = q.qsize(),0
		if n>0:
			for i in range(n):
				e = q.get()
				p += e
			p /= n
		if dev==None:
			dev = Ratio([p]*tm, ptg)
		d = dev.next( ema.next(p) )
		print(d,p)
		time.sleep(60)


def test():
	trade()

def test2():
	ar = getprices(10,'bitfinex','xrp_usd')
	print(ar)

if __name__ == '__main__':
	test()

