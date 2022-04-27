import pandas as pd
import numpy as np
from ibapi.contract import Contract


"""
create_contract.py is used to create a stock contract or an option contract

The main functions to be used: 
find_stk_contract(symbol: str) -> contract: Contract
find_opt_contract(symbol: str, expiration: str, strike: float, right: str) -> contract: Contract

eg. 
find_opt_contract("AAPL", "20220517", 170, "C")
"""


def create_stk_contract(symbol):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "STK"
    contract.currency = "USD"
    contract.exchange = "SMART"
    return contract


def create_opt_contract(symbol, expiration, strike, right):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "OPT"
    contract.exchange = "CBOE"
    contract.currency = "USD"
    contract.lastTradeDateOrContractMonth = expiration
    contract.strike = strike
    contract.right = right
    contract.multiplier = "100"
    return contract