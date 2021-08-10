from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from threading import Timer
import random

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId:int):
        self.nextOrderId = orderId
        print(orderId)
        self.start()

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    # def contractDetails(self, reqId, contractDetails):
    #     print("contractDetails: ", reqId, " ", contractDetails)

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permID, parentID, lastFillPrice, clientID, whyHeld, mktCapPrice):
        print("Order status.  ID: ", orderId, ", Status: ", status, ", Filled: ", filled, ", Remaining: ", remaining, ", Last FIll Price : ", lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print("OpenOrder. ID: ", orderId, contract.symbol, contract.secType, "@", contract.exchange, ":", order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print("ExecDetails: ",reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

    def start(self):
        contract = Contract()
        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = "NASDAQ"

        order = Order()
        order.action = "BUY"
        order.totalQuantity = 10
        order.orderType = "MKT"
        #order.lmtPrice = 147

        self.reqContractDetails(1, contract)
        print("Placing order?")
        self.placeOrder(self.nextOrderId, contract, order)
        # print(self.nextValidID())
        # print(order.status)


    def stop(self):
        self.done = True
        self.disconnect()

def main():
    print("Here")
    rand = random.randrange(0,500)
    print("Random number is: ", rand)
    app=TestApp()
    app.connect("127.0.0.1", 7497,rand)
    app.nextOrderId = 0
    app.run()



# if __name__ == "__main__":
main()
