from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
from ibapi.order import *
from threading import Timer
import random

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def tickPrice(self, reqId, tickType, price, attrib):
        print("Tick Price. Ticker Id:", reqId, "tickType:", TickTypeEnum.to_str(tickType), "Price:", price, end=' ')
        print("")

    def tickSize(self, reqId, tickType, size):
        print("Tick Size. Ticker Id:", reqId, "tickType:", TickTypeEnum.to_str(tickType), "size:", size)
        print("")

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        bot.on_bar_update(reqId, time, open, high, low, close, volume, wap, count)
class Bot:
    def __init__(self):
        self.rand = random.randrange(0,500)
        self.app=TestApp()
        self.app.connect("127.0.0.1", 7497,rand)
        app_thread = threading.Thread(target=self.run_loop, daemon=True)
        app_thread.start()
        time.sleep(1)

        contract = Contract()
        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = "NASDAQ"

        self.app.reqRealTimeBars(0, ontract, 5, "TRADES", 1, [])

        # self.app.reqMarketDataType(3) # switch to delayed-frozen data if live not available
        # app.reqMktData(1, contract, "", False, False, [])


    def run_loop(self):
        self.app.run()

    def on_bar_update(self, reqId, time, open, high, low, close, volume, wap, count):
        print(reqId)





bot = Bot()
