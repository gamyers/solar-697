#!/usr/bin/env python3

import logzero
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import ts_tools
import yaml
from logzero import logger
from plotly.subplots import make_subplots

# Connect to logzero log file
log_path = "logs/"
log_file = "dashboard_app.log"
logzero.logfile(
    log_path + log_file,
    maxBytes=1e5,
    backupCount=1,
    disableStderrLogger=True,
)
logger.info(f"pmd_plot_tools logger initialized")

configs = None
try:
    with open("../configs/config.yml", "r") as config_in:
        configs = yaml.load(config_in, Loader=yaml.SafeLoader)
        logger.info(f"{configs}\n")
except:
    logger.error(f"config file open failure.")
    exit(1)

def plot_forecast(train, test, forecast, title="Title", zipcode="01001"):
    
    colors = (("blue", 0.5), ("orange", 0.9), ("green", 0.75))
    
    # actual = test
    rmse = np.sqrt(np.mean((forecast - test) ** 2))
    logger.info(f"RMSE: {rmse}")

    data_names = ("Train", "Actual", "Forecast")
    data_streams = [train, test, forecast]

    fig = go.Figure()
    
    for idx, data in enumerate(data_streams):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data,
                opacity=colors[idx][1],
                mode="lines",
                name=data_names[idx],
                line=dict(color=colors[idx][0], width=2),
                connectgaps=True,
            )
        )

    fig.update_layout(
        title=dict(
            text=(f"{title} {len(forecast)}-Month Forecast<br>Zip Code {zipcode}<br>RMSE: {rmse:0.3f}"),
            xanchor="center",
            x=0.5,
            font=dict(
                family="Arial",
                size=20,
            ),
        ),
        autosize=True,
        height=600,
        margin=dict(
            l=10,
            r=10,
            b=0,
            t=130,
            pad=0,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.08,
            x=0.70,
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=5, label="5yr", step="year", stepmode="backward"),
                        dict(count=10, label="10yr", step="year", stepmode="backward"),
                        dict(count=15, label="15yr", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
    )

    return fig


def plot_histograms(df, title="Raw Data", zipcode="10001", t_range=[0, None]):
    # beg == 0, end == None -> include all data
    df_plot = df.iloc[t_range[0] : t_range[1]]

    columns = df_plot.columns.tolist()

    col_idx = 0
    layout = ts_tools.get_plots_layout(num_columns=4, num_items=len(columns))

    fig = make_subplots(
        rows=layout["rows"],
        cols=layout["columns"],
        subplot_titles=columns,
        shared_yaxes=True,
    )

    for _, row in enumerate(range(1, layout["rows"] + 1)):
        for _, col in enumerate(range(1, layout["columns"] + 1)):
            fig.add_trace(
                go.Histogram(
                    x=df_plot[columns[col_idx]],
                    name=columns[col_idx],
                    showlegend=False,
                ),
                row=row,
                col=col,
            )

            fig.update_yaxes(
                title_text="Count",
                row=row,
                col=col,
            )

            col_idx += 1

    fig.update_layout(
        title=dict(
            text=f"Feature Histograms",
            xanchor="center",
            x=0.5,
            font=dict(
                family="Arial",
                size=18,
            ),
        ),
        margin=dict(
            l=5,
            r=5,
            b=0,
            t=75,
            pad=0,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
        ),
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        font_color=COLORS["text"],
        autosize=True,
        height=500,
    )

    return fig


def plot_trends(df, title="Data", zipcode="01001", units={}):

    idx = 0
    cols = df.columns.tolist()
    units_text = [value for value in units.values()]
    layout = ts_tools.get_plots_layout(num_columns=1, num_items=len(cols))

    decomps = ts_tools.get_data_decomps(df, period=12)

    fig = make_subplots(
        rows=layout["rows"],
        cols=layout["columns"],
        subplot_titles=cols,
        shared_xaxes=False,
    )

    for feature, series in decomps.items():
        fig.add_trace(
            go.Scatter(
                x=series.trend.index,
                y=series.trend,
                name=feature,
                line=dict(width=4),
                connectgaps=True,
                showlegend=False,
            ),
            row=idx + 1,
            col=layout["columns"],
        )
        fig.update_yaxes(
            showgrid=True,  # False,
            gridcolor=COLORS["gridcolor_dark"],
            title_text=units_text[idx],
            row=idx + 1,
            col=layout["columns"],
        )
        idx += 1

    fig.update_layout(
        title=dict(
            text=f"{title}, Zip Code: {zipcode}",
            xanchor="center",
            x=0.5,
            font=dict(family="Arial", size=18),
        ),
        height=875,
        autosize=True,
        margin=dict(l=0, r=0, b=0, t=75, pad=25),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1),
        # yaxis=dict(title=dict(standoff=0)),
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        # dict(count=1, label="1yr", step="year", stepmode="backward"),
                        # dict(count=2, label="2yr", step="year", stepmode="backward"),
                        dict(count=5, label="5yr", step="year", stepmode="backward"),
                        dict(count=10, label="10yr", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                ),
                bgcolor=COLORS["button_background"],
                y=1.07,
            ),
            rangeslider=dict(visible=False),
            type="date",
        ),
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        font_color=COLORS["text"],
    )

    fig.update_xaxes(matches="x")  # , rangeslider_thickness=0.1)

    return fig


def plot_data(df, title="Raw Data", zipcode="10001", units={}):

    columns = df.columns.tolist()

    col_idx = 0
    layout = ts_tools.get_plots_layout(num_columns=4, num_items=len(columns))

    fig = make_subplots(
        rows=layout["rows"],
        cols=layout["columns"],
        subplot_titles=columns,
        shared_xaxes=False,
    )

    units_text = [value for value in units.values()]

    for _, row in enumerate(range(1, layout["rows"] + 1)):
        for _, col in enumerate(range(1, layout["columns"] + 1)):
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[columns[col_idx]],
                    name=columns[col_idx],
                    line=dict(width=1.5),
                    connectgaps=True,
                    showlegend=False,
                ),
                row=row,
                col=col,
            )

            fig.update_yaxes(
                title_text=units_text[col_idx],
                row=row,
                col=col,
            )
            col_idx += 1

    fig.update_layout(
        title=dict(
            text=f"{title}, Zip Code: {zipcode}",
            xanchor="center",
            x=0.5,
            font=dict(
                family="Arial",
                size=18,
            ),
        ),
        margin=dict(
            l=5,
            r=5,
            b=0,
            t=75,  # 100, # 75
            pad=0,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
        ),
        yaxis=dict(
            title=dict(
                standoff=0,
            )
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1yr", step="year", stepmode="backward"),
                        dict(count=2, label="2yr", step="year", stepmode="backward"),
                        dict(count=5, label="5yr", step="year", stepmode="backward"),
                        dict(count=10, label="10yr", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                ),
                bgcolor="#444444",
                y=1.07,
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        font_color=COLORS["text"],
        autosize=True,
        height=500,
    )

    fig.update_xaxes(matches="x", rangeslider_thickness=0.05)

    return fig


def plot_multi_line(df, title="Title", locale=[], columns=[]):

    colors = ["rgb(255,0,0)", "rgb(0,255,0)", "rgb(0,0,255)"]

    # labels = columns
    label_text = [label.replace("_", " ") for label in columns]

    fig = go.Figure()

    for idx, label in enumerate(columns):
        fig.add_trace(
            go.Scatter(
                name=label_text[idx],
                x=df.index,
                y=df[label],
                mode="lines",
                line=dict(color=colors[idx], width=2),
                connectgaps=True,
                showlegend=True,
            )
        )

    fig.update_layout(
        title=dict(
            text=f"{title} for {locale[0]}, {locale[2]}",
            xanchor="center",
            x=0.5,
            font=dict(
                family="Arial",
                size=18,
            ),
        ),
        margin=dict(
            l=5,
            r=5,
            b=0,
            t=75,
            pad=0,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",  # "bottom",
            y=1.2,
            x=0.375,
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1yr", step="year", stepmode="backward"),
                        dict(count=2, label="2yr", step="year", stepmode="backward"),
                        dict(count=5, label="5yr", step="year", stepmode="backward"),
                        dict(count=10, label="10yr", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                ),
                bgcolor="#444444",
                y=1.07,
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        font_color=COLORS["text"],
        autosize=True,
        height=300,
    )

    fig.update_xaxes(rangeslider_thickness=0.10)

    return fig
