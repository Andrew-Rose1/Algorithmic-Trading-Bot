from ib_insync import *
import datetime
import math
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


"""
 -- To Do:
    --- Have CVS ouput statistics at the top (above all the trades)

"""

plt.style.use('fivethirtyeight')

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)


file = open('stocks.txt', 'r')
tickerList = file.readlines()
file.close()


class Bot:
    def __init__(self):
        self.cash = 10000
        self.startingCash = self.cash
        self.shares = 0
        self.opentrades = 0
        self.trades = []
        self.currentLow = 0;
        self.recentlySold = 0
        self.sigPriceBuy = []
        self.sigPriceSell = []
        self.sma50Tracker = []
        self.sma100Tracker = []
        self.sma200Tracker = []
        self.profits = []
        self.percentGains = []
        self.support = 0
        self.highest = []
        self.daysLeft = 0
        total = 0
        total100 = 0
        total200 = 0
        self.pdCash = []


        contract = Contract()
        contract.symbol = "SPY"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = "NASDAQ"

        self.tickerName = contract.symbol

        #dt = '20210101 00:00:00 PST'
        dt = ''
        self.backtestPeriod = '5 Y'
        self.bars = ib.reqHistoricalData(
            contract,
            endDateTime=dt,
            durationStr=self.backtestPeriod,
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1)
        print("Bars size: " + str(len(self.bars)))
        self.dfPanda = util.df(self.bars)
        #print(dfPanda)
        #dfPanda.plot()
        #plt.show()
        self.currentHigh = self.bars[0].high
        self.pdCash.append(self.cash)


        for b in range(0, len(self.bars)):
            self.pdCash.append(self.cash + (self.shares * self.bars[b].close))

            SevenDays = []
            for m in range(b-7, b):
                SevenDays.append(self.bars[m].close)
            self.days7_Low = min(SevenDays)
            self.days7_High = max(SevenDays)

            passHighToCheck = []
            for m in range(b-60, b):
                passHighToCheck.append(self.bars[m].close)
            self.highToCheck2 = max(passHighToCheck)

            # Calculate 50 SMA
            if b > 50:
                for i in range (b-50, b):
                    total += self.bars[i].close
                self.sma50 = total/50
                self.sma50Tracker.append(self.sma50)
                total = 0
            else:
                self.sma50 = np.nan
                self.sma50Tracker.append(np.nan)

            # Calculate 100 SMA
            if b > 100:
                for i in range (b-100, b):
                    total100 += self.bars[i].close
                    self.highest.append(self.bars[i].open)
                self.sma100 = total100/100
                self.highestOpenLast100Bars = max(self.highest)
                self.highest.clear()
                total100 = 0
                self.sma100Tracker.append(self.sma100)
            else:
                self.sma100 = np.nan
                self.sma100Tracker.append(np.nan)

            # Calculate 200 SMA
            if b > 200:
                for i in range (b-200, b):
                    total200 += self.bars[i].close
                self.sma200 = total200/200
                total200 = 0
                self.sma200Tracker.append(self.sma200)
            else:
                self.sma200 = np.nan
                self.sma200Tracker.append(np.nan)


            print(self.bars[b].date)
            if self.daysLeft == 0:
                print("CAN TRADE")
                #self.test7day(self.bars[b], self.days7_Low, self.days7_High, self.sma200)
                #self.backTestingBreakoutStrategy1(self.bars[b], self.highestOpenLast100Bars)
                #self.backTestingStrategy2(self.bars[b], self.sma50)
                #self.backTestingStrategy4(self.bars[b],self.sma50)
                #self.backTestingBreakoutStrategy1(self.bars[b], self.highestOpenLast100Bars)
                #self.backTestingStrategy_50cross100(self.bars[b], self.sma50, self.sma100)

                #self.backTestingBreakoutStrategy1(self.bars[b], self.highToCheck2)
                #     #self.backTestingStrategy1(self.bars[b])
                #     #self.NioStrategy2(self.bars[b])
                #     self.backTestingStrategy1_v3(self.bars[b])
                self.backTestingStrategy1_v2(self.bars[b])
            elif self.bars[b].date != self.bars[b-1].date:
                self.daysLeft -= 1
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)

        # Sell reaming shares at last bar close
        if self.shares > 0:
            self.cash += self.shares * self.bars[len(self.bars)-1].close
            self.pdCash.append(self.cash)
        #dfCash = util.df(self.pdCash)
        #print(self.pdCash)
        #util.barplot(self.bars)
        plt.figure(figsize=(12.6, 4.6))
        self.dfPanda['50SMA'] = self.sma50Tracker
        self.dfPanda['100SMA'] = self.sma100Tracker
        self.dfPanda['200SMA'] = self.sma200Tracker
        self.dfPanda['Buy_Signal'] = self.sigPriceBuy
        self.dfPanda['Sell_Signal'] = self.sigPriceSell
        plt.plot(self.dfPanda['close'], label = 'Close', alpha = 0.35)
        plt.plot(self.dfPanda['50SMA'], label = '50SMA', alpha = 0.35)
        plt.plot(self.dfPanda['100SMA'], label = '100SMA', alpha = 0.35)
        plt.plot(self.dfPanda['200SMA'], label = '200SMA', alpha = 0.35)
        plt.scatter(self.dfPanda.index, self.dfPanda['Buy_Signal'], label = 'Buy', marker = '^', color = 'green')
        plt.scatter(self.dfPanda.index, self.dfPanda['Sell_Signal'], label = 'Sell', marker = 'v', color = 'red')
        plt.title(self.tickerName + ": Start: \$" + str(round(self.startingCash,2)) + " ---> \$" + str(round(self.cash,2)) + "   (" +str(round(((self.cash-self.startingCash)/self.startingCash)*100,2)) + "%)" )
        plt.xlabel(self.backtestPeriod)
        plt.ylabel("Close Price")
        plt.legend(loc='upper left')

        print("==== END STATS AFTER " + self.backtestPeriod + " ====")
        print("Starting cash: $" + str(self.startingCash))
        print("Ending cash: $" + str(self.cash))
        print("% Gain/Loss: " + str(((self.cash-self.startingCash)/self.startingCash)*100) + "%")
        print("Ending shares: " + str(self.shares))
        print("Number of trades made: " + str(len(self.trades)))
        f = open("trades.csv", "w", newline = '')
        writer = csv.writer(f)
        writer.writerow([" "," "," "," "," "," ","Totals:", self.cash-self.startingCash, ((self.cash-self.startingCash)/self.startingCash)*100])
        for i in range (0, len(self.trades)):
            writer.writerow([self.trades[i][0], self.trades[i][1], self.trades[i][2], self.trades[i][3], self.trades[i][4], self.trades[i][5], ' ', round(self.profits[i],2), self.percentGains[i]])
        f.close()
        plt.show()



    def historicalPlaceBuyOrder(self, buyIn, time):
        tempshares = math.floor(self.cash/buyIn)
        self.shares = tempshares
        self.cash -= tempshares * buyIn
        trade = [self.tickerName, str(time), str(tempshares), str(buyIn), "buy", "currentHigh*0.97: " + str(self.currentHigh*0.97)]
      # trade = [self.tickerName, str(time), str(tempshares), str(buyIn), "buy", "currentHigh*0.97: " + str(self.currentHigh*0.97), "50SMA: " + str(sma50)]

        self.trades.append(trade)
        self.profits.append(np.nan)
        self.percentGains.append(np.nan)

        #print("Adding to self.trades: " + str(time) + ": " + str(tempshares) + " shares of SPY bought at " + str(buyIn))
        #hardStopLoss = buyIn * 0.93

    def historicalPlaceSellOrder(self, sellOut, time):
        trade = [self.tickerName, str(time), str(self.shares), str(sellOut), "sell", "currentHigh*0.97: " + str(self.currentHigh*0.97)]
        #trade = [self.tickerName, str(time), str(self.shares), str(sellOut), "sell", "currentHigh*0.97: " + str(self.currentHigh*0.97), "50SMA: " + str(sma50)]
        #print("Adding to self.trades: " + str(time) + ": " + str(self.shares) + " shares of SPY sold at " + str(sellOut))
        profit = (float(trade[3]) - float(self.trades[-1][3])) * int(self.trades[-1][2])
        percentGain = profit/(int(self.trades[-1][2])*float(self.trades[-1][3]))
        self.trades.append(trade)
        self.profits.append(profit)
        self.percentGains.append(percentGain)
        self.cash += self.shares * sellOut
        self.shares = 0

        self.daysLeft = 2
        #self.pdCash.append(self.cash)

    # Daily Candles only
    # Buy: current day closes below 7 day low AND closes above 200sma
    # Sell: Close above 7 day high OR SL of -17% is hit
    def test7day(self, bar, dayLow7, dayHigh7, ma200):
        if (bar.close < dayLow7) and (bar.close > ma200) and (self.opentrades < 1):
            self.historicalPlaceBuyOrder(bar.close, bar.date)
            self.stopLoss = bar.close * 0.10
            self.sigPriceBuy.append(bar.close)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif (self.opentrades >= 1):
            if (bar.close > dayHigh7) or (bar.close < self.stopLoss):
                self.historicalPlaceSellOrder(bar.close, bar.date)
                self.sigPriceSell.append(bar.close)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)

    # Currently only for daily candles, basic 50ma strat
    def backTestingStrategy2(self, bar, sma50):
        if (bar.open > sma50) and (self.opentrades < 1):
            self.currentHigh = bar.high
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.close < sma50:
                self.historicalPlaceSellOrder(bar.close, bar.date)
                self.sigPriceSell.append(bar.close)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
            else:
                self.sigPriceSell.append(np.nan)
                self.sigPriceBuy.append(np.nan)
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.high > self.currentHigh:
            self.currentHigh = bar.high

    # Simple dip buy strategy
    def backTestingStrategy1(self, bar):
        if (bar.open <= self.currentHigh * 0.98) and (self.opentrades < 1):
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.close <= self.currentHigh * 0.97:
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.sigPriceSell.append(bar.close)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.close > self.currentHigh:
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))


        # Simple dip buy strategy, this one includes a wait condition after selling

    # Simple dip buy strategy, waits to buy after a rise off of new low
    def backTestingStrategy1_v2(self, bar):
        if (bar.open <= self.currentHigh * 0.98) and (self.opentrades < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.005) and (self.opentrades < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open <= self.currentHigh * 0.99:
                self.currentLow = bar.low
                self.recentlySold = 1
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.sigPriceSell.append(bar.close)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.open > self.currentHigh:
            self.currentHigh = bar.open
        if bar.open < self.currentLow:
            self.currentLow = bar.open
            #print("Setting currentHigh to: " + str(bar.close))


    # Simple dip buy strategy, waits to buy after a rise off of new low (PENNYSTOCKS)
    def backTestingStrategy1_v3(self, bar):
        if (bar.open <= self.currentHigh * 0.98) and (self.opentrades < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.02) and (self.opentrades < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open <= self.currentHigh * 0.95:
                self.currentLow = bar.low
                self.recentlySold = 1
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.sigPriceSell.append(bar.close)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.open > self.currentHigh:
            self.currentHigh = bar.open
        if bar.open < self.currentLow:
            self.currentLow = bar.open
            #print("Setting currentHigh to: " + str(bar.close))

    # 3) Bounce off of 50SMA
    #   if above 50SMA and touches it ---> buy
    #       NOT IMPLEMENTED YET:   if falls 2% below 50SMA ---> sell
    #       set a trailing stop loss otherwise 2%
    def backTestingStrategy4(self, bar, sma50):
        if sma50 != np.nan:

            if bar.low >= sma50:
                isAbove50SMA = True
            else:
                isAbove50SMA = False
            if (isAbove50SMA) and (bar.low >= sma50 * 0.98) and (self.opentrades < 1):
                self.currentHigh = bar.high
                self.historicalPlaceBuyOrder(bar.open, bar.date)
                self.sigPriceBuy.append(bar.open)
                self.sigPriceSell.append(np.nan)
                self.opentrades = 1
            elif self.opentrades >= 1:
                if bar.close < self.currentHigh*0.97:
                    self.historicalPlaceSellOrder(bar.close, bar.date)
                    self.sigPriceSell.append(bar.close)
                    self.sigPriceBuy.append(np.nan)
                    self.opentrades = 0
                else:
                    self.sigPriceSell.append(np.nan)
                    self.sigPriceBuy.append(np.nan)
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
            if bar.high > self.currentHigh:
                self.currentHigh = bar.high
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)

    def backTestingStrategy_50cross100(self, bar, ma50, ma100):
        if (self.opentrades < 1) and (ma50 > ma100):
            print("BUYING -- 50: " + str(ma50) + "  100: " + str(ma100))
            self.currentHigh = bar.high
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif ((ma50 < ma100 * 1) and (self.opentrades >= 1)) or ((bar.open < self.currentHigh*0.97) and (self.opentrades >= 1)):
            print("SELLING -- 50: " + str(ma50) + "  100: " + str(ma100))
            self.historicalPlaceSellOrder(bar.open, bar.date)
            self.sigPriceSell.append(bar.close)
            self.sigPriceBuy.append(np.nan)
            self.opentrades = 0
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.high > self.currentHigh:
            self.currentHigh = bar.high

    # Simple dip buy strategy
    def NioStrategy1(self, bar):
        if (bar.open <= self.currentHigh * 0.95) and (self.opentrades < 1):
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.close <= self.currentHigh * 0.98:
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.sigPriceSell.append(bar.close)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.close > self.currentHigh:
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))

    def NioStrategy2(self, bar):
        eod = bar.date.replace(hour=12, minute=50)
        print(bar.date)
        print(eod)
        if (bar.open <= self.currentHigh * 0.97) and (self.opentrades < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            #self.ptd[bar.date] = True
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.015) and (self.opentrades < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.close <= self.currentHigh * 0.955:
                self.currentLow = bar.low
                self.recentlySold = 1
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.sigPriceSell.append(bar.close)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
            elif bar.date >= eod:
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.sigPriceSell.append(bar.close)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
                self.currentLow = bar.low
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)

        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.close > self.currentHigh:
            self.currentHigh = bar.close
        if bar.low < self.currentLow:
            self.currentLow = bar.low
            #print("Setting currentHigh to: " + str(bar.close))

    def backTestingBreakoutStrategy1(self, bar, highToCheck):
        #print(str(self.opentrades))
        print(str(self.currentLow))
        if (bar.open > highToCheck) and (self.opentrades < 1) and self.recentlySold < 1:
            print("BUYING... highToCheck: " + str(highToCheck))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.support = highToCheck
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.01) and (self.opentrades < 1) and (bar.open > highToCheck) and (self.recentlySold >= 1):
            print("BUYING #2... highToCheck: " + str(highToCheck) + "   currentLow: " + str(self.currentLow))
            self.currentHigh = bar.close
            #print("Setting currentHigh to: " + str(bar.close))
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open < self.support*0.99 or bar.open < self.currentHigh*0.955:
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.sigPriceSell.append(bar.open)
                self.sigPriceBuy.append(np.nan)
                self.opentrades = 0
                self.recentlySold = 1
                self.currentLow = bar.low
                self.currentHigh = bar.open
            else:
                self.sigPriceSell.append(np.nan)
                self.sigPriceBuy.append(np.nan)
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.open > self.currentHigh:
            self.currentHigh = bar.open
        if bar.low < self.currentLow:
            self.currentLow = bar.low



bot = Bot()

# STRATEGY IDEAS
#
#
# 1)
# grab historical data from x 50 days back and calculate 50SMA
#   if current price below 50ma, and breaks above ---> buy
#   if current price above 50ma, and bounce off -----> buy
#
#   if fall below 2.5% of buy in ----> sell
#   keep track of new high from here on out
#       if fall 1.75% below this high ----> sell
#
#
# 2)
#   50SMA crosses over 100SMA ---> buy
#   50SMA crosses under 100SMA ---> sell
#
#
