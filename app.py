import dash
import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

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
from strategySignal import market_signal

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
adobe_strike = 0
apple_strike = 0
apple_quantity = 0
adobe_quantity = 0
ibkr_async_conn = ibkr_app()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

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
    while not ibkr_async_conn.isConnected():
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            ibkr_async_conn.disconnect()
            raise Exception(
                "set_up_async_connection",
                "timeout",
                "couldn't connect to IBKR"
            )

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

    return "Connection is " + str(connected)

@app.callback(
    Output('placeholder-div', 'children'),
    [
        Input('trade-button', 'n_clicks'),
        # Input('contract-symbol', 'value'),
        # Input('contract-sec-type', 'value'),
        # Input('contract-currency', 'value'),
        # Input('contract-exchange', 'value'),
        # Input('contract-primary-exchange', 'value'),
        # Input('order-action', 'value'),
        # Input('order-type', 'value'),
        # Input('order-size', 'value'),
        # Input('order-lmt-price', 'value'),
        # Input('order-account', 'value')
    ],
    prevent_initial_call = True
)


def place_order(n_clicks):
                # contract_symbol, contract_sec_type,
                # contract_currency, contract_exchange,
                # contract_primary_exchange, order_action, order_type,
                # order_size, order_lmt_price, order_account):

    # Contract object: STOCK
    # contract = Contract()
    # contract.symbol = contract_symbol
    # contract.secType = contract_sec_type
    # contract.currency = contract_currency
    # contract.exchange = contract_exchange
    # contract.primaryExchange = contract_primary_exchange

    # Contract object: Option
    AAPL_call_contract = Contract()
    AAPL_call_contract.symbol = "AAPL"
    AAPL_call_contract.secType = "OPT"
    AAPL_call_contract.exchange = "CBOE"
    AAPL_call_contract.currency = "USD"
    AAPL_call_contract.lastTradeDateOrContractMonth = "20220429"
    AAPL_call_contract.strike = "160"
    AAPL_call_contract.right = "C"
    AAPL_call_contract.multiplier = "100"

    AAPL_put_contract = Contract()
    AAPL_put_contract.symbol = "AAPL"
    AAPL_put_contract.secType = "OPT"
    AAPL_put_contract.exchange = "CBOE"
    AAPL_put_contract.currency = "USD"
    AAPL_put_contract.lastTradeDateOrContractMonth = "20220429"
    AAPL_put_contract.strike = "160"
    AAPL_put_contract.right = "P"
    AAPL_put_contract.multiplier = "100"

    ADBE_call_contract = Contract()
    ADBE_call_contract.symbol = "ADBE"
    ADBE_call_contract.secType = "OPT"
    ADBE_call_contract.exchange = "CBOE"
    ADBE_call_contract.currency = "USD"
    ADBE_call_contract.lastTradeDateOrContractMonth = "20220429"
    ADBE_call_contract.strike = "405"
    ADBE_call_contract.right = "C"
    ADBE_call_contract.multiplier = "100"

    ADBE_put_contract = Contract()
    ADBE_put_contract.symbol = "ADBE"
    ADBE_put_contract.secType = "OPT"
    ADBE_put_contract.exchange = "CBOE"
    ADBE_put_contract.currency = "USD"
    ADBE_put_contract.lastTradeDateOrContractMonth = "20220429"
    ADBE_put_contract.strike = "405"
    ADBE_put_contract.right = "P"
    ADBE_put_contract.multiplier = "100"

    # Example LIMIT Order
    # order = Order()
    # order.action = order_action
    # order.orderType = order_type
    # order.totalQuantity = order_size
    #
    # if order_type == 'LMT':
    #     order.lmtPrice = order_lmt_price
    #
    # if order_account:
    #     order.account = order_account

    buy_order = Order()
    buy_order.action = "BUY"
    buy_order.orderType = "MKT"
    buy_order.totalQuantity = 100

    sell_order = Order()
    sell_order.action = "SELL"
    sell_order.orderType = "MKT"
    sell_order.totalQuantity = 100

    ibkr_async_conn.reqIds(1)

    # Place orders!
    # ibkr_async_conn.placeOrder(
    #     ibkr_async_conn.next_valid_id,
    #     contract,
    #     order
    # )

    ibkr_async_conn.placeOrder(ibkr_async_conn.next_valid_id, AAPL_call_contract, buy_order)
    ibkr_async_conn.placeOrder(ibkr_async_conn.next_valid_id, AAPL_put_contract, buy_order)
    ibkr_async_conn.placeOrder(ibkr_async_conn.next_valid_id, ADBE_call_contract, sell_order)
    ibkr_async_conn.placeOrder(ibkr_async_conn.next_valid_id, ADBE_put_contract, sell_order)

    return ''


@app.callback(
    [Output('body-div', 'children'),Output('trade-signal', 'data')],
    Input('show-secret', 'n_clicks'),
    State('ols-period', 'value'), State('vol-period', 'value'),
    State('entry-thres', 'value'), State('exit-thres', 'value'),
)
def update_output(n_clicks, ols_period, vol_period, entry_thres, exit_thres):
    data = pd.read_csv("sampledata.csv", parse_dates=['date']).set_index('date')
    signal = market_signal(data, vol_period, ols_period, entry_thres, exit_thres)


    return f"{ols_period},{vol_period},{entry_thres},{exit_thres}", signal.to_dict('records')

@app.callback([Output("surface-graph", "figure"), Output('test', 'children')],
              [Input('graph-link', "n_clicks")])
def update_graph(n_clicks):
    global apple_strike
    global apple_quantity
    global adobe_strike
    global adobe_quantity
    apple_strike = 100
    adobe_strike = 200
    apple_quantity = 5
    adobe_quantity = -2
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
    print("z", len(z_data))
    #print(z_data)
    print("x", x_data.size)
    # print(x_data)
    print("y", y_data.size)
    # print(y_data)
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