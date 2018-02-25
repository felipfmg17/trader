from analisis import Ratio,EMA,Priceman
from pricer import downloadResource,extractPrice


def trade(pcs, aph, tm, ptg):
	ema = EMA(aph)
	dev = Ratio(pcs, ptg)

	while True:
		p = nextprice()
		d = dev.next( ema.next(p) )
		sendsignal(d)

