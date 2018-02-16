# For Binance Web Sockets: 	https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
# For Binance REST API:		https://github.com/binance-exchange/binance-official-api-docs
# Download time ~ 1.5s
# Runtime ~ .005seconds

import time
import requests
import pprint
import pickle
import numpy as np
import sys
pp = pprint.PrettyPrinter()

class TryBot:
	def __init__(self):
		self.BTC_Pairs = []
		self.ETH_Pairs = []
		self.BNB_Pairs = []
		self.USDT_Pairs = []
		self.ETH_Opps = []
		self.BNB_Opps = []
		self.USDT_Opps = []
		self.self.all_percentages = []
		self.pairs = {}
		self.all_orders = {}

	# Get all the currency pairs and there prices on Binance
	def updatePairs(self):
		target = '/api/v3/ticker/price'
		self.pairs = (requests.get('https://api.binance.com/' + target)).json()
		

	# Make json interactable
	# self.BTC_Pairs = []
	# self.ETH_Pairs = []
	# self.BNB_Pairs = []
	# self.USDT_Pairs = []


	# Create List of pairs for above lists ^
	def createCurrencyPairs(self):
		for pair in pairs:
			curr_pair = pair['symbol']

			if 'BTC' == curr_pair[-3:]:
				self.BTC_Pairs.append(curr_pair)
			elif 'ETH' == curr_pair[-3:]:
				self.ETH_Pairs.append(curr_pair)
			elif 'BNB' == curr_pair[-3:]:
				self.BNB_Pairs.append(curr_pair)
			elif 'USDT' == curr_pair[-4:]:
				self.USDT_Pairs.append(curr_pair)

		# print('{} BTC pairs...\n{}\n\n{} ETH pairs...\n{}\n\n{} BNB pairs...\n{}\n\n{} USDT pairs...\n{}\n\n'.format(len(self.BTC_Pairs), self.BTC_Pairs, len(self.ETH_Pairs), self.ETH_Pairs, len(self.BNB_Pairs), self.BNB_Pairs, len(self.USDT_Pairs), self.USDT_Pairs))

	
	def createCurrencyOpps(self):
		# Traverse all BTC Pairs
		for btc1 in self.BTC_Pairs:
			# Traverse all ETH Pairs
			for eth2 in self.ETH_Pairs:
				# If there exists a ETH pair with mutual BTC currency, move on
				if btc1[:-3] == eth2[:-3]:
					# FOUND!
					self.ETH_Opps.append('BTC_ETH_' + eth2[:-3])

		for btc1 in self.BTC_Pairs:
			for bnb2 in self.BNB_Pairs:
				if btc1[:-3] == bnb2[:-3]:
					# FOUND!
					self.BNB_Opps.append('BTC_BNB_' + bnb2[:-3])

		for btc1 in self.BTC_Pairs:
			for usdt2 in self.USDT_Pairs:
				if btc1[:-3] == usdt2[:-4]:
					# FOUND!
					self.USDT_Opps.append('BTC_USDT_' + usdt2[:-4])

		# print('{} Total Opps Found!\n\n{} ETH opportunities...\n{}\n\n{} BNB opportunities...\n{}\n\n{} USDT opportunities...\n{}\n\n'.format((len(self.ETH_Opps) + len(self.BNB_Opps) + len(self.USDT_Opps)),len(self.ETH_Opps), self.ETH_Opps, len(self.BNB_Opps), self.BNB_Opps, len(self.USDT_Opps), self.USDT_Opps))

	# def getPrice(symbol):
	# 	for curr_pair in pairs:
	# 		if symbol == curr_pair['symbol']:
	# 					return curr_pair['price']


	def getAllOrders(self):
		target = '/api/v3/ticker/bookTicker'
		return (requests.get('https://api.binance.com/' + target)).json()
		
		
	def getAsk(self, pair):
		for i in self.all_orders:
			symbol = i['symbol']
			if pair == symbol:
				return i['askPrice']

	def getBid(self, pair):
		for i in self.all_orders:
			symbol = i['symbol']
			if pair == symbol:
				return i['bidPrice']

	# self.all_percentages = []
	transaction_fee = .001
	def createTripletData(self):
		for self.ETH_Path in self.ETH_Opps:
			curr_split = self.ETH_Path.split('_')
			principle = 1.0
			
			step1 = principle / float(getAsk(curr_split[1] + curr_split[0])) * (1.0 - transaction_fee)
			step2 = step1/float(getAsk(curr_split[2] + curr_split[1])) * (1.0 - transaction_fee)
			newPrice = step2 * float(getBid(curr_split[2] + curr_split[0])) * (1.0 - transaction_fee)
			if newPrice > 1.0:
				self.all_percentages.append([self.ETH_Path, (100*((newPrice/1.0) - 1)),getAsk(curr_split[1] + curr_split[0]) ,getAsk(curr_split[2] + curr_split[1]), getBid(curr_split[2] + curr_split[0])])
			# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))

		for BNB_Path in self.BNB_Opps:
			curr_split = BNB_Path.split('_')
			principle = 1.0
			
			step1 = principle / float(getAsk(curr_split[1] + curr_split[0])) * (1.0 - transaction_fee)
			step2 = step1/float(getAsk(curr_split[2] + curr_split[1])) * (1.0 - transaction_fee)
			newPrice = step2 * float(getBid(curr_split[2] + curr_split[0])) * (1.0 - transaction_fee)
			if newPrice > 1.0:
				self.all_percentages.append([BNB_Path, (100*((newPrice/1.0) - 1)),getAsk(curr_split[1] + curr_split[0]) ,getAsk(curr_split[2] + curr_split[1]), getBid(curr_split[2] + curr_split[0])])
			# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))

		for USDT_Path in self.USDT_Opps:
			curr_split = USDT_Path.split('_')
			principle = 1.0
			

			step1 = principle * float(getAsk(curr_split[0] + curr_split[1])) * (1.0 - transaction_fee)
			# print('1 {} buys {} {}'.format(curr_split[0], step1, curr_split[1]))

			step2 = step1/float(getAsk(curr_split[2] + curr_split[1])) * (1.0 - transaction_fee)
			# print('{} {} buys {} {}'.format(step1,curr_split[1], step2, curr_split[2]))

			newPrice = step2 * float(getBid(curr_split[2] + curr_split[0])) * (1.0 - transaction_fee)
			# print('{} {} buys {} {}'.format(step2, curr_split[2], newPrice, curr_split[0]))

			if newPrice > 1.0:
				self.all_percentages.append([USDT_Path, (100*((newPrice/1.0) - 1)), getAsk(curr_split[0] + curr_split[1]) ,getAsk(curr_split[2] + curr_split[1]), getBid(curr_split[2] + curr_split[0])])
			# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1)))))
			# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))
			# print(getPrice(all_opps[-1][0].split('_')[2] + all_opps[-1][0].split('_')[1]))


def main():

	# Run this continoously
	while True:

		t0 = time.time()
		self.all_orders = getAllOrders()

		createCurrencyPairs()
		createCurrencyOpps()
		createTripletData()

		# print(self.all_percentages)
		if len(self.all_percentages) > 0:
			all_opps = np.array(self.all_percentages)
			all_opps=all_opps[np.argsort(all_opps[:,1])]
			print(all_opps)
		else:
			print('No Triplets Found.')
		t1 = time.time()
		print('Runtime {} seconds'.format(t1-t0))

if __name__ == '__main__':
	main()