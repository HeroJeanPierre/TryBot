# For Binance Web Sockets: 	https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
# For Binance REST API:		https://github.com/binance-exchange/binance-official-api-docs
import time
import requests
import pprint
import pickle
import numpy as np
pp = pprint.PrettyPrinter()

# Get all the currency pairs and there prices on Binance
pairs = requests.get('https://api.binance.com/{}'.format('/api/v3/ticker/price'))

# Make json interactable
pairs = pairs.json()
BTC_Pairs = []
ETH_Pairs = []
BNB_Pairs = []
USDT_Pairs = []


# Create List of pairs for above lists ^
def createCurrencyPairs():
	for pair in pairs:
		curr_pair = pair['symbol']

		if 'BTC' == curr_pair[-3:]:
			BTC_Pairs.append(curr_pair)
		elif 'ETH' == curr_pair[-3:]:
			ETH_Pairs.append(curr_pair)
		elif 'BNB' == curr_pair[-3:]:
			BNB_Pairs.append(curr_pair)
		elif 'USDT' == curr_pair[-4:]:
			USDT_Pairs.append(curr_pair)

	# print('{} BTC pairs...\n{}\n\n{} ETH pairs...\n{}\n\n{} BNB pairs...\n{}\n\n{} USDT pairs...\n{}\n\n'.format(len(BTC_Pairs), BTC_Pairs, len(ETH_Pairs), ETH_Pairs, len(BNB_Pairs), BNB_Pairs, len(USDT_Pairs), USDT_Pairs))

# These are always going to best the first trades made.
# BTC -> ETH
# BTC -> BNB
# BTC -> USDT

# All potential arbitrage triplets will go here
ETH_Opps = []
BNB_Opps = []
USDT_Opps = []

def createCurrencyOppps():
	# Traverse all BTC Pairs
	for btc1 in BTC_Pairs:
		# Traverse all ETH Pairs
		for eth2 in ETH_Pairs:
			# If there exists a ETH pair with mutual BTC currency, move on
			if btc1[:-3] == eth2[:-3]:
				# FOUND!
				ETH_Opps.append('BTC_ETH_' + eth2[:-3])

	for btc1 in BTC_Pairs:
		for bnb2 in BNB_Pairs:
			if btc1[:-3] == bnb2[:-3]:
				# FOUND!
				BNB_Opps.append('BTC_BNB_' + bnb2[:-3])

	for btc1 in BTC_Pairs:
		for usdt2 in USDT_Pairs:
			if btc1[:-3] == usdt2[:-4]:
				# FOUND!
				USDT_Opps.append('BTC_USDT_' + usdt2[:-4])

	# print('{} Total Opps Found!\n\n{} ETH opportunities...\n{}\n\n{} BNB opportunities...\n{}\n\n{} USDT opportunities...\n{}\n\n'.format((len(ETH_Opps) + len(BNB_Opps) + len(USDT_Opps)),len(ETH_Opps), ETH_Opps, len(BNB_Opps), BNB_Opps, len(USDT_Opps), USDT_Opps))

# def getPrice(symbol):
# 	for curr_pair in pairs:
# 		if symbol == curr_pair['symbol']:
# 					return curr_pair['price']


all_orders = requests.get('https://api.binance.com/{}'.format('/api/v3/ticker/bookTicker'))
all_orders = all_orders.json()
def getPrice(pair):
	for i in all_orders:
		symbol = i['symbol']
		if pair == symbol:
			return i['askPrice']


all_percentages = []
transaction_fee = .001
def createTripletData():
	for ETH_Path in ETH_Opps:
		curr_split = ETH_Path.split('_')
		principle = 1.0
		
		step1 = (principle / float(getPrice(curr_split[1] + curr_split[0]))) * (1.0 - transaction_fee)
		step2 = step1/float(getPrice(curr_split[2] + curr_split[1])) * (1.0 - transaction_fee)
		newPrice = step2 * float(getPrice(curr_split[2] + curr_split[0])) * (1.0 - transaction_fee)

		all_percentages.append([ETH_Path, (100*((newPrice/1.0) - 1))])
		# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))

	for BNB_Path in BNB_Opps:
		curr_split = BNB_Path.split('_')
		principle = 1.0
		
		step1 = principle / float(getPrice(curr_split[1] + curr_split[0])) * (1.0 - transaction_fee)
		step2 = step1/float(getPrice(curr_split[2] + curr_split[1])) * (1.0 - transaction_fee)
		newPrice = step2 * float(getPrice(curr_split[2] + curr_split[0])) * (1.0 - transaction_fee)

		all_percentages.append([BNB_Path, (100*((newPrice/1.0) - 1))])
		# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))

	for USDT_Path in USDT_Opps:
		curr_split = USDT_Path.split('_')
		principle = 1.0
		

		step1 = principle * float(getPrice(curr_split[0] + curr_split[1])) * (1.0 - transaction_fee)
		# print('1 {} buys {} {}'.format(curr_split[0], step1, curr_split[1]))

		step2 = step1/float(getPrice(curr_split[2] + curr_split[1])) * (1.0 - transaction_fee)
		# print('{} {} buys {} {}'.format(step1,curr_split[1], step2, curr_split[2]))

		newPrice = step2 * float(getPrice(curr_split[2] + curr_split[0])) * (1.0 - transaction_fee)
		# print('{} {} buys {} {}'.format(step2, curr_split[2], newPrice, curr_split[0]))


		all_percentages.append([USDT_Path, (100*((newPrice/1.0) - 1))])
		# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))
		# print(getPrice(all_opps[-1][0].split('_')[2] + all_opps[-1][0].split('_')[1]))

def main():
	t0 = time.time()
	createCurrencyPairs()
	createCurrencyOppps()
	createTripletData()

	all_opps = np.array(all_percentages)
	all_opps=all_opps[np.argsort(all_opps[:,1])]
	print(all_opps)
	t1 = time.time()
	print('Runtime {} seconds'.format(t1-t0))

if __name__ == '__main__':
	main()