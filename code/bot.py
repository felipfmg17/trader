from analisis import Ratio,EMA,Priceman
from pricer import downloadResource,extractPrice
import time
import queue
import threading


def fetchprice(exchange, host, resource, q):
	while True:
		data = downloadResource(host, resource)
		price = extractPrice(data, exchange)
		print(exchange,price)
		q.put(float(price))
		time.sleep(60)


def trade():


	pcs = None
	ema = EMA(aph):
	dev = Ratio(pcs,ptg)


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
		n = q.qsize()
		s = 0
		if n>0:
			for i in range(n):
				e = q.get()
				s += e
			s /= n
		d = dev.next( ema.next(s) )
		sendsignal(d, dst):

		time.sleep(60)


if __name__ == '__main__':
    trade()


