import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ts_tools

pd.set_option("plotting.backend", "plotly")

COLORS = {
    "background": "#111111",
    "text": "#7FDBFF",
    "line1": "rgb(255,0,0)",
    "line2": "rgb(0,255,0)",
    "line3": "rgb(0,0,255)",
}


def plot_histograms(df, title="Raw Data", zipcode="10001", t_range=[0, None]):
    # beg == 0, end == None -> include all data
    df_plot = df.iloc[t_range[0] : t_range[1]]

    columns = df_plot.columns.tolist()

    col_idx = 0
    layout = ts_tools.get_plots_layout(columns=4, items=len(columns))

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


def plot_data(df, title="Raw Data", zipcode="10001", units={}, t_range=[0, None]):
    # t_range[0] == 0 , t_range[1] == None -> include all data
    df_plot = df.iloc[t_range[0] : t_range[1]]
    
    columns = df_plot.columns.tolist()

    col_idx = 0
    layout = ts_tools.get_plots_layout(columns=4, items=len(columns))

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
                    x=df_plot.index,
                    y=df_plot[columns[col_idx]],
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
            t=75, # 100, # 75
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
    
    fig.update_xaxes(
        matches="x",
        rangeslider_thickness=0.05
    )

    return fig


def plot_multi_line(df, title="Title", locale=[], columns=[], t_range=[0, None]):
    # t_range[0] == 0, t_range[1] == None -> include all data
    df_plot = df.iloc[t_range[0] : t_range[1]]

    colors = ["rgb(255,0,0)", "rgb(0,255,0)", "rgb(0,0,255)"]

    # labels = columns
    label_text = [label.replace("_", " ") for label in columns]

    fig = go.Figure()

    for idx, label in enumerate(columns):
        fig.add_trace(
            go.Scatter(
                name=label_text[idx],
                x=df_plot.index,
                y=df_plot[label],
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
    
    fig.update_xaxes(
        rangeslider_thickness=0.10
    )
    

    return fig
