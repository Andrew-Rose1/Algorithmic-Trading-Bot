from ib_insync import *
import datetime

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

# tickerList = ["TSLA", "AAPL", "AMZN", "MSFT", ]

file = open('stocks.txt', 'r')
tickerList = file.readlines()
file.close()
#
# test = "AAPL\\n"
# print(test)
# test.split('\\')
# print(test)

# for i in tickerList:
#     print(i)
now = datetime.datetime.now()
print(now)

newNow = now.replace(hour=6, minute=00)
print (newNow)



# 1) Create contract objects for each ticker. Append to contractList
# for ticker in tickerList:
#     contract = (ticker, 'SMART', 'USD')
#     contractList += contract


# 2) Grab realtime market data for each ticker
# def onPendingTickers(ticker):
#     print("pending ticker event recieved")
#     print(ticker)
#
# for stock in contractList:
#     ib.reqMktData(s, '', False, False)
#     ib.pendingTickersEvent += onPendingTicker


# 3) Grab historical data from makret open until now
# For example, if needing the last week's high value,
#   grab historical data 7 days back and save the highest value. Use that to compare
# dt = ''
# barsList = []
# while True:
#     bars = ib.reqHistoricalData(
#         contract,
#         endDateTime=dt,
#         # 252 trading days a year
#         durationStr='14 D',
#         barSizeSetting='1 day',
#         whatToShow='TRADES',
#         useRTH=True,
#         formatDate=1)
#     if not bars:
#         break
#     barsList.append(bars)
#     dt = bars[0].date
#     print(dt)

# 4) Loop through current strategies

# ib.run()




# BACKTESTING TO BE DONE
# cash = $100,000
# startDate = 01012015
# endDate = 12312020
# get historical data from SPY and run strategies
# keep track of SPY shares
cash = 50000
shares = 0
openTrades = 0
trade = []
def historicalPlaceBuyOrder(buyIn, time):
    tempShares = round.floor(cash/buyIn)
    shares = tempShares
    cash -= tempShares * buyIn
    trades += str(time) + ": " + str(amount) + " shares of SPY bought at " + str(buyIn)
    #hardStopLoss = buyIn * 0.93

def historicalPlaceSellOrder(sellOut, time):
    cash += shares * sellOut
    shares = 0
    trades += str(time) + ": " + str(amount) + " shares of SPY sold at " + str(sellOut)

# def backTestingStrategy2(bar):
#     if (bar.Open > sma50) && openTrades < 1:
#         currentHigh = bar.High
#         historicalPlaceBuyOrder(bar.Open, bar.Time)
#     elif openTrades >= 1:
#         if bar.Open < currentHigh * 0.97:
#             historicalPlaceSellOrder(bar.Open, bar.Time)
#             openTrades = 0

def backTestingStrategy1(bar):
    if (bar.Close <= currentHigh * 0.98) and (openTrades < 1):
        currentHigh = bar.High
        historicalPlaceBuyOrder(bar.Close, bar.Time)
    elif openTrades >= 1:
        if bar.Close <= currentHigh * 0.97:
            historicalPlaceSellOrder(bar.Open, bar.Time)
            openTrades = 0
    if bar.close > currentHigh:
        currentHigh = bar.Close


contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.exchange = "SMART"
contract.currency = "USD"
contract.primaryExchange = "NASDAQ"

dt = ''
barsList = []
while True:
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=dt,
        # 252 trading days a year
        durationStr='1 D',
        barSizeSetting='5 mins',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1)
    if not bars:
        break
    barsList.append(bars)
    dt = bars[0].date
    print(dt)
print("Bars size: " + str(len(bars)))
currentHigh = bars[0].high
for b in bars:
    backTestingStrategy1(b)
if shares > 0:
    cash += shares * bars[len(bars)-1].Close

print("==== END STATS AFTER 504 TRADING DAYS ====")
print("Ending Cash: $" + cash)
print("Number of trades made: " + str(len(trades)))
print("Trades:")
for i in trades:
    print (i)


################# 50 MA ####################
#
#     def sma50(ticker) --> returns 50ma int
#
# dt = ''
# maBarsList = []
# maBars = ib.reqHistoricalData(
#     contract,
#     endDateTime=dt,
#     # 252 trading days a year
#     durationStr='50 D',
#     barSizeSetting='1 day',
#     whatToShow='TRADES',
#     useRTH=True,
#     formatDate=1)
# ######maBarsList.append(maBars)
# ######dt = maBars[0].date
# ######print(dt)
# total = 0
# for b in range (0, len(maBars)):
#     total += b[i].Close
# sma = total / 50




# STRATEGY IDEAS
#
# grab historical data from x 50 days back and calculate 50SMA
#   if current price below 50ma, and breaks above ---> buy
#   if current price above 50ma, and bounce off -----> buy
#
#   if fall below 2.5% of buy in ----> sell
#   keep track of new high from here on out
#       if fall 1.75% below this high ----> sell
