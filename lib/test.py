# For Binance Web Sockets: 	https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
# For Binance REST API:		https://github.com/binance-exchange/binance-official-api-docs

from binance.client import Client
import requests
import csv
import pprint
pp = pprint.PrettyPrinter()

with open('../cred/api_secret_binance', 'r') as f:
	secret = f.read()
with open('../cred/api_key_binance', 'r') as f:
	key = f.read()

info = requests.get('https://api.binance.com/{}'.format('/api/v3/ticker/price'))



# # pp.pprint(test.json())
# order = requests.get( params={'signature'})
# all_orders = all_orders.json()
