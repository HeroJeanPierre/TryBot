# The purpose of this file is to retrieve data
# for triplet pairs

# For Binance Web Sockets:  https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
# For Binance REST API:     https://github.com/binance-exchange/binance-official-api-docs
# Download time ~ 1.5s
# Runtime ~ .005seconds

import time
import requests
import pprint
import pickle
import numpy as np
import csv
pp = pprint.PrettyPrinter()


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
        self.transactionFee = .00015  # With BNB Fees

        # Download pairs and prices, this will just be used for the pairs though
        self.pairs = (requests.get(
            'https://api.binance.com/api/v3/ticker/price')).json()

        # This calls the order book for every currency, necissary in order to get the bid and ask
        self.all_orders = (requests.get(
            'https://api.binance.com/api/v3/ticker/bookTicker')).json()

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
        self.all_orders = (requests.get(
            'https://api.binance.com/api/v3/ticker/bookTicker')).json()

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
    def getAskPrice(self, pair):
        for i in self.all_orders:
            symbol = i['symbol']
            if pair == symbol:
                return i['askPrice']

    # get the current ask price for given currency pair
    def getBidPrice(self, pair):
        for i in self.all_orders:
            symbol = i['symbol']
            if pair == symbol:
                return i['bidPrice']

    def getAskVolume(self, pair):
        for i in self.all_orders:
            symbol = i['symbol']
            if pair == symbol:
                return i['askQty']

    def getBidVolume(self, pair):
        for i in self.all_orders:
            symbol = i['symbol']
            if pair == symbol:
                return i['bidQty']

    def getAskPriceInUSDT(self, pair):
        if 'USDT' in pair:
            return float(self.getAskPrice(pair))
        else:
            return float(self.getAskPrice(pair)) * float(self.getAskPrice(pair[-3:] + 'USDT'))

    def getBidPriceInUSDT(self, pair):
            if 'USDT' in pair:
                return float(self.getBidPrice(pair))
            else:
                return float(self.getBidPrice(pair)) * float(self.getBidPrice(pair[-3:] + 'USDT'))

    def getAskValueInUSDT(self, pair):
        if 'USDT' in pair:
            return float(self.getAskVolume(pair)) * float(self.getAskPrice(pair))
        else:
            return float(self.getAskVolume(pair)) * self.getAskPriceInUSDT(pair)

    def getBidValueInUSDT(self, pair):
        if 'USDT' in pair:
            return float(self.getBidVolume(pair)) * float(self.getBidPrice(pair))
        else:
            return float(self.getBidVolume(pair)) * self.getBidPriceInUSDT(pair)

    # create data for possible percentage gains
    def createTripletData(self):
        for ETH_Path in self.ETH_Opps:
            currSplit = ETH_Path.split('_')
            principle = 1.0

            step1 = principle / float(self.getAskPrice(currSplit[1] + currSplit[0])) * (1.0 - self.transactionFee)
            step2 = step1 / float(self.getAskPrice(currSplit[2] + currSplit[1])) * (1.0 - self.transactionFee)
            newPrice = step2 * float(self.getBidPrice(currSplit[2] + currSplit[0])) * (1.0 - self.transactionFee)

            if newPrice > (1.0005):
                found_pair = ETH_Path
                percentage = (100 * ((newPrice / 1.0) - 1))
                pathValue1 = self.getAskValueInUSDT(currSplit[1] + currSplit[0])
                pathValue2 = self.getAskValueInUSDT(currSplit[2] + currSplit[1])
                pathValue3 = self.getBidValueInUSDT(currSplit[2] + currSplit[0])

                self.all_percentages.append([found_pair, percentage, pathValue1, pathValue2, pathValue3])

        for BNB_Path in self.BNB_Opps:
            currSplit = BNB_Path.split('_')
            principle = 1.0

            step1 = principle / float(self.getAskPrice(currSplit[1] + currSplit[0])) * (1.0 - self.transactionFee)
            step2 = step1 / float(self.getAskPrice(currSplit[2] + currSplit[1])) * (1.0 - self.transactionFee)
            newPrice = step2 * float(self.getBidPrice(currSplit[2] + currSplit[0])) * (1.0 - self.transactionFee)

            if newPrice > (1.0005):
                found_pair = BNB_Path
                percentage = (100 * ((newPrice / 1.0) - 1))
                pathValue1 = self.getAskValueInUSDT(currSplit[1] + currSplit[0])
                pathValue2 = self.getAskValueInUSDT(currSplit[2] + currSplit[1])
                pathValue3 = self.getBidValueInUSDT(currSplit[2] + currSplit[0])

                self.all_percentages.append([found_pair, percentage, pathValue1, pathValue2, pathValue3])

        for USDT_Path in self.USDT_Opps:
            currSplit = USDT_Path.split('_')
            principle = 1.0

            step1 = principle * float(self.getAskPrice(currSplit[0] + currSplit[1])) * (1.0 - self.transactionFee)
            # print('1 {} buys {} {}'.format(currSplit[0], step1, currSplit[1]))
            step2 = step1 / float(self.getAskPrice(currSplit[2] + currSplit[1])) * (1.0 - self.transactionFee)
            # print('{} {} buys {} {}'.format(step1,currSplit[1], step2, currSplit[2]))
            newPrice = step2 * float(self.getBidPrice(currSplit[2] + currSplit[0])) * (1.0 - self.transactionFee)
            # print('{} {} buys {} {}'.format(step2, currSplit[2], newPrice, currSplit[0]))

            if newPrice > (1.0005):
                found_pair = USDT_Path
                percentage = (100 * ((newPrice / 1.0) - 1))
                pathValue1 = self.getAskValueInUSDT(currSplit[0] + currSplit[1])
                pathValue2 = self.getAskValueInUSDT(currSplit[2] + currSplit[1])
                pathValue3 = self.getBidValueInUSDT(currSplit[2] + currSplit[0])

                self.all_percentages.append([found_pair, percentage, pathValue1, pathValue2, pathValue3])


            # print('Net Gain: {}'.format((100*((newPrice/1.0) - 1)))))
            # print('Net Gain: {}'.format((100*((newPrice/1.0) - 1))))
            # print(getPrice(all_opps[-1][0].split('_')[2] + all_opps[-1][0].split('_')[1]))


def main():
    bot = TryBotDataScraper()
    # print(bot.getAskValueInUSDT('TRXETH'))
    # Open csv file
    csv_tag = time.strftime('%b_%d_%H_%M_%S')
    csv_file = open('found_data_{}.csv'.format(csv_tag), 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['path', 'percentage', 'path1', 'path2', 'path3', 'time'])

    timeTotal = time.time()

    # Run this continoously
    # x = 1
    x = float(input("Minutes would you like to test for: "))
    print("Testing for for {} seconds | {} hours | {} days".format(
        x * 60, x / 60, (x / (60 * 24))))


    totalSecond = x * 60
    while (time.time() - timeTotal) < totalSecond:

        bot.resetVals()
        t0 = time.time()
        bot.createCurrencyPairs()
        bot.createCurrencyOpps()
        bot.createTripletData()

        # If there exists a triplet path, print it
        if len(bot.all_percentages) > 0:
            all_opps = np.array(bot.all_percentages)

            # Sort the list of found triplets in ascending order based on % gain
            all_opps = all_opps[np.argsort(all_opps[:, 1])]
            print(all_opps[:, :6])

            # Create time stamp for csv file
            time_stamp = time.strftime('%b %d %H:%M:%S')

            for i in all_opps:
                if (i[2] > 10) and (i[3] > 10) and (i[4] > 10):
                    csv_writer.writerow([i[0], i[1], i[2], i[3], i[4], time_stamp])
        else:
            print('No Triplets Found.')
        bot.updateOrders()
        print()

        # print('Runtime {} seconds'.format(time.time() - t0))

    csv_file.close()
    print("Total time took {} seconds".format(time.time() - timeTotal))


if __name__ == '__main__':
    main()
