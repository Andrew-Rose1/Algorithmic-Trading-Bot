from ib_insync import *
from datetime import datetime, time, timedelta
#import datetime
import numpy as np
import time
import math
import nest_asyncio
from functools import partial

"""
This program will run and execute live trades on a paper account.
Still a work in progress...
"""

nest_asyncio.apply()
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

class NioBot:
    def __init__(self):
        self.now = datetime.now()
        self.dayStart = self.now.replace(hour=6, minute=30, second=0)
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

        tillMorning = (self.now-self.dayStart).total_seconds()
        newMorn = str(math.floor(tillMorning)) + " S"

        for i in symbols:
            stock = Stock(i, 'SMART', 'USD')
            bars = ib.reqRealTimeBars(stock, 1, 'TRADES', False)
            bars.updateEvent += self.onBarUpdate
        time.sleep(1)
        ib.run()



    def onBarUpdate(self, bar, hasNewBar):
        self.now = datetime.now()
        tillMorning = (self.now-self.dayStart).total_seconds()
        newMorn = str(math.floor(tillMorning)) + " S"
        total = []
        bars2hoursBack = ib.reqHistoricalData(
            bar.contract,
            endDateTime='',
            durationStr=newMorn,
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1)
        for i in bars2hoursBack:
            total.append(i.high)
        self.highToCheck = max(total[:-2])
        self.lowToCheck = max(total[-60:-2])
        total.clear()

        # Only trade after 5 mins
        # Define trading strategy here
        if len(bars2hoursBack > 4):
            self.backTesting_Strategy_v4(bar[-1], self.highToCheck, self.lowToCheck, bar.contract.symbol)

    

    def liveBuyOrder(self, buyIn, time, ticker):
        stock = Stock(ticker, 'SMART', 'USD')
        order = MarketOrder('BUY', 20)
        trade = ib.placeOrder(stock, order)

    def liveSellOrder(self, sellOut, time, ticker):
        stock = Stock(ticker, 'SMART', 'USD')
        order = MarketOrder('Sell', 20)
        trade = ib.placeOrder(stock, order)




    ######################################
    # Define backTesting Strategies Here #
    ######################################

    # Simple dip buy strategy, waits to buy after a rise off of new low (Small Cap)
    def backTesting_Strategy_v1(self, bar):
        if (bar.open_ <= self.currentHigh - 0.02) and (self.opentrades < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            self.liveBuyOrder(bar.open_, bar.time)
            self.opentrades = 1
        elif (bar.open_ >= self.currentLow * 1.02) and (self.opentrades < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            self.liveBuyOrder(bar.open_, bar.time)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open_ <= self.currentHigh * 0.95:
                self.currentLow = bar.low
                self.recentlySold = 1
                self.liveSellOrder(bar.open_, bar.time)
                self.opentrades = 0
        if bar.high > self.currentHigh:
            self.currentHigh = bar.high
        if bar.low < self.currentLow:
            self.currentLow = bar.low


    def backTesting_Strategy_v2(self, tick):
        eod = tick.time.replace(hour=12, minute=50)
        if (tick.last <= self.currentHigh * 0.97) and (len(ib.positions()) < 1) and (self.recentlySold < 1):
            self.currentHigh = tick.last
            self.liveBuyOrder(tick.last, tick.time)
        elif (tick.last >= self.currentLow * 1.015) and (len(ib.positions()) < 1) and (self.recentlySold >= 1):
            self.currentHigh = tick.last
            self.liveBuyOrder(tick.last, tick.time)
        elif len(ib.positions()) >= 1:
            if tick.last <= self.currentHigh * 0.955:
                self.currentLow = tick.last
                self.recentlySold = 1
                self.liveSellOrder(tick.last, tick.time)
            elif tick.time >= eod:
                self.liveSellOrder(tick.last, tick.time)
                self.currentLow = tick.last
        if tick.last > self.currentHigh:
            self.currentHigh = tick.last
        if tick.last < self.currentLow:
            self.currentLow = tick.last


    def backTesting_Strategy_v3(self, bar):
        eod = bar.date.replace(hour=12, minute=50)
        if (bar.open <= self.currentHigh * 0.97) and (len(ib.positions()) < 1) and (self.recentlySold < 1):
            self.currentHigh = bar.close
            self.liveBuyOrder(bar.open, bar.date)
            self.opentrades = 1
        elif (bar.open >= self.currentLow * 1.015) and (len(ib.positions()) < 1) and (self.recentlySold >= 1):
            self.currentHigh = bar.close
            self.liveBuyOrder(bar.open, bar.date)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.close <= self.currentHigh * 0.955:
                self.currentLow = bar.low
                self.recentlySold = 1
                self.liveSellOrder(bar.open, bar.date)
                self.opentrades = 0
            elif bar.date >= eod:
                self.liveSellOrder(bar.open, bar.date)
                self.opentrades = 0
                self.currentLow = bar.low
        if bar.close > self.currentHigh:
            self.currentHigh = bar.close
        if bar.low < self.currentLow:
            self.currentLow = bar.low


    def backTesting_Strategy_v4(self, bar, highToCheck, lowToCheck, ticker):
        if (bar.open_ > highToCheck) and (self.opentrades < 1) and self.recentlySold < 1:
            self.liveBuyOrder(bar.open_, bar.time, ticker)
            self.opentrades = 1
        elif (bar.open_ >= lowToCheck * 1.01) and (self.opentrades < 1) and (bar.open_ > highToCheck) and (self.recentlySold >= 1):
            self.liveBuyOrder(bar.open_, bar.time, ticker)
            self.opentrades = 1
        elif self.opentrades >= 1:
            if bar.open_ < lowToCheck*0.975 or bar.open_ < highToCheck*0.95:
                self.liveSellOrder(bar.open_, bar.time, ticker)
                self.opentrades = 0
                self.recentlySold = 1
        

    


NioBot = NioBot()
