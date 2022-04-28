"""
settings.py stores global variables.

Quantities are the current holding quantities.
    They can be used to draw payoff diagrams, or be retrieved as the previous quantities.
    Quantities are always non-negative, since place_orders() does not accept negative quantities.

isLongAAPL takes 3 values:
    0 (no holdings, no position), 1 (long AAPL, short ADBE), -1 (short AAPL, long ADBE)
    use (isLongAAPL * quantities) to get the correct quantities for drawing the payoff diagrams

How to use them in other files:
    import settings.py
    settings.strikes["AAPL"]
    settings.quantities["AAPL"]
    settings.isLongAAPL
"""

strikes = {"AAPL": 0, "ADBE": 0}
quantities = {"AAPL": 0, "ADBE": 0}
isLongAAPL = 0