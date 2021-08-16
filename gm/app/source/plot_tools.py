#!/usr/bin/env python3

import logzero
import numpy as np
import pandas as pd
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
logger.info(f"plot_tools logger initialized")


try:
    with open("config.yml", "r") as config_in:
        cfg = yaml.load(config_in, Loader=yaml.SafeLoader)
        logger.info(f"{cfg}\n")
except:
    logger.error(f"config file open failure.")
    exit(1)


def plot_forecast(train, test, test_pred, forecast, title="", zipcode="", locale=[]):

    rmse = np.sqrt(np.mean((test_pred - test) ** 2))
    logger.info(f"RMSE: {rmse}")

    data_names = ("Train", "Test", "Test Predict", "Forecast")
    data_streams = [train, test, test_pred, forecast]

    fig = go.Figure()

    for idx, data in enumerate(data_streams):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data,
                mode="lines",
                name=data_names[idx],
            )
        )

    fig.update_layout(
        title=dict(
            text=(
                f"{title} {len(forecast)}-Month Forecast<br>"
                + f"{locale[0]}, {locale[2]} {zipcode}<br>"
                + f"RMSE: {rmse:0.3f}"
            ),
            font=dict(family="Arial", size=20),
            xanchor="center",
            x=0.5,
        ),
        # title_yanchor="top",
        # title_y=0.5,
        margin=dict(l=10, r=10, b=0, t=130, pad=0),
        legend=dict(orientation="h", yanchor="top", y=1.09, x=0.60),
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=5, label="5yr", step="year", stepmode="backward"),
                        dict(count=10, label="10yr", step="year", stepmode="backward"),
                        dict(count=15, label="15yr", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                ),
                bgcolor=cfg["COLORS"]["button_background"],
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        plot_bgcolor=cfg["COLORS"]["background"],
        paper_bgcolor=cfg["COLORS"]["background"],
        font_color=cfg["COLORS"]["text"],
        autosize=True,
        height=500,
    )

    return fig


def plot_histograms(df, title="", zipcode=""):

    columns = df.columns.tolist()

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
                    x=df[columns[col_idx]],
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
        plot_bgcolor=cfg["COLORS"]["background"],
        paper_bgcolor=cfg["COLORS"]["background"],
        font_color=cfg["COLORS"]["text"],
        autosize=True,
        height=500,
    )

    return fig


def plot_trends(df, title="", zipcode="", locale=[]):

    cols = df.columns.tolist()
    layout = ts_tools.get_plots_layout(num_columns=1, num_items=len(cols))
    units_text = [value for value in cfg["data_units"].values()]

    decomps = ts_tools.get_data_decomps(df, period=12)

    fig = make_subplots(
        rows=layout["rows"],
        cols=layout["columns"],
        subplot_titles=cols,
        shared_xaxes=True,
    )

    fig.update_annotations(font_size=14)

    for idx, (feature, series) in enumerate(decomps.items()):
        fig.add_trace(
            go.Scatter(
                x=series.trend.index,
                y=series.trend,
                line=dict(width=3.5),
                connectgaps=True,
                showlegend=False,
            ),
            row=idx + 1,
            col=layout["columns"],
        )
        fig.update_yaxes(
            showgrid=True,  # False,
            gridcolor=cfg["COLORS"]["gridcolor_dark"],
            title_text=units_text[idx],
            row=idx + 1,
            col=layout["columns"],
        )

    fig.update_layout(
        title=dict(
            text=(f"{title}<br>" + f"{locale[0]}, {locale[2]} {zipcode}"),
            xanchor="center",
            x=0.5,
            font=dict(family="Arial", size=18),
        ),
        yaxis=dict(tickfont=dict(size=9)),
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=2, label="2yr", step="year", stepmode="backward"),
                        dict(count=5, label="5yr", step="year", stepmode="backward"),
                        dict(count=10, label="10yr", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                ),
                bgcolor=cfg["COLORS"]["button_background"],
                y=1.07,
            ),
        ),
        plot_bgcolor=cfg["COLORS"]["background"],
        paper_bgcolor=cfg["COLORS"]["background"],
        font_color=cfg["COLORS"]["text"],
        font=dict(size=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1),
        margin=dict(l=0, r=0, b=0, t=105, pad=0),
        autosize=True,
        height=875,
    )

    fig.update_xaxes(matches="x")  # , rangeslider_thickness=0.1)

    return fig


def plot_irradiance(df, title="Irradiance Data", zipcode="", irr_columns=[], locale=[]):

    logger.info(f"plot_data irradiance columns: {irr_columns}")

    layout = ts_tools.get_plots_layout(num_columns=2, num_items=len(irr_columns))

    fig = make_subplots(
        rows=layout["rows"],
        cols=layout["columns"],
        subplot_titles=irr_columns,
        shared_xaxes=False,
    )

    col_idx = 0
    for _, row in enumerate(range(1, layout["rows"] + 1)):
        for _, col in enumerate(range(1, layout["columns"] + 1)):
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[irr_columns[col_idx]],
                    name=irr_columns[col_idx],
                    line=dict(width=1.5),
                    connectgaps=True,
                    showlegend=False,
                ),
                row=row,
                col=col,
            )
            fig.update_xaxes(
                rangeslider=dict(visible=False),
            )
            col_idx += 1

    fig.update_layout(
        title=dict(
            text=f"{title}, {locale[0]}, {locale[2]}, {zipcode}",
            xanchor="center",
            x=0.5,
            font=dict(
                family="Arial",
                size=16,
            ),
        ),
        font=dict(
            size=12,
        ),
        margin=dict(
            l=5,
            r=5,
            b=0,
            t=75,
            pad=10,
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
            rangeslider=dict(visible=False),
            type="date",
        ),
        plot_bgcolor=cfg["COLORS"]["background"],
        paper_bgcolor=cfg["COLORS"]["background"],
        font_color=cfg["COLORS"]["text"],
        autosize=True,
        height=500,
    )

    fig.update_xaxes(matches="x")

    return fig


def plot_multi_line(df, title="Title", locale=[], columns=[]):

    colors = (("red", 0.75), ("yellow", 0.75), ("green", 0.80), ("blue", 0.90))

    label_text = [label.replace("_", " ") for label in columns]

    fig = go.Figure()

    for idx, label in enumerate(columns):
        fig.add_trace(
            go.Scatter(
                name=label_text[idx],
                x=df.index,
                y=df[label],
                mode="lines",
                line=dict(color=colors[idx][0], width=2),
                opacity=colors[idx][1],
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
            y=1.1,
            x=0.30,
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
        plot_bgcolor=cfg["COLORS"]["background"],
        paper_bgcolor=cfg["COLORS"]["background"],
        font_color=cfg["COLORS"]["text"],
        autosize=True,
        height=400,
    )

    fig.update_xaxes(rangeslider_thickness=0.10)

    return fig
