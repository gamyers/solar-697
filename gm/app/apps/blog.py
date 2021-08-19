#!/usr/bin/env python3

# import sqlite3
# import sys

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import logzero

# import plotly.graph_objects as go
from app import app
# from dash.dependencies import Input, Output
# from dash_table import DataTable
# from logzero import logger

# --------------------------begin layout--------------------------#
layout_blog = html.Div(
    dbc.Row(
        dbc.Col(
            html.Div(
                html.Iframe(
                    src="/assets/blog.htm",
                    style={
                        "height": "200em",
                        "width": "100%",
                        "backgroundColor": "lightgrey",
                        "padding-left": "2%",
                        "padding-right": "2%",
                        "border-style": "none",
                    },
                ),
                style={
                    "width": "100%",
                    "display": "block",                    
                },
            ),
            width={"size": 10, "offset": 1},
        ),
    ),
)
