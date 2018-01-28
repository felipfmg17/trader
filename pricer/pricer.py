import http.client,json,time,pymysql,logging,threading, smtplib

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

# Receives a Bitso Json file with a ticker containing
# the price of a coin
# returns the price as a decimal number
def bitsoPriceExtractor(data):
    price = None
    data = data.decode('utf-8')
    jsonObj = json.loads(data)
    price = jsonObj['payload']['last']
    return price

# Receives a Bitfinex Json file with a ticker containing
# the price of a coin
# returns the price as a decimal number
def bitfinexPriceExtractor(data):
    price = None
    data = data.decode('utf-8')
    jsonString = json.loads(data)
    price = jsonString['last_price']
    return price

# Receives a Bitfinex Json file with a ticker containing
# the price of a coin
# returns the price as a decimal number
def binancePriceExtractor(data):
    price = None
    data = data.decode('utf-8')
    jsonObj = json.loads(data)
    price = jsonObj['lastPrice']
    return price

def createDBConnection(host,user, password, db_name):
    db = pymysql.connect(host,user,password,db_name)
    return db

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


def sendErrorEmail(destemail,msg):
    try:
        gmail_user = 'felipedevcrypto@gmail.com'
        gmail_password = 'didu.2015'

        sent_from = gmail_user
        #to = ['felipfmg17@gmail.com']
        to = [destemail]
        subject = 'Pricer Error'
        body = msg

        email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, body)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        print('Email sent!')
    except:
        print('Email could not be sent')

# Start an infinite loop which downloads a resources, extracts the price
# and stores it in a database
# The price is extracted from the json file using 'extractor' function
# The loop wait for some seconds specified in 'pause'
# exchange and cur_pair must be exact values from the database
def startDownload(host,resource,exchange,cur_pair,pause,db,extractor,destemail):
    number = 1
    while True:
        try:
            data = downloadResource(host,resource)
            price = extractor(data)
            savePriceBD(exchange, cur_pair, price, db);
            print('Download successful ' + str(number) + ': ' ,host+resource)
            number += 1
        except Exception as err:
            print(threading.current_thread().name, 'Error', host+resource )
            logging.exception(err)
            sendErrorEmail(destemail,host+resource)
        time.sleep(pause)



# runs  'startDownload()'  for multiple currency pairs
# it ask for the database connection and the number of resources you want to download
# then type the resources including host, currency pair , pause, host
def startMultiDownload():
    print('Type next Mysql params -  host user password dbName: ')
    db_params = input().split()
    print('Type email for notifications: ')
    destemail = input()
    print('Type amount of resources: ')
    nums_requests = int(input())
    ths = []
    for i in range(nums_requests):
        db = createDBConnection(*db_params)
        print('Type params for resource number ' + str(i+1) + ' : host resource exchange currencyPair pause: ')
        req = input().split()
        req[4] = int(req[4])
        req = req + [db, exts[req[2]],destemail]
        th = threading.Thread(target=startDownload, args=req )
        th.start()
        ths.append(th)
    for th in ths:
        th.join()


exts = {}
exts['bitso'] = bitsoPriceExtractor
exts['bitfinex'] = bitfinexPriceExtractor
exts['binance'] = binancePriceExtractor

startMultiDownload()


