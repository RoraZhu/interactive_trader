from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# df = px.data.iris()
#
# fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
#                  title="Using The add_trace() method With A Plotly Express Figure")
#
# fig.add_trace(
#     go.Scatter(
#         x=[2, 4],
#         y=[4, 8],
#         mode="lines",
#         line=go.scatter.Line(color="gray"),
#         showlegend=False)
# )
# fig.show()


page_1 = html.Div(
    [html.P("This is the content of parameter setting!"),
    html.Div(["OLS period:",
        dcc.Slider(0, 20000, 1000, value=1000,id = 'ols-period')
    ]),
     html.Div(["vol period:",
               dcc.Slider(0, 1000, 50, value=100,id = 'vol-period')
               ]),
     html.Div(["entry threshold absolute:",
               dcc.Slider(0, 3, 0.1, value=1, id='entry-thres')
               ]),
     html.Div(["exit threshold absolute:",
               dcc.Slider(0, 3, 0.1, value=0.5, id='exit-thres')
               ]),
     html.Div(["AAPL quantity:",
               dcc.Slider(10, 30, 1, value=20, id='con-quantity')
               ]),
     dcc.Interval(id='interval1', interval=60 * 1000, n_intervals=0),
     html.H1(id='label1', children=''),

     html.Div([
        html.Button('Update Parameters', id='show-secret'),
        html.Br(),
        html.Div(id='body-div'),
        html.Br(),
     ]),
    dcc.Graph(id ='vol-graph'),
    html.Div(dash_table.DataTable(id="trade-signal"),
             style = {'width': '800px',})


     ],

)

