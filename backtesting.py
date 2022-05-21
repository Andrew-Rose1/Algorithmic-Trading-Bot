from ib_insync import *
from datetime import time, datetime
import math
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

"""
Project Name: Alogirhtmic Backtesting Bot
Purpose: The purpose of this program is to use computer algorithms to quickly and accurately
         analyze years worth of ticker data, and apply trading strategies to that data. We can then see
         exactly when a trade is executed and see if a specific strategy could potentially be profitable.
"""

plt.style.use('fivethirtyeight')
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)


class Bot:
    def __init__(self):
        # Define starting account size for backtesting
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
        total = 0
        total100 = 0
        total200 = 0
        self.pdCash = []
        # Used if day trading  
        # self.daysLeft = 0

        # Define Cotract Object to hold Ticket information
        contract = Contract()
        contract.symbol = "SPY"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = "NASDAQ"
        self.tickerName = contract.symbol

        # Get bar data for ticket
        # Use panda data structure
        dt = ''
        self.backtestPeriod = '1 D'
        self.bars = ib.reqHistoricalData(
            contract,
            endDateTime=dt,
            durationStr=self.backtestPeriod,
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1)
        self.dfPanda = util.df(self.bars)
        self.currentHigh = self.bars[0].high
        self.pdCash.append(self.cash)



        # Analyze ticker bar data
        for b in range(0, len(self.bars)):
            self.pdCash.append(self.cash + (self.shares * self.bars[b].close))

            # Store ticket data for past 7 days
            SevenDays = []
            for m in range(b-7, b):
                SevenDays.append(self.bars[m].close)
            self.days7_Low = min(SevenDays)
            self.days7_High = max(SevenDays)

            # Find and store highest close price in past 2 months
            passHighToCheck = []
            for m in range(b-58, b):
                passHighToCheck.append(self.bars[m].close)
            self.highToCheck2 = max(passHighToCheck)
            passHighToCheck.clear()

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
            print(self.bars[b])

            # Used if day trading
            """
            if self.cash < 25000 and self.daysLeft == 0:
                self.backTestingBreakoutStrategy2(self.bars[b], self.highToCheck2)
            elif self.bars[b].date.date() != self.bars[b-1].date.date():
                self.daysLeft -= 1
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
            else:
                self.sigPriceBuy.append(np.nan)
                self.sigPriceSell.append(np.nan)
            """

            # Call any Trading Strategy
            # Paramaters (current bar data, ...)
            self.backTestingBreakoutStrategy2(self.bars[b], self.highToCheck2)


        # On lats bar: Sell reaming shares at bar close price
        if self.shares > 0:
            self.cash += self.shares * self.bars[len(self.bars)-1].close
            self.pdCash.append(self.cash)
        
        # Configure panda data frame
        self.dfPanda['50SMA'] = self.sma50Tracker
        self.dfPanda['100SMA'] = self.sma100Tracker
        self.dfPanda['200SMA'] = self.sma200Tracker
        self.dfPanda['Buy_Signal'] = self.sigPriceBuy
        self.dfPanda['Sell_Signal'] = self.sigPriceSell

        # Optional: Create GUI plot
        plt.figure(figsize=(12.6, 4.6))
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

        # Console output
        print("==== RESULTS AFTER " + self.backtestPeriod + " ====")
        print("Starting cash: $" + str(self.startingCash))
        print("Ending cash: $" + str(self.cash))
        print("% Gain/Loss: " + str(((self.cash-self.startingCash)/self.startingCash)*100) + "%")
        print("Ending shares: " + str(self.shares))
        print("Number of trades made: " + str(len(self.trades)))

        # Save results ot a csv
        ####### COLUMNS ########
        # Ticket               #
        # Trade Execution Data #
        # Shares               #
        # Buy/Sell Price       #
        # P/L $                #
        # P/L %                #
        ########################
        f = open("trades.csv", "w", newline = '')
        writer = csv.writer(f)
        writer.writerow([" "," "," "," "," ","Totals:", self.cash-self.startingCash, ((self.cash-self.startingCash)/self.startingCash)*100])
        for i in range (0, len(self.trades)):
            writer.writerow([self.trades[i][0], self.trades[i][1], self.trades[i][2], self.trades[i][3], self.trades[i][4], ' ', round(self.profits[i],2), self.percentGains[i]])
        f.close()

        # Show Plot
        plt.show()



    def historicalPlaceBuyOrder(self, buyIn, time):
        tempshares = math.floor(self.cash/buyIn)
        self.shares = tempshares
        self.cash -= tempshares * buyIn
        trade = [self.tickerName, str(time), str(tempshares), str(buyIn), "buy"]
        self.trades.append(trade)
        self.profits.append(np.nan)
        self.percentGains.append(np.nan)

    def historicalPlaceSellOrder(self, sellOut, time):
        trade = [self.tickerName, str(time), str(self.shares), str(sellOut), "sell"]
        profit = (float(trade[3]) - float(self.trades[-1][3])) * int(self.trades[-1][2])
        percentGain = profit/(int(self.trades[-1][2])*float(self.trades[-1][3]))
        self.trades.append(trade)
        self.profits.append(profit)
        self.percentGains.append(percentGain)
        self.cash += self.shares * sellOut
        self.shares = 0
        # Used if day trading    
        # self.daysLeft = 2




    ######################################
    # Define backTesting Strategies Here #
    ######################################

    # Breakout strategy
    def backTesting_breakout(self, bar, highToCheck):
        print(str(self.currentLow))
        if (bar.open_ > highToCheck *1.025) and (self.opentrades < 1) and self.recentlySold < 1:
            self.historicalPlaceBuyOrder(bar.open_, bar.date)
            self.support = highToCheck
            self.opentrades = 1
        elif (bar.open_ >= self.currentLow * 1.01) and (self.opentrades < 1) and (bar.open_ > highToCheck) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open_, bar.date)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open_ < self.support*0.975 or bar.open_ < self.currentHigh*0.95:
                self.historicalPlaceSellOrder(bar.open_, bar.date)
                self.opentrades = 0
                self.recentlySold = 1
                self.currentLow = bar.low
                self.currentHigh = bar.open_
        if bar.open_ > self.currentHigh:
            self.currentHigh = bar.open_
        if bar.low < self.currentLow:
            self.currentLow = bar.low


    # Daily Candles only
    # Buy: current day closes below 7 day low AND closes above 200sma
    # Sell: Close above 7 day high OR SL of -3% is hit
    def test7day(self, bar, dayLow7, dayHigh7, ma200):
        if (bar.close < dayLow7) and (bar.close > ma200) and (self.opentrades < 1):
            self.historicalPlaceBuyOrder(bar.close, bar.date)
            self.stopLoss = bar.close * 0.03
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


    # Currently only for daily candles. Utilizies basic 50ma strategy
    def backTesting_daily_50SMA(self, bar, sma50):
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
    def backTesting_dip_v1(self, bar):
        if (bar.open <= self.currentHigh * 0.98) and (self.opentrades < 1):
            self.currentHigh = bar.close
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


    # Simple dip buy strategy, waits to buy after a rise off of new low
    def backTesting_dip_v2(self, bar):
        if (bar.open <= self.currentHigh * 0.98) and (self.opentrades < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.005) and (self.opentrades < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
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


    # Simple dip buy strategy, waits to buy after a rise off of new low (for small cap)
    def backTesting_smallCapDip(self, bar):
        if (bar.open <= self.currentHigh * 0.98) and (self.opentrades < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.02) and (self.opentrades < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
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


    # Bounce off of 50SMA
    def backTesting_50SMA_bounce(self, bar, sma50):
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


    # Buy after 50SMA crosses over 100SMA
    def backTestingStrategy_50cross100(self, bar, ma50, ma100):
        if (self.opentrades < 1) and (ma50 > ma100):
            self.currentHigh = bar.high
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif ((ma50 < ma100 * 1) and (self.opentrades >= 1)) or ((bar.open < self.currentHigh*0.97) and (self.opentrades >= 1)):
            self.historicalPlaceSellOrder(bar.open, bar.date)
            self.sigPriceSell.append(bar.close)
            self.sigPriceBuy.append(np.nan)
            self.opentrades = 0
        else:
            self.sigPriceBuy.append(np.nan)
            self.sigPriceSell.append(np.nan)
        if bar.high > self.currentHigh:
            self.currentHigh = bar.high


    # Variation to dip buy strategy (work in progress...)
    def backTesting_dip_v3(self, bar):
        if (bar.open <= self.currentHigh * 0.95) and (self.opentrades < 1):
            self.currentHigh = bar.close
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


    # Variation to dip buy strategy (work in progress...)
    def backTesting_dip_v4(self, bar):
        eod = bar.date.replace(hour=12, minute=50)
        if (bar.open <= self.currentHigh * 0.97) and (self.opentrades < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.015) and (self.opentrades < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
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


    # Variation to breakout strategy (work in progress...)
    def backTesting_breakout_v1(self, bar, highToCheck):
        if (bar.open > highToCheck) and (self.opentrades < 1) and self.recentlySold < 1:
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.support = highToCheck
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.01) and (self.opentrades < 1) and (bar.open > highToCheck) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
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


    # Small cap: Variation to breakout strategy (work in progress...) 
    def backTesting_breakout_v2(self, bar, highToCheck):
        if (bar.open > highToCheck) and (self.opentrades < 1) and self.recentlySold < 1:
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.support = highToCheck
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.01) and (self.opentrades < 1) and (bar.open > highToCheck) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.support = highToCheck
            self.sigPriceBuy.append(bar.open)
            self.sigPriceSell.append(np.nan)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open < self.support*0.95 or bar.open < self.currentHigh*0.965:
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


# Start Backtesting Bot
bot = Bot()
