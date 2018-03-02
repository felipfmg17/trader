import math
import random
import time
import pymysql
import threading
import pickle
import socket
import queue
import sys
import play
import matplotlib.pyplot as plt
import heapq as hp
from red_black_dict_mod import RedBlackTree

class EMA:
	def __init__(self,a):
		self.a = a
		self.s = None

	def next(self,v):
		s,a = self.s, self.a
		self.s = v if s==None else a*v + (1-a)*s
		return round(self.s,3)

def calcEMA(vals,a):
    series = [vals[0]]
    for i in range(1,len(vals)):
        s = series[-1]*(1-a) + vals[i]*a
        series.append(s)
    return series

# Ratio using Red Black Tree
# returns 1: buy, 0: do nothing, -1: sells
class Ratio:
    def __init__(self,vals,ptg):
        self.n = len(vals)
        self.vals = vals[:]
        self.ind = 0
        self.ptg = ptg
        tr = RedBlackTree()
        for i in range(self.n):
            if not vals[i] in tr:
                tr[vals[i]] = set()
            tr[vals[i]].add(i)
        self.tr = tr

    def next(self,v):
        vals,n,ind,ptg,tr = self.vals,self.n,self.ind,self.ptg,self.tr
        inds = []

        # searching for low values
        lim = v/(1+ptg)
        it = tr.minimum
        while it and it.key<=lim:
            for e in it.value:
                u = (e-ind+n)%n
                inds.append(u)
            it = it.successor

        # searching for high values
        lim = v/(1-ptg)
        it = tr.maximum
        while it and it.key>=lim:
            for e in it.value:
                u = (e-ind+n)%n
                inds.append(u)
            it = it.predecessor


        # get the last added value from inds
        s = 0
        if len(inds)>0:
            u = (max(inds)+ind)%n
            if vals[u]>v:
                s = -1
            elif vals[u]<v:
                s = 1

        # remove ind and vals[ind] from tr
        pv = vals[ind]
        mp = tr[pv]
        mp.remove(ind)
        if len(mp)==0:
            del tr[pv]

        # add ind and v to tr
        if v not in tr:
            tr[v] = set()
        tr[v].add(ind)
        vals[ind] = v
        self.ind = (ind+1)%n

        return s

# search the first point which compares less than per or max than per
# returns 1: buy, 0: do nothing, -1: sells
class Ratiog:
    def __init__(self,vals,per):
        self.n = len(vals)
        self.vals = vals[:]
        self.ind = 0
        self.per = per

    def next(self,v):
        vals,n,ind,per = self.vals,self.n,self.ind,self.per
        s = 0
        for i in range(n):
            j = (ind-i-1+n)%n
            if (v-vals[j])/vals[j]>per:
                s = 1
                break
            if (v-vals[j])/vals[j]<-per:
                s = -1
                break
        vals[ind] = v
        self.ind = (ind+1)%n
        return s

class Priceman:
    def __init__(self,d0,d1):
        self.pcs = self.loadPrices(d0,d1)
        pm = {}
        pm['zero'] = 0
        pm['hour'] = 60
        pm['hour8'] = pm['hour']*8
        pm['day'] = pm['hour']*24
        pm['day3'] = pm['day']*3
        pm['day5'] = pm['day']*5
        pm['week'] = pm['day']*7
        pm['week2'] = pm['week']*2
        pm['week3'] = pm['week']*3
        pm['full'] = 'full'
        self.pm = pm

    def get(self,ini,s):
        return self.pcs[self.pm[ini]:self.pm[ini]+self.pm[s]]

    def gets(self,ini,s):
        if s=='full':
            return self.pcs[ ini: ]
        return self.pcs[ ini : ini+s ]

    

    # load prices from database from date d0
    # to d1, dates are given in secons from epoch
    def loadPrices(self,d0,d1):
        db = pymysql.connect('localhost','root','root','pricer')
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

# pcs: prices to simulate in the form coinB/coinA
# cna: coinA
# aph: alpha for EMA
# tm: time in minutes to calculate Ratio
# ptg: percentage to buy or sel
def sim(pcs, cna, fee, aph, tm, ptg):
    ema, dev = EMA(aph), Ratio([pcs[0]] * tm, ptg)
    ocna, cnb, fees = cna, 0, 0
    for p in pcs:
        d = dev.next( ema.next(p) )
        if d==1 and cna>0 :
            fees += cna * fee
            cna -= cna * fee
            cnb += cna / p
            cna = 0
        elif d==-1 and cnb>0 :
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

# Simulates and prints prices every time a
# buy or sell is made
# at the end prices are plotted
def simg(pcs, cna, fee, aph, tm, ptg):
    print('\nSIMULATING:')
    ema, dev, ems = EMA(aph), Ratio([pcs[0]] * tm, ptg), []
    ocna, cnb, sells, buys, fees = cna, 0, 0, 0, 0

    t0 = time.time()

    for i in range(len(pcs)):
        p = pcs[i]
        e = ema.next(p)
        ems.append(e)
        d = dev.next(e)
        if d==1 and cna>0 :
            fees += cna * fee
            cna -= cna * fee
            cnb += cna / p
            cna = 0
            buys += 1
            print('Buy:',i,p)
        elif d==-1 and cnb>0 :
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
        print('Sell:',i,p)
    gain = (cna - ocna) / ocna

    print('time: ',round(time.time()-t0,3),'\n')

    print('\n')
    print('alpha:',aph,'tm:',tm,'ptg:',ptg)
    print('Original coins A:',ocna)
    print('Final coins A: ',round(cna,2))
    print('Difference:',round(cna-ocna,2))
    print('Percentage gain:',round(gain*100,2),'%')
    print('Buys and sells:',buys)
    print('Fees percentage:',round(fees/cna*100,2),'%')

    plt.plot(pcs)
    plt.plot(ems)
    plt.show()

def getevm():
    #random.seed(time.time())

    mtt = []
    difs =  [ (i+1)/10000 for i in range(10)]
    difs = difs + [-v for v in difs]
    mtt.append(difs)

    idifs = [ (i+1)*10 for i in range(10)] 
    idifs = idifs + [-v for v in idifs]
    mtt.append(idifs)

    difs =  [ (i+1)/1000 for i in range(10)]
    difs = difs + [-v for v in difs] 
    mtt.append(difs)

    d0, d1 = 1517103819, 1519516817
    pm = Priceman(d0,d1)
    pcs = pm.gets(pm.pm['week2'] , pm.pm['day']*4)
    pcf = [pcs, 100, 0.001]


    # limits
    lms = []
    lms.append((0.008, 0.015))  # alpha for EMA smoothing
    #lms.append((20,30))     # minutes
    lms.append((700, 1000))     # minutes
    lms.append((0.03, 0.10))   # percentage

    # rounding values
    rds = [5,5,5]

    evm = {}
    evm['mtt'] = mtt  # mutation table
    evm['pcf'] = pcf  # prices, coins, fees
    evm['lms'] = lms  # limits
    evm['rds'] = rds  #rounding values
    evm['frd'] = 8  # rounding for fitness

    return evm


def loadevm(f):

    mtt = []
    mtt.append( map(float,f.readline().split()) )
    mtt.append( map(int,f.readline().split()) )
    mtt.append( map(float,f.readline().split()) )

    pcf = [ [] ] + map(float,f.readline().split())

    lms = []
    lms.append( map(float,f.readline().split()) )
    lms.append( map(int,f.readline().split()) )
    lms.append( map(float,f.readline().split()) )

    rds = map(int,f.readline().split())

    frd = int(f.readline())

    evm = {}
    evm['mtt'] = mtt
    evm['pcf'] = pcf
    evm['lms'] = lms
    evm['rds'] = rds
    evm['frd'] = frd

    return evm


def dumpevm():
    f = open('../rsc/evmdump.txt','w')

    # mutations, mtt
    difs =  [ (i+1)/10000 for i in range(10)]
    difs = difs + [-v for v in difs]
    print(*difs,file=f)

    idifs = [ (i+1)*10 for i in range(10)] 
    idifs = idifs + [-v for v in idifs]
    print(*idifs,file=f)

    difs =  [ (i+1)/1000 for i in range(10)]
    difs = difs + [-v for v in difs]
    print(*difs,file=f)

    # coins and fee, pcf
    print(100,0.001,file=f)

    # limits, lms
    print(0.008,0.015,file=f)
    print(700,1000,file=f)
    print(0.3,0.1,file=f)

    # rounding values for genes, rds
    print(5,5,5,file=f) 

    # rounding for fitness, frd
    print(8,file=f)

    f.close()


# Generates a new random gen
def born(evm):
    gen = []
    lms = evm['lms']
    gen.append( random.uniform(lms[0][0],lms[0][1]) )
    gen.append( random.randrange(lms[1][0],lms[1][1]) )
    gen.append( random.uniform(lms[2][0],lms[2][1]) )
    rds = evm['rds']
    for i in range(len(rds)):
        gen[i] = round(gen[i],rds[i])
    gen = tuple(gen)
    gn = fitness(gen,evm)
    return (-gn,tuple(gen))

# Given a gen, calculates the percentage gain
# during a buy an sell simulation
def fitness(gen,evm):
    pms = evm['pcf'] + list(gen)
    return round( sim(*pms), evm['frd'] )

def evalgens(spc,ngens,evm):
    gn,gen = -spc[0], spc[1]
    nspcs = []
    for ngen in ngens:
        ngn = fitness(ngen,evm)
        if ngn>gn:
            nspcs.append((-ngn,ngen))
    return nspcs

def evalworker(adr):
    ss = socket.socket()
    ss.bind(adr)
    ss.listen(1)
    while True:
        soc,cli = ss.accept()
        evm = play.recv(soc)
        while True:
            pack = play.recv(soc)
            if pack=='end':
                break
            spc,ngens = pack
            nscps = evalgens(spc,ngens,evm)
            play.send(soc,nscps)

def getadjs(spc, vis, evm):
    adjs = []
    for i in range(len(spc[1])):
        tbl = evm['mtt'][i]
        for val in tbl:
            nspc = None
            gen = spc[1]
            ngen = list(gen)
            ngen[i] = round(ngen[i]+val,evm['rds'][i])
            ngen = tuple(ngen)
            lms = evm['lms']
            if ngen[i]>=lms[i][0] and ngen[i]<=lms[i][1] and ngen not in vis:
                adjs.append(ngen)
    return adjs

def sendslice(spc,slc,soc,q):
    pack = (spc,slc)
    play.send(soc,pack)
    nspcs = play.recv(soc)
    q.put(nspcs)

# psm: perfect specimens
# rps number of  repetitions of the while
# st for the priority queue
# vis is a set of gens
def perfect(spc, adrs, evm):
    print('perfecting')
    # Creating sockets for workers
    socs = []
    for adr in adrs:
        soc = socket.socket()
        soc.connect(adr)
        socs.append(soc)
    # Sending environment to workers
    for soc in socs:
        play.send(soc,evm)
    # Defining objects for the dfs
    st, psm, vis, rps = [], {}, set(), 10
    hp.heappush(st, spc)
    vis.add(spc[1])
    while len(st)>0 and len(psm)<3 and rps>0:
        # Getting adjacent elements
        spc = hp.heappop(st)
        adjs = getadjs(spc,vis,evm)
        # Dividing adjacent specimens into slices
        sn = len(socs)
        slcs = [ [] for i in range(sn) ]
        for i in range(len(adjs)):
            slcs[i%sn].append(adjs[i])
        ths,q = [],queue.Queue()
        # Sending slices to workers and waiting them to finish
        for i in range(sn):
            ths.append( play.mkthread(sendslice, (spc,slcs[i],socs[i],q)) )
        for th in ths:
            th.join()
        # Gathering the result from the workers
        nspcs = []
        while q.qsize()>0:
            nspcs.extend(q.get())
        # Analizing the results
        for nspc in nspcs:
            hp.heappush(st,nspc)
            vis.add(nspc[1])
        if len(nspcs)==0:
            if -spc[0]>0:
                psm[ spc[0] ] = spc[1]
        rps -= 1
    for soc in socs:
        play.send(soc,'end')
    return psm

# pps : population
def populate(evm,adrs):
    print('populating...')
    pps = {}
    for i in range(6):
        spc = born(evm)
        psm = perfect(spc,adrs,evm)
        pps.update(psm)
    return pps

def train(conf):
    f = open(conf,'r')
    exchange, cur_pair = f.readline().split()
    rng, wdt, ofs = map(int,f.readline().split()) # total price range, width, offset
    ns = int(f.readline())
    adrs = []
    for i in range(ns):
        adr = f.readline().split()
        adr[1] = int(adr[1])
        adrs.append(adr)
    evm = loadevm(f)
    f.close()
    # load prices from db
    db = pymysql.connect('localhost','root','root','pricer')
    tpcs = lastnprices(rng,exchange,cur_pair)
    ini = 0
    while ini<len(tpcs):
        pcs = tpcs[ini:] if len(tpcs)-ini-wdt<wdt else tpcs[ini:ini+wdt]
        ini += ofs
        evm['pcf'][0] = pcs
        




def test5():
    evm = getevm()
    d0, d1 = 1517103819, 1519516817
    pm = Priceman(d0,d1)
    pcs = []
    pcf = [pcs, 100, 0.001]

    tpps = {}
    n = len(pm.pcs)
    ini = 0
    offs = 60*24
    while ini+offs<n:
        pcs = pm.gets(ini,offs)
        ini += offs
        pcf[0] = pcs
        evm['pcf'] = pcf
        pps = populate(evm)
        print(pps)
        tpps.update(pps)

    pcs = pm.gets( 0 , 'full' )
    pcf[0] = pcs
    for k,v in tpps.items():
        prm = pcf + list(v)
        print(k,v,sim(*prm))
        print()


    tpps = [ (k,v) for k,v in tpps.items() ]
    tpps = sorted(tpps)
    print('Perfects specimens from 4 days environments during 3 weeks')
    print(tpps)

    s = ''
    for spc in tpps:
        s += str(spc[0]) + ' ' + str(spc[1]) + '\n'

    fout = open('perfs.txt','w')
    fout.write(s)
    fout.close()

def test():
    d0, d1 = 1517103819, 1519516817
    pm = Priceman(d0,d1)
    #pcs = pm.gets(pm.pm['week2'] , pm.pm['day']*4 )
    pcs = pm.gets(pm.pm['zero'] , pm.pm['full'] )
    pcf = [pcs,100,0.001]
    gen = [0.00874, 867, 0.03295]
    prm = pcf + gen
    simg(*prm)


if __name__ == '__main__':

    dumpevm()
    exit(1)

    if sys.argv[1]=='0':
        test5()
    else:
        evalworker(('localhost',int(sys.argv[1])))

