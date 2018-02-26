import http.client
import json
import time
import pymysql
import logging
import threading
import smtplib

# example host=api.binance.com
# resource = /api/v1/ticker/24hr?symbol=ETHBTC
# Downloads the desired resource from the host
# returns a string
def downloadResource(host,resource):
    data = None
    headers = {'User-Agent': 'Mozilla/5.0'}
    conn = http.client.HTTPSConnection(host)
    conn.request('GET',resource,'',headers)
    response = conn.getresponse()
    data = response.read()
    return data

# Receives a file with a ticker containing
# the price of a coin
# returns the price as a decimal number
def extractPrice(data, exchange):
    if exchange=='bitso':
        price = None
        data = data.decode('utf-8')
        jsonObj = json.loads(data)
        price = jsonObj['payload']['last']
        return price
    elif exchange=='bitfinex':
        price = None
        data = data.decode('utf-8')
        jsonString = json.loads(data)
        price = jsonString['last_price']
        return price
    elif exchange=='binance':
        price = None
        data = data.decode('utf-8')
        jsonObj = json.loads(data)
        price = jsonObj['lastPrice']
        return price
    elif exchange=='poloniex':
        price = None
        data = data.decode('utf-8')
        jsonObj = json.loads(data)
        price = jsonObj['USDT_XRP']['last']
        return price
    elif exchange=='hitbtc':
        price = None
        data = data.decode('utf-8')
        jsonObj = json.loads(data)
        price = jsonObj['last']
        return price
    elif exchange=='bitstamp':
        price = None
        data = data.decode('utf-8')
        jsonObj = json.loads(data)
        price = jsonObj['last']
        return price
    elif exchange=='bittrex':
        price = None
        data = data.decode('utf-8')
        jsonObj = json.loads(data)
        price = jsonObj['result']['Last']
        return price
    elif exchange=='cex.io':
        price = None
        data = data.decode('utf-8')
        jsonObj = json.loads(data)
        price = jsonObj['last']
        return price

# Stores a prices with the exchange and currency pair information
# exchange  and cur_pair must be a valid string from the database
def savePriceBD(exchange, cur_pair, price, db):
    cursor = db.cursor()
    sql = 'select id from currency_pair where name = \"' + cur_pair + '\"'
    cursor.execute(sql)
    data = cursor.fetchone()[0]
    cursor.close()
    cur_pair_id = data
    cursor = db.cursor()
    sql = 'select id from exchange where name = \"' + exchange + '\"'
    cursor.execute(sql)
    data = cursor.fetchone()[0]
    exchange_id = data
    cursor.close()
    cursor = db.cursor()
    sql = 'select id from price_type where name = \"last\"'
    cursor.execute(sql)
    data = cursor.fetchone()[0]
    price_type = data
    cursor.close()

    sql = 'insert into coin_price(date_time_sec, exchange_id, currency_pair_id, price, date_time, price_type_id) '
    sql = sql + 'values('
    sql = sql + str( time.time() )+ ', '
    sql = sql + str( exchange_id ) + ', '
    sql = sql + str( cur_pair_id ) + ', '
    sql = sql + str( price ) + ', '
    sql = sql + 'NOW(), '
    sql = sql + str( price_type) + ')'

    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()

def sendEmail(msg):
    try:
        user = 'felipedevcrypto@gmail.com'
        password = 'felipedevcrypto'
        to = ['felipfmg17@gmail.com']
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(user, password)
        server.sendmail(user, to, msg)
        server.close()
        print('Email sent!')
    except Exception as err:
        print('Email could not be sent')
        logging.exception(err)

class ErrorState:
    def __init__(self):
        self.lk = threading.Lock()
        self.bkt = {}

    def setmsg(self,msg):
        if self.lk.acquire():
            if msg not in self.bkt:
                self.bkt[msg] = 0
            self.bkt[msg] += 1
            self.lk.release()

    def getmsg(self):
        msg = ''
        if self.lk.acquire():
            for u,v in self.bkt.items():
                msg += u + ' ' + str(v) +'\n'
            self.lk.release()
        return msg

    def reset(self):
        if self.lk.acquire():
            self.bkt = {}
            self.lk.release()

def measureerrs(ers):
    while True:
        time.sleep(60*60*6)
        msg = ers.getmsg()
        ers.reset()
        sendEmail(msg)

# Start an infinite loop which downloads a resources, extracts the price
# and stores it in a database
# The price is extracted from the json file using 'extractor' function
# The loop wait for some seconds specified in 'pause'
# exchange and cur_pair must be exact values from the database
def startDownload(host,resource,exchange,cur_pair,pause,db,ers):
    while True:
        try:
            data = downloadResource(host, resource)
            price = extractPrice(data, exchange)
            savePriceBD(exchange, cur_pair, price, db);
            print('Download successful:',host+resource)
        except Exception as err:
            ers.setmsg(host+resource)
            print(threading.current_thread().name, 'Error', host+resource )
            logging.exception(err)
        time.sleep(pause)

# runs  'startDownload()'  for multiple currency pairs
# it ask for the database connection and the number of resources you want to download
# then type the resources including host, currency pair , pause, host
def startMultiDownload():
    nums_requests = int(input())  # amount of resources
    ers = ErrorState()
    ths = []
    th = threading.Thread(target=measureerrs, args=[ers] )
    th.start()
    ths.append(th)
    time.sleep(1)
    for i in range(nums_requests):
        db = pymysql.connect('localhost','root','root','pricer')
        req = input().split() # host resource exchange currencypair pause
        req[4] = int(req[4])
        req = req + [db,ers]
        th = threading.Thread(target=startDownload, args=req )
        th.start()
        ths.append(th)
    for th in ths:
        th.join()

if __name__ == '__main__':
    startMultiDownload()



