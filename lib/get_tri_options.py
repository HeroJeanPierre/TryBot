# For Binance Web Sockets: 	https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
# For Binance REST API:		https://github.com/binance-exchange/binance-official-api-docs
# Download time ~ 1.5s
# Runtime ~ .005seconds

import time
import requests
import pprint
pp = pprint.PrettyPrinter()
import pickle
import numpy as np
import sys
import csv


class TryBotDataScraper:

	# Set intitial variables for data
	def __init__(self):
		# These are all the pairs for primary currencies
		# Ex. XRPBTC, STRATETH, ETHUSDT
		self.BTC_Pairs = []
		self.ETH_Pairs = []
		self.BNB_Pairs = []
		self.USDT_Pairs = []

		# These will hold the possible triplets that could be
		# traded
		self.ETH_Opps = []
		self.BNB_Opps = []
		self.USDT_Opps = []

		# Will hold, paths, percentage data, and potentially volume
		self.all_percentages = []

		# Transaction fees are 0.015% with BNB fees turned on, so this is optimal. Just have like $10 in BNB account
		self.transaction_fee = .00015 # With BNB Fees
	
		# Download pairs and prices, this will just be used for the pairs though
		self.pairs = (requests.get('https://api.binance.com/api/v3/ticker/price')).json()

		# This calls the order book for every currency, necissary in order to get the bid and ask
		self.all_orders = (requests.get('https://api.binance.com/api/v3/ticker/bookTicker')).json()


	# This just resets the values so the loop can re-evaluate for another time period
	def resetVals(self):
		self.BTC_Pairs = []
		self.ETH_Pairs = []
		self.BNB_Pairs = []
		self.USDT_Pairs = []
		self.ETH_Opps = []
		self.BNB_Opps = []
		self.USDT_Opps = []
		self.all_percentages = []


	# Update the order sheets for currency pairs 
	def updateOrders(self):
		self.all_orders = (requests.get('https://api.binance.com/api/v3/ticker/bookTicker')).json()


	# Create list of all currency pairs
	def createCurrencyPairs(self):
		for pair in self.pairs:
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

	
	# Find all currnency triplets w/ BTC as base
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

	
	# get the current ask price for given currency pair
	def getAsk(self, pair):
		for i in self.all_orders:
			symbol = i['symbol']
			if pair == symbol:
				return i['askPrice']


	# get the current ask price for given currency pair
	def getBid(self, pair):
		for i in self.all_orders:
			symbol = i['symbol']
			if pair == symbol:
				return i['bidPrice']


	# create data for possible percentage gains
	def createTripletData(self):
		for self.ETH_Path in self.ETH_Opps:
			curr_split = self.ETH_Path.split('_')
			principle = 1.0
			
			step1 = principle / float(self.getAsk(curr_split[1] + curr_split[0])) * (1.0 - self.transaction_fee)
			step2 = step1/float(self.getAsk(curr_split[2] + curr_split[1])) * (1.0 - self.transaction_fee)
			newPrice = step2 * float(self.getBid(curr_split[2] + curr_split[0])) * (1.0 - self.transaction_fee)
			if newPrice > 1.0:
				self.all_percentages.append([self.ETH_Path, (100*((newPrice/1.0) - 1)),self.getAsk(curr_split[1] + curr_split[0]) ,self.getAsk(curr_split[2] + curr_split[1]), self.getBid(curr_split[2] + curr_split[0])])
			# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))

		for BNB_Path in self.BNB_Opps:
			curr_split = BNB_Path.split('_')
			principle = 1.0
			
			step1 = principle / float(self.getAsk(curr_split[1] + curr_split[0])) * (1.0 - self.transaction_fee)
			step2 = step1/float(self.getAsk(curr_split[2] + curr_split[1])) * (1.0 - self.transaction_fee)
			newPrice = step2 * float(self.getBid(curr_split[2] + curr_split[0])) * (1.0 - self.transaction_fee)
			if newPrice > 1.0:
				self.all_percentages.append([BNB_Path, (100*((newPrice/1.0) - 1)),self.getAsk(curr_split[1] + curr_split[0]) ,self.getAsk(curr_split[2] + curr_split[1]), self.getBid(curr_split[2] + curr_split[0])])
			# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))

		for USDT_Path in self.USDT_Opps:
			curr_split = USDT_Path.split('_')
			principle = 1.0
			

			step1 = principle * float(self.getAsk(curr_split[0] + curr_split[1])) * (1.0 - self.transaction_fee)
			# print('1 {} buys {} {}'.format(curr_split[0], step1, curr_split[1]))

			step2 = step1/float(self.getAsk(curr_split[2] + curr_split[1])) * (1.0 - self.transaction_fee)
			# print('{} {} buys {} {}'.format(step1,curr_split[1], step2, curr_split[2]))

			newPrice = step2 * float(self.getBid(curr_split[2] + curr_split[0])) * (1.0 - self.transaction_fee)
			# print('{} {} buys {} {}'.format(step2, curr_split[2], newPrice, curr_split[0]))

			if newPrice > 1.0:
				self.all_percentages.append([USDT_Path, (100*((newPrice/1.0) - 1)), self.getAsk(curr_split[0] + curr_split[1]) ,self.getAsk(curr_split[2] + curr_split[1]), self.getBid(curr_split[2] + curr_split[0])])
			# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1)))))
			# print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))
			# print(getPrice(all_opps[-1][0].split('_')[2] + all_opps[-1][0].split('_')[1]))


def main():

	# Open csv file
	csv_tag = time.strftime('%b_%d_%H_%M_%S')
	csv_file = open('found_data_{}.csv'.format(csv_tag) , 'w')	
	csv_writer = csv.writer(csv_file)
	csv_writer.writerow(['path', 'percentage', 'time'])

	timeTotal = time.time()

	# Run this continoously
	x = float(input("Minutes would you like to test for: "))
	print("Testing for for {} seconds | {} hours | {} days".format(x*60, x/60, (x/(60*24))))

	# Will contain found pairs
	allGathered = []

	# 
	bot = TryBotDataScraper()


	totalSecond = x*60
	while (time.time() - timeTotal) < totalSecond:
		bot.resetVals()
		t0 = time.time()
		bot.createCurrencyPairs()
		bot.createCurrencyOpps()
		bot.createTripletData()

		if len(bot.all_percentages) > 0:
			all_opps = np.array(bot.all_percentages)
			all_opps=all_opps[np.argsort(all_opps[:,1])]
			print(all_opps[:,:2])
			time_date = time.strftime('%b %d %H:%M:%S')

			for i in all_opps:
				csv_writer.writerow([i[0], i[1], time_date])
		else:
			print('No Triplets Found.')
		bot.updateOrders()

		print('Runtime {} seconds'.format(time.time()-t0))
	csv_file.close()
	print("Total time took {} seconds".format(time.time() - timeTotal))

	with open("../data/test_data/found_data.pickle", 'wb') as f:
		pickle.dump(allGathered, f)

if __name__ == '__main__':
	main()