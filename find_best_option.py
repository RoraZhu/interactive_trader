import numpy as np
from create_contract import create_stk_contract
from datetime import datetime
from interactive_trader import fetch_option_chain, fetch_historical_data, fetch_current_time

"""
find_best_option.py is used to find the closest strike and 
the smallest expiration date that exceeds the following 22 trading days
from the option chain.

The main function to be used: 
find_best_option(symbol: str, conId: Int) -> best_strike: Float, best_expire: str

eg.
find_best_option("AAPL", 265598)
find_best_option("ADBE", 265768)
"""


def _find_underlying(symbol, durationStr="30 S", barSize="15 secs", field="close"):
    contract = create_stk_contract(symbol)
    data = fetch_historical_data(contract=contract, durationStr=durationStr, barSizeSetting=barSize)
    result = data[field].iloc[-1]
    return result


def _find_option_chain(symbol, conId, exchange="CBOE", secType="STK"):
    option_chain = fetch_option_chain(symbol, secType, conId)
    option_chain = option_chain[option_chain["exchange"] == exchange].reset_index(drop=True)
    strikes = np.array(list(option_chain["strikes"][0]))
    expirations = np.array(list(option_chain["expirations"][0]))
    return strikes, expirations


def _find_best_strike(underlying, strikes):
    diff = abs(underlying - strikes)
    return strikes[np.where(diff == min(diff))][0]


def _find_expiration(expirations, lower=22, upper=90):
    current_time = fetch_current_time()
    expire_times = [datetime.strptime(expire_time, "%Y%m%d") for expire_time in expirations]
    expire_times = list(filter(lambda expire_time: lower < (expire_time - current_time).days < upper, expire_times))
    expire_times.sort()
    return expire_times[0].strftime("%Y%m%d")


def find_best_option(symbol, conId):
    underlying = _find_underlying(symbol)
    strikes, expirations = _find_option_chain(symbol, conId)
    best_strike = _find_best_strike(underlying, np.array(strikes))
    best_expire = _find_expiration(np.array(expirations))
    return best_strike, best_expire


if __name__ == "__main__":
    conIds = {"AAPL": 265598, "ADBE": 265768}
    for symbol in conIds:
        best_strike, best_expire = find_best_option(symbol, conIds[symbol])
