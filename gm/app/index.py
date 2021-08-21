#!/usr/bin/env python3

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import logzero
from app import app
from apps import app1, app2, app3, blog
from dash.dependencies import Input, Output
from dash_table import DataTable
from logzero import logger

# Connect to logzero log file
log_path = "logs/"
log_file = "dashboard_app.log"

logzero.logfile(
    log_path + log_file,
    maxBytes=1e5,
    backupCount=1,
    disableStderrLogger=True,
)
logger.info(f"{log_path}, {log_file}\n")


navbar_style = {
    # "top": 35,
    # "position": "fixed",    
}

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=True),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5(
                            "Solar Irradiance Data Explorer",
                            style={
                                "color": "gold",
                            },
                        ),
                        html.Hr(style={"borderColor": "gold", "borderWidth": 3}),
                        html.Br(),
                        dbc.Nav(
                            [
                                html.Br(),
                                html.Br(),
                                dbc.NavLink(
                                    "EDA",
                                    href="/apps/app1",
                                    active="exact",
                                ),
                                dbc.NavLink(
                                    "Data Trends",
                                    href="/apps/app2",
                                    active="exact",
                                ),
                                dbc.NavLink(
                                    "Forecasting",
                                    href="/apps/app3",
                                    active="exact",
                                ),
#                                 dbc.NavLink(
#                                     "Blog",
#                                     href="/apps/blog",
#                                     active="exact",
#                                 ),                                
                            ],
                            vertical=True,
                            pills=True,
                            style=navbar_style,
                        ),
                    ],
                    width=1,
                ),
                dbc.Col(
                    [
                        html.Div(
                            id="page-content",
                            children=[],
                        ),
                    ],
                    width=11,
                ),
            ]
        ),
    ],
)


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/":
        return app1.layout_app1
    elif pathname == "/apps/app1":
        return app1.layout_app1
    elif pathname == "/apps/app2":
        return app2.layout_app2
    elif pathname == "/apps/app3":
        return app3.layout_app3
#     elif pathname == "/apps/blog":
#         return blog.layout_blog
    else:
        return dbc.Jumbotron(
            [
                html.H1("404: Content not found"),
                html.Hr(),
                html.P(f"path -> {pathname} not available"),
            ]
        )


if __name__ == "__main__":
    app.run_server(
        host="192.168.64.164",
        port="8088",
        use_reloader=True,  # False, #
        debug=True,  # False, #
    )
