from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

page_1 = html.Div(
    [html.P("This is the content of parameter setting!"),
    html.Div(["OLS period:",
        dcc.Slider(0, 20000, 1000, value=10000,id = 'ols-period')
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

     html.Div([
        html.Button('Update Parameters', id='show-secret'),
        html.Div(id='body-div')
     ])

     ],

)
