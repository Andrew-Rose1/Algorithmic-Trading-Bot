from ib_insync import *
from datetime import datetime, time, timedelta
#import datetime
import numpy as np
import time
import math
import nest_asyncio
from functools import partial

nest_asyncio.apply()

"""
 To Do:
    -- Make it so when a buy order is placed, the current ticker is tracked and only that one
       is scanned, then keep track of those lows and only sell that one?

       if recently sold == 1 then all tickers, even if not bought, will try to sell

"""


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

class NioBot:
    def __init__(self):
        self.now = datetime.now()
        self.dayStart = self.now.replace(hour=6, minute=30, second=0)
        print(self.now)
        print(self.dayStart)
        print(self.now - self.dayStart)
        self.currentHigh = 0
        self.currentLow = 0
        self.opentrades = 0
        self.recentlySold = 0
        self.currentLOD = 0
        self.support = 0


        sub = ScannerSubscription(
            instrument='STK',
            locationCode='STK.US.MAJOR',
            scanCode='TOP_PERC_GAIN')

        tagValues = [
            TagValue("changePercAbove", "20"),
            TagValue('priceAbove', 1),
            TagValue('priceBelow', 20),
            TagValue('volumeAbove', 200000)]

        # the tagValues are given as 3rd argument; the 2nd argument must always be an empty list
        # (IB has not documented the 2nd argument and it's not clear what it does)
        scanData = ib.reqScannerData(sub, [], tagValues)
        symbols = [sd.contractDetails.contract.symbol for sd in scanData]
        print(symbols)

        tillMorning = (self.now-self.dayStart).total_seconds()
        print(tillMorning)
        print(tillMorning/60)
        print((tillMorning/60)/60)

        newMorn = str(math.floor(tillMorning)) + " S"
        print(newMorn)

        #
        # for i in symbols:
        #     print(i)
        #stock = Stock("ANY", 'SMART', 'USD')
        #market_data = ib.reqMktData(stock, '', False, False)
        #     time.sleep(2)
        #ib.pendingTickersEvent += self.onPendingTicker
        #self.catchUp(stock)
        #self.scannerTest()

        # self.contract = Contract()
        # self.contract.symbol = "SQBG"
        # self.contract.secType = "STK"
        # self.contract.exchange = "SMART"
        # self.contract.currency = "USD"
        # self.contract.primaryExchange = "NASDAQ"

        for i in symbols:
            print(i)
            stock = Stock("BTCM", 'SMART', 'USD')
            #self.catchUp(stock)
            bars = ib.reqRealTimeBars(contract, 1, 'TRADES', False)
            bars.updateEvent += self.onBarUpdate


            #time.sleep(2)
            #market_data = ib.reqMktData(stock, '', False, False)
            #ib.pendingTickersEvent += self.onPendingTicker
        time.sleep(2)
        ib.run()


    # def onPendingTicker(self, ticker):
    #     print("pending ticker event recieved")
    #     print(ticker)
    #     #print(type(ticker))
    #     # d = {i: (c.contract.symbol, c.close) for (i, c) in enumerate(tickers)}
    #     # ib.loopUntil(any(np.isnan(val) for val in d.values()), len(tickers))
    #     #self.NioStrategy2(ticker)

    # def scannerTest(self):
    #     sub = ScannerSubscription(
    #         instrument='STK',
    #         locationCode='STK.US.MAJOR',
    #         scanCode='TOP_PERC_GAIN')
    #
    #     tagValues = [
    #         TagValue("changePercAbove", "20"),
    #         TagValue('priceAbove', 1),
    #         TagValue('priceBelow', 50),
    #         TagValue('volumeAbove', 200000)]
    #
    #     # the tagValues are given as 3rd argument; the 2nd argument must always be an empty list
    #     # (IB has not documented the 2nd argument and it's not clear what it does)
    #     scanData = ib.reqScannerData(sub, [], tagValues)
    #
    #     symbols = [sd.contractDetails.contract.symbol for sd in scanData]
    #     print(symbols)

    # def catchUp(self, contract):
    #     total = []
    #     # bars1 = ib.reqHistoricalData(
    #     #     contract,
    #     #     endDateTime='',
    #     #     durationStr='7200 S',
    #     #     barSizeSetting='1 min',
    #     #     whatToShow='TRADES',
    #     #     useRTH=True,
    #     #     formatDate=1)
    #     #     #time.sleep(2)
    #     # for i in bars1:
    #     #     total.append(i.high)
    #     # self.currentHOD = max(total)
    #     # self.currentLOD = min(total)
    #     # total.clear()
    #     # self.currentHigh = self.currentHOD
    #     # self.highToCheck = self.currentHigh
    #     # self.currentLow = self.currentLOD
    #     bars = ib.reqRealTimeBars(contract, 1, 'TRADES', False)
    #     bars.updateEvent += self.onBarUpdate
    #     #bars.updateEvent += partial(self.onBarUpdate, contract)
    #     #print(len(self.bars))

    def onBarUpdate(self, bar, hasNewBar):
        print("pending bar event recieved")
        self.now = datetime.now()
        tillMorning = (self.now-self.dayStart).total_seconds()
        newMorn = str(math.floor(tillMorning)) + " S"
        total = []
        print("Contract: " + str(bar.contract.symbol))
        bars2hoursBack = ib.reqHistoricalData(
            bar.contract,
            endDateTime='',
            durationStr=newMorn,
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1)
        print("SIZE: " + str(len(bars2hoursBack)))
        for i in bars2hoursBack:
            total.append(i.high)
        #total.sort()
        #print(total)
        #print(max(total))
        self.highToCheck = max(total[:-2])
        #time.sleep(2)
        #print(self.highToCheck)
        self.lowToCheck = max(total[-60:-2])
        total.clear()
        #print("Size: " + str(len(total)))
        #total.clear()
        # self.currentHigh = self.highToCheck
        # self.highToCheck = self.currentHigh
        #print("open: " + str(bar[-1].open_))
        #self.backTestingStrategy1_v3(bar)

        # Only trade after 5 mins
        if len(bars2hoursBack > 4):
            self.backTestingBreakoutStrategy1(bar[-1], self.highToCheck, self.lowToCheck, bar.contract.symbol)
        print(bar[-1])
        #print(bar[-1].high)

    # def NioStrategy1(self, bar):
    #     if (bar.open <= self.currentHigh * 0.98) and (self.opentrades < 1) and (self.recentlySold < 1):
    #         self.currentHigh = bar.close
    #         #print("Setting currentHigh to: " + str(bar.close))
    #         self.historicalPlaceBuyOrder(bar.open, bar.date)
    #         self.sigPriceBuy.append(bar.open)
    #         self.sigPriceSell.append(np.nan)
    #         self.opentrades = 1
    #     elif (bar.open >= self.currentLow * 1.015) and (self.opentrades < 1) and (self.recentlySold >= 1):
    #         self.currentHigh = bar.close
    #         #print("Setting currentHigh to: " + str(bar.close))
    #         self.historicalPlaceBuyOrder(bar.open, bar.date)
    #         self.sigPriceBuy.append(bar.open)
    #         self.sigPriceSell.append(np.nan)
    #         self.opentrades = 1
    #     elif self.opentrades >= 1:
    #         if bar.close <= self.currentHigh * 0.99:
    #             self.currentLow = bar.low
    #             self.recentlySold = 1
    #             self.historicalPlaceSellOrder(bar.open, bar.date)
    #             self.sigPriceSell.append(bar.close)
    #             self.sigPriceBuy.append(np.nan)
    #             self.opentrades = 0
    #         else:
    #             self.sigPriceBuy.append(np.nan)
    #             self.sigPriceSell.append(np.nan)
    #     else:
    #         self.sigPriceBuy.append(np.nan)
    #         self.sigPriceSell.append(np.nan)
    #     if bar.close > self.currentHigh:
    #         self.currentHigh = bar.close
    #     if bar.low < self.currentLow:
    #         self.currentLow = bar.low
    #         #print("Setting currentHigh to: " + str(bar.close))

    # Simple dip buy strategy, waits to buy after a rise off of new low (PENNYSTOCKS)
    def backTestingStrategy1_v3(self, bar):
        print("currentHigh: " + str(self.currentHigh))
        if (bar.open_ <= self.currentHigh - 0.02) and (self.opentrades < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open_, bar.time)
            self.opentrades = 1
        elif (bar.open_ >= self.currentLow * 1.02) and (self.opentrades < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open_, bar.time)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open_ <= self.currentHigh * 0.95:
                self.currentLow = bar.low
                self.recentlySold = 1
                self.historicalPlaceSellOrder(bar.open_, bar.time)
                self.opentrades = 0
        if bar.high > self.currentHigh:
            self.currentHigh = bar.high
        if bar.low < self.currentLow:
            self.currentLow = bar.low

    def NioStrategy2(self, tick):
        eod = tick.time.replace(hour=12, minute=50)
        print(tick.time)
        print(eod)
        if (tick.last <= self.currentHigh * 0.97) and (len(ib.positions()) < 1) and (self.recentlySold < 1):
            self.currentHigh = tick.last
            self.historicalPlaceBuyOrder(tick.last, tick.time)
        elif (tick.last >= self.currentLow * 1.015) and (len(ib.positions()) < 1) and (self.recentlySold >= 1):
            self.currentHigh = tick.last
            self.historicalPlaceBuyOrder(tick.last, tick.time)
        elif len(ib.positions()) >= 1:
            if tick.last <= self.currentHigh * 0.955:
                self.currentLow = tick.last
                self.recentlySold = 1
                self.historicalPlaceSellOrder(tick.last, tick.time)
            elif tick.time >= eod:
                self.historicalPlaceSellOrder(tick.last, tick.time)
                self.currentLow = tick.last
        if tick.last > self.currentHigh:
            self.currentHigh = tick.last
        if tick.last < self.currentLow:
            self.currentLow = tick.last

    def NioStrategy2_bar(self, bar):
        eod = bar.date.replace(hour=12, minute=50)
        print(bar.date)
        print(eod)
        if (bar.open <= self.currentHigh * 0.97) and (len(ib.positions()) < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.015) and (len(ib.positions()) < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open, bar.date)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.close <= self.currentHigh * 0.955:
                self.currentLow = bar.low
                self.recentlySold = 1
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.opentrades = 0
            elif bar.date >= eod:
                self.historicalPlaceSellOrder(bar.open, bar.date)
                self.opentrades = 0
                self.currentLow = bar.low
        if bar.close > self.currentHigh:
            self.currentHigh = bar.close
        if bar.low < self.currentLow:
            self.currentLow = bar.low

    def backTestingBreakoutStrategy1(self, bar, highToCheck, lowToCheck, ticker):
        #print(str(self.opentrades))
        print("high to check: " + str(highToCheck))
        print("price to sell:  if below " + str(lowToCheck*0.975) + "  or  if below " + str(highToCheck*0.95))
        #print("price to buy: " + str(highToCheck*1.005))
        if (bar.open_ > highToCheck) and (self.opentrades < 1) and self.recentlySold < 1:
            print("BUYING... highToCheck: " + str(highToCheck))
            self.historicalPlaceBuyOrder(bar.open_, bar.time, ticker)
            # self.support = highToCheck
            self.opentrades = 1
        elif (bar.open_ >= lowToCheck * 1.01) and (self.opentrades < 1) and (bar.open_ > highToCheck) and (self.recentlySold >= 1):
            print("BUYING #2... highToCheck: " + str(highToCheck) + "   currentLow: " + str(self.currentLow))
            # self.curren tHigh = bar.close
            self.historicalPlaceBuyOrder(bar.open_, bar.time, ticker)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open_ < lowToCheck*0.975 or bar.open_ < highToCheck*0.95:
                self.historicalPlaceSellOrder(bar.open_, bar.time, ticker)
                self.opentrades = 0
                self.recentlySold = 1
                # self.currentLow = bar.low
                # self.currentHigh = bar.open_
        # if bar.open_ > self.currentHigh:
        #     self.currentHigh = bar.open_
        # if bar.low < self.currentLow:
        #     self.currentLow = bar.low

    def historicalPlaceBuyOrder(self, buyIn, time, ticker):
        #stock = Stock(ticker, 'SMART', 'USD')
        stock = Stock(ticker, 'SMART', 'USD')

        # raw_balance = ib.accountSummary('DU4271259')
        # for av in raw_balance:
        #     if av.tag == 'AvailableFunds':
        #         self.currentBalance = float(av.value)

        order = MarketOrder('BUY', 20)
        trade = ib.placeOrder(stock, order)
        #print(str(datetime.now()) + " -- " + str(20) + " shares of " + ticker.symbol + " bought at $")
        print("BUYING")


    def historicalPlaceSellOrder(self, sellOut, time, ticker):
        stock = Stock(ticker, 'SMART', 'USD')
        # openPositions = ib.positions()
        # shares = openPositions[0].position
        order = MarketOrder('Sell', 20)
        trade = ib.placeOrder(stock, order)
        # print(str(datetime.now()) + " -- " + str(shares) + " shares of " + ticker.symbol + " sold at $" + str(sellOut))
        print("Selling")


NioBot = NioBot()
