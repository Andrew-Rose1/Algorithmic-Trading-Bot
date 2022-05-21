# Algorithmic Trading Bot

This piece of software uses the Interactive Brokers API to test market trading strategies against historical and live data. This project includes both a backtesting and live version.

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for testing purposes. This software should be used soley for testing.

You will need to setup your IB account to your TWS client and ensure you correctly define your port within the python code. IB has plenty of Getting Started documentation how to setup the client for automated trading.

Below is the code snippet where you define your port. In this example, port 7947 was used.

    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=2)
  
The Results folder includes some sample backtesting results.

There are additional resources at the end of this README

### Prerequisites

Requirements for the software and other tools to build, test and push 
- An Interactive Brokers (IB) Account that is funded with at least $500. Accounts that are not funded cannot access real-time market data or utilize historical market data.
- Trader Workstation (TWS) - IB Trading Platform
- Python3

### Installing

Ensure you have python and pip installed. Then, proceed to install the following dependancies

* ib_insync

    ```sh
    pip install ib_insync
    ```

* numpy

    ```sh
    pip install numpy
    ```
    
* nest_asyncio

    ```sh
    pip install nest_asyncio
    ```
    
* pandas

    ```sh
    pip install pandas
    ```
    
* matplotlib

    ```sh
    pip install matplotlib
    ```

## Running the tests

After dependenices are installed and you have connected to your TWS client, you are almost ready to run the bot.
First you will need to define your "Contract" which is essentially the ticker you wish to trade.
A "Contract" object looks like this (used in backtesting.py):

    contract = Contract()
    contract.symbol = "SPY"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.primaryExchange = "NASDAQ"
    
We use a different class to define a contract in liveBot.py:

    stock = Stock("SPY", 'SMART', 'USD')
    
You can now run either liveBot.py or backtesting.py just as you would any other python file, with no additional arguemnts.

### Backtesting Bot

When using historical data to backtest, a csv file will be created with the name "trades.csv". I have included some sample data in the Results folder.

### Live Bot

When using the live bot you will simply see market orders executed in TWS when the bot executes trades.

## Contact

**Andrew Rose** - [LinkedIn](https://www.linkedin.com/in/andrewrose7/) - andrew.rose115@gmail.com
    
Project Link: https://github.com/Andrew-Rose1/Algorithmic-Trading-Bot/

## Acknowledgments

  - [Interactive Brokers API](https://www.interactivebrokers.com/en/trading/ib-api.php)
  - [ib_insync Documentation](https://pypi.org/project/ib-insync/)
  - [Pandas Documentation](https://pandas.pydata.org/docs/)
