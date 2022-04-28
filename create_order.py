import pandas as pd
import numpy as np
from ibapi.order import Order


def create_order(action,  quantity, orderType="MKT"):
    order = Order()
    order.action = action
    order.orderType = orderType
    order.totalQuantity = quantity
    return order