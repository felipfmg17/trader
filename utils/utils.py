
import json


# def genBinanceReqs():
#     data = pricer.downloadResource('api.binance.com', '/api/v1/ticker/allBookTickers')
#     data = data.decode('utf-8')
#     jsonObj = json.loads(data)
#     pairs = []
#     for e in jsonObj:
#     	pairs.append(e['symbol'])
#     pairs = [ e for e in pairs if 'BTC'  in e ]
#     pp = []
#     for e in pairs:
#     	ind = e.find('BTC')
#     	fst = e[:ind]
#     	snd = e[ind:]
#     	s = fst+'_'+snd
#     	s = s.lower()
#     	pp.append(s)
#     print(pp)

#     ans = ''
#     for i in range( len(pairs) ):
#     	line = 'api.binance.com ' + '/api/v1/ticker/24hr?symbol='+pairs[i] +  ' binance ' +  pp[i] + ' 60' + '\n'
#     	ans = ans + line

#     print(ans)


def downloadResource(host,resource):
    data = None
    headers = {'User-Agent': 'Mozilla/5.0'}
    conn = http.client.HTTPSConnection(host)
    conn.request('GET',resource,'',headers)
    response = conn.getresponse()
    data = response.read()
    return data

def genBinancePairsBD():
	data = downloadResource('api.binance.com', '/api/v1/ticker/allBookTickers')
	data = data.decode('utf-8')
	jsonObj = json.loads(data)
	pairs = []
	for e in jsonObj:
		pairs.append(e['symbol'])
	pairs = [ e for e in pairs if 'BTC'  in e ]
	pp = []
	for e in pairs:
		if e == 'BTCUSDT':
			continue
		ind = e.find('BTC')
		fst = e[:ind]
		snd = e[ind:]
		s = fst+'_'+snd
		s = s.lower()
		s = '(\"' + s + '\")'
		pp.append(s)


	sql = 'insert into currency_pair(name) values\n'

	for i in range(len(pp)):
		sql = sql + pp[i] + ','
		if i%7==6:
			sql += '\n'

	print(sql)
		


genBinancePairsBD()