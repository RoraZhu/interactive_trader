import numpy as np
import pandas as pd
import time
import statsmodels.api as sm
import warnings
import statistics
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',10)
from datetime import *
warnings.filterwarnings('ignore')



def realized_vol(period, data):
    vol = np.log(data/data.shift(1))**2
    vol = np.sqrt(vol.rolling(window = period).mean()*390*252)
    vol = vol.dropna()
    return vol

## Find the leverage ratio
## (Y, X)
## Y = a * X + b + residue
def OLS(vol, pair):
    Y = np.array(vol[pair[0]].dropna())
    X = np.array(vol[pair[1]].dropna())
    X_ = sm.add_constant(X)
    model = sm.OLS(Y, X_) #model OLS
    results = model.fit()
    print(f'The model is fitted with {round(results.rsquared,4)} R2, {results.pvalues} p values.')
    return results

def leverage_ratio(vol, pair):
    results = OLS(vol, pair)
    a = results.params[1]
    return a

def cal_residue_zscore(vol, pair):
    results = OLS(vol, pair)
    Y = np.array(vol[pair[0]].dropna())
    X = np.array(vol[pair[1]].dropna())
    a = results.params[1]
    b = results.params[0]
    residue = Y - a*X - b
    residue = (residue-np.mean(residue))/residue.std()
    return residue


def market_signal(data, vol_period, ols_period, z_entry_threshold, z_exit_threshold):
    '''
    params:
    pairs: DataFrame with columns [stock1, stock2]'
    z_entry_threshold: open position absolute threshold
    z_exit_threshold: close position absolute threshold

    '''
    data = data.copy().iloc[-(vol_period+ols_period):]
    pair = (data.columns[0], data.columns[1])

    data["vol_"+pair[0]] = realized_vol(vol_period, data[pair[0]])
    data["vol_"+pair[1]] = realized_vol(vol_period, data[pair[1]])

    data = data.iloc[vol_period:]
    data['zscore'] = cal_residue_zscore(data, ("vol_"+pair[0],"vol_"+pair[1]))

    data['longs'] = (data['zscore'] <= -z_entry_threshold) * 1.0
    data['shorts'] = (data['zscore'] >= z_entry_threshold) * 1.0
    data['exits'] = (np.abs(data['zscore']) <= z_exit_threshold) * 1.0

    data['long_market'] = 0.0
    data['short_market'] = 0.0


    def signal_process(x):
        arr = x[-1]

        if len(x) == 1:
            # initial long_market
            arr[3] = arr[0]
            # initial short_market
            arr[4] = arr[1]
            return arr
        else:
            long = arr[0]
            short = arr[1]
            exit = arr[2]
            long_market = x[-2][3]
            short_market = x[-2][4]

            # update long_market signal
            arr[3] = (long or long_market) and not exit

            # update short_market signal
            arr[4] = (short or short_market) and not exit
            return arr

    data[['longs', 'shorts', 'exits', 'long_market', 'short_market']] \
        = data[['longs', 'shorts', 'exits', 'long_market', 'short_market']].rolling(2, method="table",
                                                                                     min_periods=1).apply(
        signal_process, raw=True, engine="numba")


    vol_pair = ("vol_" + pair[0], "vol_" + pair[1])
    # data[pair[0]+'- a*'+pair[1]] = leverage_ratio(data, vol_pair)

    data.reset_index(inplace=True)
    data = data.round(4)

    signal_output = data[["date",pair[0],pair[1],vol_pair[0],vol_pair[1],'zscore']].copy()
    signal_output['signal'] = data['long_market']-data['short_market']
    op1 = "long "+pair[0]+" vol, short "+ pair[1]+" vol"
    op2 = "long " + pair[1] + " vol, short " + pair[0] + " vol"
    signal_output['operation'] = signal_output['signal'].apply(lambda x: op1 if x == 1.0 else (op2 if x == -1.0 else ""))
    # signal_output['operation']
    # data.rename(columns={'AAPL': 'aapl_close', 'ADBE': 'adbe_close'}, inplace=True)
    today = signal_output['date'].iloc[-1].date()
    signal_output = signal_output[signal_output['date'] >= pd.Timestamp(today)].iloc[::-1]
    print(today)
    return signal_output

if __name__ == '__main__':
    data = pd.read_csv("sampledata.csv",parse_dates=['date']).set_index('date')

    # parmas
    pair = ('AAPL', 'ADBE')
    ols_period = 1000
    vol_period = 100
    z_entry_threshold = 1.0
    z_exit_threshold = 0.5
    signal = market_signal(data, vol_period, ols_period, z_entry_threshold, z_exit_threshold)

