import pandas as pd
import plotly.graph_objects as go


def plot_multi_line(df, title="Title", range=[0, None], columns=[]):
    # begin == 0, end == None -> include all data
    begin = range[0]  # math.ceil(len(df_rs)*.90)
    end = range[1]  # math.ceil(len(df_rs) * 0.075)
    df_plot = df.iloc[begin:end]

    colors = ["rgb(255,0,0)", "rgb(0,255,0)", "rgb(0,0,255)"]

    labels = columns
    label_text = [label.replace("_", " ") for label in labels]

    fig = go.Figure()

    for idx, label in enumerate(labels):
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot[label],
                mode="lines",
                name=labels[idx],
                line=dict(color=colors[idx], width=2),
                connectgaps=True,
            )
        )

    fig.update_layout(
        title=dict(
            text=f"{title}",  # : {label_text[0]}, {label_text[1]}, {label_text[2]}
            xanchor="center",
            x=0.5,
            font=dict(
                family="Arial",
                size=20,
            ),
        ),
        autosize=True,
        height=500,
        margin=dict(
            l=10,
            r=10,
            b=0,
            t=100,
            pad=0,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.08,
            # x=0.70,
        ),
    )

    return fig
