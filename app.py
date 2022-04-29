import dash
import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from threading import Timer
from place_orders import *
from create_contract import create_stk_contract
from page_2 import page_2
from page_1 import page_1
from order_page import order_page
from error_page import error_page
from navbar import navbar
from sidebar import sidebar, SIDEBAR_HIDDEN, SIDEBAR_STYLE
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from interactive_trader import *
from datetime import datetime
from ibapi.contract import Contract
from ibapi.order import Order
import time
import threading
import pandas as pd
from strategySignal import market_signal, trade_quantity
from pull_data import pull_data
import settings
import find_best_option

CONTENT_STYLE = {
    "transition": "margin-left .5s",
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE1 = {
    "transition": "margin-left .5s",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

order_status = ""
errors = ""
connected = ""
ibkr_async_conn = ibkr_app()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
app.layout = html.Div(
    [
        dcc.Store(id='side_click'),
        dcc.Location(id="url"),
        navbar,
        sidebar,
        html.Div(id="page-content", style=CONTENT_STYLE),
        dcc.Interval(
            id='ibkr-update-interval',
            interval=5000,
            n_intervals=0
        )
    ],
)


@app.callback(
    [Output('trade-blotter', 'data'), Output('trade-blotter', 'columns')],
    Input('ibkr-update-interval', 'n_intervals')
)
def update_order_status(n_intervals):
    global ibkr_async_conn
    global order_status

    order_status = ibkr_async_conn.order_status

    df = order_status
    dt_data = df.to_dict('records')
    dt_columns = [{"name": i, "id": i} for i in df.columns]
    return dt_data, dt_columns


@app.callback(
    [Output('errors-dt', 'data'), Output('errors-dt', 'columns')],
    Input('ibkr-update-interval', 'n_intervals')
)
def update_order_status(n_intervals):
    global ibkr_async_conn
    global errors

    errors = ibkr_async_conn.error_messages

    df = errors
    dt_data = df.to_dict('records')
    dt_columns = [{"name": i, "id": i} for i in df.columns]
    return dt_data, dt_columns

@app.callback(
    [
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
    ],

    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDDEN
            content_style = CONTENT_STYLE1
            cur_nclick = "HIDDEN"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick

# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/home-screen"]:
        return page_1
    elif pathname == "/blotter":
        return order_page
    elif pathname == "/errors":
        return error_page
    elif pathname == "/graph":
        return page_2
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

@app.callback(
    Output('ibkr-async-conn-status', 'children'),
    [
        Input('ibkr-async-conn-status', 'children'),
        Input('master-client-id', 'value'),
        Input('port', 'value'),
        Input('hostname', 'value')
    ]
)
def async_handler(async_status, master_client_id, port, hostname):

    if async_status == "CONNECTED":
        raise PreventUpdate
        pass

    global ibkr_async_conn
    ibkr_async_conn.connect(hostname, port, master_client_id)

    timeout_sec = 5

    start_time = datetime.now()
    # while not ibkr_async_conn.isConnected():
    #     time.sleep(0.01)
    #     if (datetime.now() - start_time).seconds > timeout_sec:
    #         ibkr_async_conn.disconnect()
    #         raise Exception(
    #             "set_up_async_connection",
    #             "timeout",
    #             "couldn't connect to IBKR"
    #         )

    def run_loop():
        ibkr_async_conn.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while ibkr_async_conn.next_valid_id is None:
        time.sleep(0.01)

    global order_status
    order_status = ibkr_async_conn.order_status

    global errors
    errors = ibkr_async_conn.error_messages

    global connected
    connected = ibkr_async_conn.isConnected()

    ibkr_async_conn.disconnect()

    return "Connection is " + str(connected)


@app.callback(
    [Output('body-div', 'children'),Output('trade-signal', 'data'),Output('label1', 'children'),Output('vol-graph','figure')],
    [Input('show-secret', 'n_clicks'),Input('interval1', 'n_intervals')],
    State('ols-period', 'value'), State('vol-period', 'value'),
    State('entry-thres', 'value'), State('exit-thres', 'value'),
    State('con-quantity','value')
)
def update_output(n_clicks,n_intervals, ols_period, vol_period, entry_thres, exit_thres, con_quantity):
    symbols = ["AAPL", "ADBE"]
    pull_data(symbols)
    # data = pd.read_csv("sampledata.csv", parse_dates=['date']).set_index('date')
    AAPL = pd.read_csv("./data/AAPL.csv", parse_dates=['date'])[['date','close']]
    AAPL.rename(columns={'close': 'AAPL'}, inplace=True)
    ADBE = pd.read_csv("./data/ADBE.csv", parse_dates=['date'])[['date','close']]
    ADBE.rename(columns={'close': 'ADBE'}, inplace=True)
    data = AAPL.merge(ADBE, on="date").set_index('date')

    signal, hedge_ratio = market_signal(data, vol_period, ols_period, entry_thres, exit_thres)
    # print(signal)
    quantity_pair = trade_quantity(hedge_ratio, con_quantity)
    now = datetime.now().strftime("%H:%M:%S")
    fig = make_subplots(rows=1, cols=2)
    fig.add_trace(go.Scatter(x=signal['date'], y=signal['vol_AAPL'], name='vol_AAPL'), row=1, col=1)
    fig.add_trace(go.Scatter(x=signal['date'], y=signal['vol_ADBE'], name='vol_ADBE'), row=1, col=1)
    fig.add_trace(go.Scatter(x=signal['date'], y=signal['zscore'], name='zscore'), row=1, col=2)

    if n_clicks==None:
        return "Please click to start runing strategy",signal.to_dict('records'),"",fig

    local_settings = pd.read_csv("./data/settings.csv").set_index('index')

    addGlobal(local_settings.loc['isLongAAPL','AAPL'], local_settings.loc['quantities','AAPL'],
              local_settings.loc['quantities','ADBE'], local_settings.loc['strikes','AAPL'], local_settings.loc['strikes','ADBE'])

    print("settings_local:",local_settings)
##################place order######################################################
    conIds = {"AAPL": 265598, "ADBE": 265768}
    strategy_signal = (settings.isLongAAPL, int(signal['signal'].iloc[0]))
    print("signal:",strategy_signal)

    AAPLPrevQuantity = settings.quantities["AAPL"]
    ADBEPrevQuantity = settings.quantities["ADBE"]
    AAPLCurrQuantity = quantity_pair[0]
    ADBECurrQuantity = quantity_pair[1]


    prevSignal, currSignal = strategy_signal
    if prevSignal!=currSignal:
        place_orders(prevSignal, currSignal, AAPLCurrQuantity, ADBECurrQuantity,
                     AAPLPrevQuantity, ADBEPrevQuantity, conIds)

    if settings.isLongAAPL!=0:
        info = f"The trading signal is {strategy_signal}. We hold {settings.isLongAAPL * settings.quantities['AAPL']} AAPL straddle(s) at ${settings.strikes['AAPL']}\n" \
               f"{-settings.isLongAAPL * settings.quantities['ADBE']} ADBE straddle(s) at ${settings.strikes['ADBE']}"
    else:
        info = f"The trading signal is {strategy_signal}. We don't plan to hold any positions."

    return info, signal.to_dict('records'),'Last Strategy Update: ' + str(now),fig

#
# @app.callback(dash.dependencies.Output('label1', 'children'),
#     [dash.dependencies.Input('interval1', 'n_intervals')])
# def update_interval(n):
#     now = datetime.now().strftime("%H:%M:%S")
#     return 'last calculate: ' + str(now)

@app.callback([Output("surface-graph", "figure"), Output('test', 'children')],
              [Input('graph-link', "n_clicks")])
def update_graph(n_clicks):
    apple_strike = settings.strikes['AAPL']
    adobe_strike = settings.strikes['ADBE']
    apple_quantity = settings.quantities["AAPL"] * settings.isLongAAPL
    adobe_quantity = settings.quantities['ADBE'] * settings.isLongAAPL
    x_start = apple_strike * 0.75
    x_end = apple_strike * 1.25
    y_start = adobe_strike * 0.75
    y_end = adobe_strike * 1.25
    step_x = max((x_end - x_start) / 100, 0.0001)
    step_y = max((y_end - y_start) / 100, 0.0001)

    x_data = np.arange(x_start, x_end, step_x)
    y_data = np.arange(y_start, y_end, step_y)
    z_data = []
    for i in range(x_data.size):
        x_profit = (max(0, x_data[i] - apple_strike) + max(0, apple_strike - x_data[i])) * apple_quantity
        data = []
        for j in range(y_data.size):
            y_profit = (max(0, y_data[j] - adobe_strike) + max(0, adobe_strike - y_data[j])) * adobe_quantity
            data.append(x_profit + y_profit)
        z_data.append(data)

    fig = go.Figure(data=[go.Surface(z=np.array(z_data), x=x_data, y=y_data)])
    # print("z", len(z_data))
    #print(z_data)
    # print("x", x_data.size)
    # print(x_data)
    # print("y", y_data.size)
    # print(y_data)
    fig.update_scenes(xaxis_title={'text': 'AAPL Price'})
    fig.update_scenes(yaxis_title={'text': 'ADBE Price'})
    fig.update_scenes(zaxis_title={'text': 'Payoff'})
    x_price = find_best_option._find_underlying("AAPL")
    y_price = find_best_option._find_underlying("ADBE")
    z_value = (max(0, x_price - apple_strike) + max(0, apple_strike - x_price)) * apple_quantity + \
              (max(0, y_price - adobe_strike) + max(0, adobe_strike - y_price)) * adobe_quantity
    fig.add_trace(go.Scatter3d(x=[x_price], y=[y_price], z=[z_value], name='Current Position'))
    fig.update_layout(title='Payoff Graph', autosize=True)

    # z_data = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv')
    # z = z_data.values
    # sh_0, sh_1 = z.shape
    # x, y = np.linspace(0, 1, sh_0), np.linspace(0, 1, sh_1)
    # fig = go.Figure(data=[go.Surface(z=z, x=x, y=y)])
    # fig.update_layout(title='Mt Bruno Elevation', autosize=False,
    #                   width=500, height=500,
    #                   margin=dict(l=65, r=50, b=65, t=90))

    return fig, ''

if __name__ == "__main__":
    app.run_server(debug=True)