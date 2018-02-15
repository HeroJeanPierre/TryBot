# For Binance Web Sockets: 	https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
# For Binance REST API:		https://github.com/binance-exchange/binance-official-api-docs

from binance.client import Client
import requests
import csv
import pprint
pp = pprint.PrettyPrinter()

# pp.pprint(test.json())


def getAsk(pair):
	all_orders = requests.get('https://api.binance.com/{}'.format('/api/v3/ticker/bookTicker'))
	for i in all_orders.json():
		symbol = i['symbol']
		if pair == symbol:
			return i['askPrice']
		# if pair == i['symbol']
			# return i['askPrice']
			




print(getAsk('BNBBTC'))
