import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app import app


# --------------------------begin layout--------------------------#
layout_blog = html.Div(
    dbc.Row(
        dbc.Col(
            html.Div(
                html.Iframe(
                    src="/assets/blog.htm",
                    style={
                        "height": "800em",
                        "width": "75%",
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
