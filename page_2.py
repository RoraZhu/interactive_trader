import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State


page_2 = html.Div(
    [
        html.P("Payoff Graph", id="test"),
        html.Div([dcc.Graph(id='surface-graph')]),
     ],
)


