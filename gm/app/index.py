import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app import app
from apps import app1, app2
from dash.dependencies import Input, Output
from dash_table import DataTable


app.layout = html.Div(
    [
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("EDA")),
        ]),
        dcc.Location(id="url", refresh=True), # False
        html.Div(id="page-content"),
    ],
)


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/": # "/apps/app1":
        return app1.layout_1
    elif pathname == "/apps/app2":
        return app2.layout
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(
        host="192.168.64.164",
        port="8088",
        use_reloader=False,
        debug=True,
    )
