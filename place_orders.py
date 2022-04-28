import settings
from find_best_option import find_best_option
from create_contract import create_opt_contract
from create_order import create_order
from interactive_trader.synchronous_functions import place_order

"""
place_orders.py handles order placement.

main function to call:
    place_orders(prevSignal, currSignal, AAPLCurrQuantity, ADBECurrQuantity,
                  AAPLPrevQuantity, ADBEPrevQuantity, conIds)
                  
        prevSignal and currSignal have three possible values: -1, 0, 1.
        AAPLCurrQuantity, ADBECurrQuantity come from the strategy output.
        AAPLPrevQuantity, ADBEPrevQuantity come from the settings.py. They are updated automatically. 
            One needn't update settings.py by assigning it the currQuantity 
            since this is automatically done by place_orders.
        conIds is fixed to be conIds = {"AAPL": 265598, "ADBE": 265768}

for concrete usage, see if __name__ == "__main__"
"""


def addGlobal(isLongAAPL, AAPLQuantity, ADBEQuantity, AAPLStrike, ADBEStrike):
    settings.strikes["AAPL"] = AAPLStrike
    settings.strikes["ADBE"] = ADBEStrike
    settings.quantities["AAPL"] = AAPLQuantity
    settings.quantities["ADBE"] = ADBEQuantity
    settings.isLongAAPL = isLongAAPL if isLongAAPL == 1 else -1
    if AAPLQuantity == 0 and ADBEQuantity == 0:
        settings.isLongAAPL = 0


def place(isLongAAPL, AAPLQuantity, AAPLExpiration, AAPLStrike, ADBEQuantity, ADBEExpiration, ADBEStrike):
    AAPLCallContract = create_opt_contract("AAPL", AAPLExpiration, AAPLStrike, "C")
    AAPLPutContract = create_opt_contract("AAPL", AAPLExpiration, AAPLStrike, "P")
    ADBECallContract = create_opt_contract("ADBE", ADBEExpiration, ADBEStrike, "C")
    ADBEPutContract = create_opt_contract("ADBE", ADBEExpiration, ADBEStrike, "P")
    if isLongAAPL:
        buyOrder = create_order("BUY", AAPLQuantity)
        sellOrder = create_order("SELL", ADBEQuantity)
        place_order(ADBECallContract, sellOrder)
        place_order(ADBEPutContract, sellOrder)
        place_order(AAPLCallContract, buyOrder)
        place_order(AAPLPutContract, buyOrder)
    else:
        buyOrder = create_order("BUY", ADBEQuantity)
        sellOrder = create_order("SELL", AAPLQuantity)
        place_order(AAPLCallContract, sellOrder)
        place_order(AAPLPutContract, sellOrder)
        place_order(ADBECallContract, buyOrder)
        place_order(ADBEPutContract, buyOrder)


def place_orders(prevSignal, currSignal, AAPLCurrQuantity, ADBECurrQuantity,
                  AAPLPrevQuantity, ADBEPrevQuantity, conIds: dict):
    AAPLStrike, AAPLExpire = find_best_option("AAPL", conIds["AAPL"])
    ADBEStrike, ADBEExpire = find_best_option("ADBE", conIds["ADBE"])
    if prevSignal != currSignal:
        if prevSignal == 1:
            # two cases: prev = 1 & curr = 0, prev = 1 & curr = -1
            place(0, AAPLPrevQuantity, AAPLExpire, AAPLStrike, ADBEPrevQuantity, ADBEExpire, ADBEStrike)
            addGlobal(0, 0, 0, 0, 0)
            if currSignal == -1:
                place(0, AAPLCurrQuantity, AAPLExpire, AAPLStrike, ADBECurrQuantity, ADBEExpire, ADBEStrike)
                addGlobal(0, AAPLCurrQuantity, ADBECurrQuantity, AAPLStrike, ADBEStrike)
        elif prevSignal == -1:
            # two cases: prev = -1 & curr = 0, prev = -1 & curr = 1
            place(1, AAPLPrevQuantity, AAPLExpire, AAPLStrike, ADBEPrevQuantity, ADBEExpire, ADBEStrike)
            addGlobal(1, 0, 0, 0, 0)
            if currSignal == 1:
                place(1, AAPLCurrQuantity, AAPLExpire, AAPLStrike, ADBECurrQuantity, ADBEExpire, ADBEStrike)
                addGlobal(1, AAPLCurrQuantity, ADBECurrQuantity, AAPLStrike, ADBEStrike)
        else:
            if currSignal == 1:
                # prev = 0 & curr = 1
                place(1, AAPLCurrQuantity, AAPLExpire, AAPLStrike, ADBECurrQuantity, ADBEExpire, ADBEStrike)
                addGlobal(1, AAPLCurrQuantity, ADBECurrQuantity, AAPLStrike, ADBEStrike)
            else:
                # prev = 0 & curr = -1
                place(0, AAPLCurrQuantity, AAPLExpire, AAPLStrike, ADBECurrQuantity, ADBEExpire, ADBEStrike)
                addGlobal(0, AAPLCurrQuantity, ADBECurrQuantity, AAPLStrike, ADBEStrike)
        print("Orders placed")


if __name__ == "__main__":
    conIds = {"AAPL": 265598, "ADBE": 265768}
    signals = [(0, 0), (0, 1), (1, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (-1, 0)]
    AAPLPrevQuantity = settings.quantities["AAPL"]
    ADBEPrevQuantity = settings.quantities["ADBE"]
    AAPLCurrQuantity = 1
    ADBECurrQuantity = 1
    for signal in signals:
        prevSignal, currSignal = signal
        place_orders(prevSignal, currSignal, AAPLCurrQuantity, ADBECurrQuantity,
                     AAPLPrevQuantity, ADBEPrevQuantity, conIds)
        AAPLPrevQuantity = settings.quantities["AAPL"]
        ADBEPrevQuantity = settings.quantities["ADBE"]