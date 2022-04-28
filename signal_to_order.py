import numpy as np
from create_contract import create_stk_contract
from interactive_trader import find_best_option

def place_order (signal, quantity):

def create_order(prev_signal, curr_signal, aaplQuantity, adbeQuantity, conId):
    if prev_signal == 0:
        if curr_signal == 1:
            aaplStrike, aaplExpire = find_best_option(symbol = 'AAPL', conId)
            adbeStrike, adbeExpire = find_best_option(symbol = 'ADBE', conId)
            place_order(curr_signal, aaplQuantity, adbeQuantity)

        if curr_signal == -1:
            aaplStrike, aaplExpire = find_best_option(symbol='AAPL', conId)
            adbeStrike, adbeExpire = find_best_option(symbol='ADBE', conId)
            place_order (curr_signal, aaplQuantity, adbeQuantity)

    if prev_signal == 1:
        if curr_signal == 0:
            place_order(curr_signal, aaplQuantity, adbeQuantity)

        if curr_signal == -1:
            place_order(curr_signal,aaplQuantity, adbeQuantity)
            aaplStrike, aaplExpire = find_best_option(symbol='AAPL', conId)
            adbeStrike, adbeExpire = find_best_option(symbol='ADBE', conId)
            place_order(curr_signal, aaplQuantity, adbeQuantity)

    if prev_signal == -1:
        if curr_signal == 0:
            place_order(curr_signal, aaplQuantity, adbeQuantity)

        if curr_signal == 1:
            place_order(curr_signal, aaplQuantity, adbeQuantity)
            aaplStrike, aaplExpire = find_best_option(symbol='AAPL', conId)
            adbeStrike, adbeExpire = find_best_option(symbol='ADBE', conId)
            place_order(curr_signal, aaplQuantity, adbeQuantity)
