import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_data(df, title="Raw Data", zipcode="10001", columns=[], units=[], t_range=[0, None]):
    # beg == 0, end == None -> include all data
    beg = t_range[0]  # math.ceil(len(df_rs)*.90)
    end = t_range[1]  # math.ceil(len(df_rs) * 0.075)
    df_plot = df.iloc[beg:end]

    col_idx = 0

    if len(columns) % 2:
        rows = int((len(columns) + 1) / 2)
        cols = 2
    else:
        rows = int(len(columns) / 2)
        cols = 2

    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=columns,
    )

    for _, row in enumerate(range(1, rows + 1)):
        for _, col in enumerate(range(1, cols + 1)):
            fig.add_trace(
                go.Scatter(
                    x=df_plot.index,
                    y=df_plot[columns[col_idx]],
                    name=columns[col_idx],
                    showlegend=False,
                ),
                row=row,
                col=col,
            )

            fig.update_yaxes(
                title_text=units[col_idx],
                row=row,
                col=col,
            )

            fig.update_xaxes(title_text="Year/Month")

            col_idx += 1

    fig.update_layout(
        title=dict(
            text=f"{title}, Zip Code: {zipcode}",
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
    )

    return fig


def plot_multi_line(df, title="Title", t_range=[0, None], columns=[]):
    # beg == 0, end == None -> include all data
    beg = t_range[0]  # math.ceil(len(df_rs)*.90)
    end = t_range[1]  # math.ceil(len(df_rs) * 0.075)
    df_plot = df.iloc[beg:end]

    colors = ["rgb(255,0,0)", "rgb(0,255,0)", "rgb(0,0,255)"]

    labels = columns
    label_text = [label.replace("_", " ") for label in labels]
    # {label_text[0]}, {label_text[1]}, {label_text[2]}

    fig = go.Figure()

    for idx, label in enumerate(labels):
        fig.add_trace(
            go.Scatter(
                name=label_text[idx],
                x=df_plot.index,
                y=df_plot[label],
                mode="lines",
                line=dict(color=colors[idx], width=2),
                connectgaps=True,
            )
        )

    fig.update_layout(
        title=dict(
            text=f"{title}",
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
            l=5,
            r=5,
            b=0,
            t=75,
            pad=0,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            x=0.0,
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
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
#             margin=dict(
#                 l=0,
#                 r=0,
#                 b=0,
#                 t=100,
#                 pad=0,
#             ),
        ),
    )

    return fig
