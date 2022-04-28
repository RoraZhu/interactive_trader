import pandas as pd
import numpy as np
from find_best_option import find_best_option
from create_contract import create_opt_contract
from create_order import create_order
from interactive_trader.synchronous_functions import place_order


def place(isLongAAPL, aaplQuantity, aaplExpiration, aaplStrike, adbeQuantity, adbeExpiration, adbeStrike):
    aaplCallContract = create_opt_contract("AAPL", aaplExpiration, aaplStrike, "C")
    aaplPutContract = create_opt_contract("AAPL", aaplExpiration, aaplStrike, "P")
    adbeCallContract = create_opt_contract("ADBE", adbeExpiration, adbeStrike, "C")
    adbePutContract = create_opt_contract("ADBE", adbeExpiration, adbeStrike, "P")
    if isLongAAPL:
        buyOrder = create_order("BUY", aaplQuantity)
        sellOrder = create_order("SELL", adbeQuantity)
        place_order(adbeCallContract, sellOrder)
        place_order(adbePutContract, sellOrder)
        place_order(aaplCallContract, buyOrder)
        place_order(aaplPutContract, buyOrder)
    else:
        buyOrder = create_order("BUY", adbeQuantity)
        sellOrder = create_order("SELL", aaplQuantity)
        place_order(aaplCallContract, sellOrder)
        place_order(aaplPutContract, sellOrder)
        place_order(adbeCallContract, buyOrder)
        place_order(adbePutContract, buyOrder)


def place_orders(prevSignal, currSignal, AAPLCurrQuantity, ADBECurrQuantity,
                  AAPLPrevQuantity, ADBEPrevQuantity, conIds):
    AAPLStrike, AAPLExpire = find_best_option("AAPL", conIds["AAPL"])
    ADBEStrike, ADBEExpire = find_best_option("ADBE", conIds["ADBE"])
    if prevSignal != currSignal:
        if prevSignal == 0 and currSignal == 1:
            place(1, AAPLCurrQuantity, AAPLExpire, AAPLStrike, ADBECurrQuantity, ADBEExpire, ADBEStrike)

        elif prevSignal == 0 and currSignal == -1:
            place(0, AAPLCurrQuantity, AAPLExpire, AAPLStrike, ADBECurrQuantity, ADBEExpire, ADBEStrike)

        elif prevSignal == 1 and currSignal == 0:
            place(0, AAPLPrevQuantity, AAPLExpire, AAPLStrike, ADBEPrevQuantity, ADBEExpire, ADBEStrike)

        elif prevSignal == 1 and currSignal == -1:
            place(0, AAPLPrevQuantity, AAPLExpire, AAPLStrike, ADBEPrevQuantity, ADBEExpire, ADBEStrike)
            place(0, AAPLCurrQuantity, AAPLExpire, AAPLStrike, ADBECurrQuantity, ADBEExpire, ADBEStrike)

        elif prevSignal == -1 and currSignal == 1:
            place(1, AAPLPrevQuantity, AAPLExpire, AAPLStrike, ADBEPrevQuantity, ADBEExpire, ADBEStrike)
            place(1, AAPLCurrQuantity, AAPLExpire, AAPLStrike, ADBECurrQuantity, ADBEExpire, ADBEStrike)

        else:
            place(1, AAPLPrevQuantity, AAPLExpire, AAPLStrike, ADBEPrevQuantity, ADBEExpire, ADBEStrike)