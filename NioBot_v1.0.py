from ib_insync import *
from datetime import datetime
import numpy as np

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=6)

class NioBot:
    def __init__(self):
        self.now = datetime.now()
        self.dayStart = self.now.replace(hour=6, minute=30, second=0)
        print(self.now)
        print(self.dayStart)
        print(self.now - self.dayStart)
        self.currntHigh = 0

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




        #for i in symbols:
            #print(i)
            #stock = Stock('FLGC', 'SMART', 'USD')
        #self.catchUp(stock)
        #self.scannerTest()

        for i in symbols:
            print(i)
            stock = Stock(i, 'SMART', 'USD')
            self.catchUp(stock)
            #market_data = ib.reqMktData(stock, '', False, False)
            #ib.pendingTickersEvent += self.onPendingTicker
        ib.run()


    def onPendingTicker(self, ticker):
        print("pending ticker event recieved")
        # print(ticker)
        print(type(ticker))
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
        self.bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='60 S',
            barSizeSetting='1 secs',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1,
            keepUpToDate=True)
        self.bars.updateEvent += self.onBarUpdate
        #print(len(self.bars))

    def onBarUpdate(self, bar):
        print("pending bar event recieved")
        self.NioStrategy2_bar(bar)
        print(bar)

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
        stock = Stock(ticker, 'SMART', 'USD')

        raw_balance = ib.accountSummary('DU4271259')
        for av in raw_balance:
            if av.tag == 'AvailableFunds':
                self.currentBalance = float(av.value)

        order = MarketOrder('BUY', mathfloor(15000/buyIn))
        trade = ib.placeOrde(stock, order)
        print(str(datetime.now()) + " -- " + str(shares) + " shares of " + ticker.symbol + " bought at $" + str(sellOut))


    def historicalPlaceSellOrder(self, ticker, sellOut):
        stock = Stock(ticker, 'SMART', 'USD')
        openPositions = ib.positions()
        shares = openPositions[0].position
        order = MarketOrder('Sell', shares)
        trade = ib.placeOrde(stock, order)
        print(str(datetime.now()) + " -- " + str(shares) + " shares of " + ticker.symbol + " sold at $" + str(sellOut))


NioBot = NioBot()
