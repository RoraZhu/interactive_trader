import pandas as pd
import numpy as np
from threading import Timer
from create_contract import create_stk_contract
from interactive_trader.synchronous_functions import fetch_historical_data


"""
pull_data.py is used to pull historical data and automatically update minute level data to the csv files.
The csv files are always updated and can be used directly in the OLS functions. 

main function to be used:
pull_data(symbols: listOfStr, interval: Int, historicalDuration: Str, newDuration: Str, barSize: Str)
Symbols is the list of symbol.
Interval represents the frequency in seconds to update data.
historicalDuration is the durationStr used to pull historical data.
newDuration is the durationStr used to pull updated data.
barSize is the frequency of data.

eg.
pull_data(["AAPL", "ADBE"])
pull_data(["AAPL", "ADBE"], interval=120, historicalDuration="30000 S",
              newDuration="240 S", barSize="1 min")
"""


def pull_historical(symbols, durationStr, barSize):
    for symbol in symbols:
        contract = create_stk_contract(symbol)
        data = fetch_historical_data(contract=contract, durationStr=durationStr, barSizeSetting=barSize)
        data.to_csv("./data/" + symbol + ".csv", index=False)


def pull_new(symbols, interval, durationStr, barSize):
    for symbol in symbols:
        original = pd.read_csv("./data/" + symbol + ".csv")

        contract = create_stk_contract(symbol)
        new = fetch_historical_data(contract=contract, durationStr=durationStr, barSizeSetting=barSize)

        # delete the oldest original, add the newest new
        index = np.where(new["date"] == original["date"].iloc[-1])[0][0]
        shift = len(new) - (index + 1)
        original = pd.concat([original.iloc[shift:, :], new.iloc[(index+1):, :]])

        original.to_csv("./data/" + symbol + ".csv", index=False)
        print(symbol + " updated")
    loop = Timer(interval, pull_new, [symbols, interval, durationStr, barSize])
    loop.start()


def pull_data(symbols, interval=120, historicalDuration="30000 S",
              newDuration="120 S", barSize="1 min"):
    pull_historical(symbols, historicalDuration, barSize)
    timer = Timer(0.01, pull_new, [symbols, interval, newDuration, barSize])
    timer.start()


if __name__ == "__main__":
    symbols = ["AAPL", "ADBE"]
    pull_data(symbols)