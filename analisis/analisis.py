import matplotlib.pyplot as plt
import math
import random
import pymysql
import time
import heapq as hp

class EMA:
	def __init__(self,a):
		self.a=a
		self.s=None

	def next(self,v):
		s,a = self.s, self.a
		self.s = v if s==None else a*v +(1-a)*s
		return self.s

class SMA:
	def __init__(self,vals):
		self.n = len(vals)
		self.vals = vals[:]
		self.ind = 0
		self.s = sum(vals)/len(vals)

	def next(self,v):
		vals,n,ind = self.vals,self.n,self.ind
		self.s = self.s - vals[ind]/n + v/n
		vals[ind] = v
		self.ind = (ind+1)%n
		return self.s

class Ratio:
	def __init__(self,vals):
		self.n = len(vals)
		self.vals = vals[:]
		self.ind = 0

	def next(self,v):
		vals,n,ind = self.vals,self.n,self.ind
		s = (v-vals[ind])/vals[ind]
		vals[ind] = v
		self.ind = (ind+1)%n
		return s

def calcSMA(vals,n):
	series = []
	s = 0
	for i in range(n):
		s += vals[i]
	s /= n
	series.append(s)
	for i in range(n,len(vals)):
		s -= vals[i-n]/n
		s += vals[i]/n
		series.append(s)
	return series

def calcEMA(vals,a):
	series = [vals[0]]
	for i in range(1,len(vals)):
		s = series[-1]*(1-a) + vals[i]*a
		series.append(s)
	return series

# pcs: prices to simulate in the form coinB/coinA
# cna: coinA
# aph: alpha for EMA
# tm: time in minutes to calculate Ratio
# ptg: percentage to buy or sel
def sim(pcs, cna, fee, aph, tm, ptg):
    #print('sim tm:',tm)
    lbuy, lsell = ptg,-ptg
    ema, dev = EMA(aph), Ratio([pcs[0]] * tm)
    ocna, cnb, fees = cna, 0, 0
    for p in pcs:
        d = dev.next( ema.next(p) )
        if d>lbuy and cna>0 :
            fees += cna * fee
            cna -= cna * fee
            cnb += cna / p
            cna = 0
        elif d<lsell and cnb>0 :
            cna = cnb * p
            cnb = 0
            fees += cna * fee
            cna -= cna * fee
    if cnb>0:
        cna = cnb * pcs[-1]
        fees += cna * fee
        cna -= cna * fee
    gain = (cna - ocna) / ocna
    return gain

def simg(pcs, cna, fee, aph, tm, ptg):
    lbuy, lsell = ptg,-ptg
    ema, dev, ems = EMA(aph), Ratio([pcs[0]] * tm), []
    ocna, cnb, sells, buys, fees = cna, 0, 0, 0, 0
    for i in range(len(pcs)):
        p = pcs[i]
        e = ema.next(p)
        ems.append(e)
        d = dev.next(e)
        if d>lbuy and cna>0 :
            fees += cna * fee
            cna -= cna * fee
            cnb += cna / p
            cna = 0
            buys += 1
            print('Buy:',i,p)
        elif d<lsell and cnb>0 :
            cna = cnb * p
            cnb = 0
            fees += cna * fee
            cna -= cna * fee
            sells += 1
            print('Sell:',i,p)
    if cnb>0:
        cna = cnb * pcs[-1]
        fees += cna * fee
        cna -= cna * fee
        sells += 1
    gain = (cna - ocna) / ocna


    print('Original coins A:',ocna)
    print('Final coins A: ',round(cna,2))
    print('Difference:',round(cna-ocna,2))
    print('Percentage gain:',round(gain*100,2),'%')
    print('Buys and sells:',buys)
    print('Fees percentage:',round(fees/cna*100,2),'%')

    plt.plot(pcs)
    plt.plot(ems)
    plt.show()

# load prices from database from date d0
# to d1, dates are given in secons from epoch
def loadPrices(d0,d1):
    db = pymysql.connect('localhost','root','root','crypto_prices')
    sql = """ SELECT  a.price as Price
    FROM coin_price as a
    JOIN currency_pair as b
    ON a.currency_pair_id = b.id
    JOIN exchange as c
    ON a.exchange_id = c.id
    WHERE c.name = \"bitso\"
    AND b.name = \"xrp_mxn\" """
    sql += ' AND a.date_time_sec > '  + str(d0)
    sql += ' AND a.date_time_sec < '  + str(d1)
    cursor = db.cursor()
    cursor.execute(sql)
    lines = cursor.fetchall()
    prices = [ e[0] for e in lines ]
    return prices;

# Generates a new random gen
#
def randgen(evm):
    gen = []
    lms = evm['lms']
    gen.append( random.uniform(lms[0][0],lms[0][1]) )
    gen.append( random.randrange(lms[1][0],lms[1][1]) )
    gen.append( random.uniform(lms[2][0],lms[2][1]) )
    rds = evm['rds']
    for i in range(len(rds)):
        gen[i] = round(gen[i],rds[i])
    gen = tuple(gen)
    return gen

def born(evm):
    gen = randgen(evm)
    gn = fitness(gen,evm)
    while gn<=0:
        gen = randgen(evm)
        gn = fitness(gen,evm)
    return (-gn,tuple(gen))

# Given a gen, calculates the percentage gain
# during a buy an sell simulation
def fitness(gen,evm):
    pcf = evm['pcf']
    pms = pcf + list(gen)
    return round(sim(*pms),evm['frd'])

# calculates adjacent spicimens to spc
# modifing the i property of spc wit val
def getadj(spc, i, val,evm):
    nspc = None
    gn, gen = -spc[0],spc[1]
    ngen = list(gen)
    ngen[i] = round(ngen[i]+val,evm['rds'][i])
    lms = evm['lms']
    if ngen[i]>=lms[i][0] and ngen[i]<=lms[i][1]:
        ngn = fitness(ngen,evm)
        if ngn>gn:
            nspc = (-ngn, tuple(ngen))
    return nspc

# Given a specimen u, generates all
# adjacent possible specimes
# vis is used to store visited specimes
# st is a priority queue for the next
# specimen to process
# psm stores perfect specimens which cannot be
# improved more
def dfs(u,vis,st,psm,evm):
    kds = 0
    for i in range(len(u[1])):
        tbl = evm['mtt'][i]
        for val in tbl:
            #print(i,val)
            v = getadj(u, i, val,evm)
            if v!=None  and v[1] not in vis:
                hp.heappush(st,v)
                vis.add(v[1])
                kds += 1
    if kds==0:
        psm.add(u)
        print('Perfect specimen:',u)

def mute(spc,evm):
    st, psm, vis, rps = [], set(), set(), 500
    hp.heappush(st, spc)
    vis.add(spc[1])
    while len(st)>0 and len(psm)<50 and rps>0:
        u = hp.heappop(st)
        dfs(u, vis, st, psm, evm)
        rps -= 1
    return psm

def repr(s1,s2):
    ngen = []
    for i in range(len(s1[1])):
        j = random.randint(2)
        if j==0:
            ngen.append(s1[1][i])
        else:
            ngen.append(s2[1][i])
    ngn = fitness(ngen)
    return (-ngn,tuple(ngen))





def test2():
    # show prices in the databases
    pcs = loadPrices(1514770796,1515912230)
    pcs = loadPrices(1515391551, 1515912230)
    ema = calcEMA(pcs,0.01)
    plt.plot(pcs)
    plt.plot(ema)
    plt.show()

def test3():
    mtt = []
    difs = [(i + 1) / 100 for i in range(10)] + [ (i+1)/1000 for i in range(5)]
    difs = difs + [-v for v in difs]
    idifs = [i + 1 for i in range(10)] + [15, 20, 30]
    idifs = idifs + [-v for v in idifs]
    mtt.append(difs)
    mtt.append(idifs)
    mtt.append(difs)

    ini = 1515391551
    fin = 1515909634
    pcs = loadPrices(ini, fin)
    pcf = [pcs, 100, 0.001]

    lms = []
    lms.append((0, 1))
    lms.append((5, 400))
    lms.append((0, 0.50))

    rds = [3,3,3]


    evm = {}
    evm['mtt'] = mtt
    evm['pcf'] = pcf
    evm['lms'] = lms
    evm['rds'] = rds
    evm['frd'] = 7

    spc = born(evm)
    print('first specimen:',spc)
    bspc = mute(spc,evm)
    for sp in bspc:
        print(sp)




test3()


