# For Binance Web Sockets: 	https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
# For Binance REST API:		https://github.com/binance-exchange/binance-official-api-docs

from binance.client import Client
import requests
import csv
import pprint
pp = pprint.PrettyPrinter()

test = requests.get('https://api.binance.com/{}'.format('/api/v1/depth'), params = {'symbol' : 'LTCBTC'})
pp.pprint(test.json())

