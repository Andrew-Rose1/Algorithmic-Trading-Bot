from ib_insync import *
from datetime import datetime
import numpy as np
import time
import math

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



        #
        # for i in symbols:
        #     print(i)
        #     stock = Stock(i, 'SMART', 'USD')
        #     market_data = ib.reqMktData(stock, '', False, False)
        #     time.sleep(2)
        #     ib.pendingTickersEvent += self.onPendingTicker
        #self.catchUp(stock)
        #self.scannerTest()

        # for i in symbols:
        #     print(i)
        stock = Stock('AAPL', 'SMART', 'USD')
        self.catchUp(stock)
            #time.sleep(2)
            #market_data = ib.reqMktData(stock, '', False, False)
            #ib.pendingTickersEvent += self.onPendingTicker
        ib.run()


    def onPendingTicker(self, ticker):
        print("pending ticker event recieved")
        print(ticker)
        #print(type(ticker))
        # d = {i: (c.contract.symbol, c.close) for (i, c) in enumerate(tickers)}
        # ib.loopUntil(any(np.isnan(val) for val in d.values()), len(tickers))
        #self.NioStrategy2(ticker)

    def scannerTest(self):
        sub = ScannerSubscription(
            instrument='STK',
            locationCode='STK.US.MAJOR',
            scanCode='TOP_PERC_GAIN')

        tagValues = [
            TagValue("changePercAbove", "20"),
            TagValue('priceAbove', 1),
            TagValue('priceBelow', 50),
            TagValue('volumeAbove', 200000)]

        # the tagValues are given as 3rd argument; the 2nd argument must always be an empty list
        # (IB has not documented the 2nd argument and it's not clear what it does)
        scanData = ib.reqScannerData(sub, [], tagValues)

        symbols = [sd.contractDetails.contract.symbol for sd in scanData]
        print(symbols)

    def catchUp(self, contract):
        total = []
        # bars1 = ib.reqHistoricalData(
        #     contract,
        #     endDateTime='',
        #     durationStr='60 S',
        #     barSizeSetting='1 secs',
        #     whatToShow='TRADES',
        #     useRTH=True,
        #     formatDate=1,
        #     keepUpToDate=True)
        #     #time.sleep(2)
        # for i in bars1:
        #     total.append(i.high)
        # self.currentHOD = max(total)
        # self.currentLOD = min(total)
        # total.clear()
        # self.currentHigh = self.currentHOD
        # self.currentLow = self.currentLOD
        bars = ib.reqRealTimeBars(contract, 1, 'MIDPOINT', False)
        bars.updateEvent += self.onBarUpdate
        #print(len(self.bars))

    def onBarUpdate(self, bar, hasNewBar):
        print("pending bar event recieved")
        print("open: " + str(bar[-1].open_))
        self.backTestingStrategy1_v3(bar[-1])
        #print(bar[-1].close)

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

    def historicalPlaceBuyOrder(self, buyIn, time):
        #stock = Stock(ticker, 'SMART', 'USD')
        stock = Stock('AAPL', 'SMART', 'USD')

        # raw_balance = ib.accountSummary('DU4271259')
        # for av in raw_balance:
        #     if av.tag == 'AvailableFunds':
        #         self.currentBalance = float(av.value)

        order = MarketOrder('BUY', 20)
        trade = ib.placeOrder(stock, order)
        print(str(datetime.now()) + " -- " + str(20) + " shares of " + ticker.symbol + " bought at $")
        print("BUYING")


    def historicalPlaceSellOrder(self, ticker, sellOut):
        # stock = Stock(ticker, 'SMART', 'USD')
        # openPositions = ib.positions()
        # shares = openPositions[0].position
        # order = MarketOrder('Sell', shares)
        # trade = ib.placeOrde(stock, order)
        # print(str(datetime.now()) + " -- " + str(shares) + " shares of " + ticker.symbol + " sold at $" + str(sellOut))
        print("Selling")


NioBot = NioBot()
