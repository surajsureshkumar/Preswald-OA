from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import numpy as np
import base64


# Load the CSV
connect()

df = get_df("cleanedData3.csv")

with open("dotamap3_25.jpg", "rb") as f:
    encoded_image = "data:image/jpg;base64," + base64.b64encode(f.read()).decode()

column_prefix = np.array(["r1", "r2", "r3", "r4","r5", "d1","d2","d3","d4","d5"], dtype=str)
column_suffix = np.array(["gold","lh","denies","kills","deaths","assists","x","y"], dtype=str)

first_half = np.char.add(column_prefix[:, None], '_')  
output = np.char.add(first_half, column_suffix).ravel().tolist()

players = ["r1", "r2", "r3", "r4", "r5", "d1", "d2", "d3", "d4", "d5"]
stats = ["x", "y", "gold", "kills", "deaths", "assists", "lh", "denies"]

records = []
for _, row in df.iterrows():
    match = row["match_name"]
    for p in players:
        record = {
            "match_name": match,
            "team": "Radiant" if p.startswith("r") else "Dire",
            "player": p
        }
        for stat in stats:
            col = f"{p}_{stat}"
            record[stat] = row.get(col, None)
        records.append(record)

long_df = pd.DataFrame(records)

x_min, x_max = long_df["x"].min(), long_df["x"].max()
y_min, y_max = long_df["y"].min(), long_df["y"].max()

long_df["x"] = ((long_df["x"] - x_min) / (x_max - x_min)) * 8000
long_df["y"] = ((long_df["y"] - y_min) / (y_max - y_min)) * 8000

long_df["y"] = 8000 - long_df["y"]

frames = []
for match in long_df["match_name"].unique()[:100]:
    match_df = long_df[long_df["match_name"] == match]
    frames.append(go.Frame(
        data=[
            go.Scatter(
                x=match_df["x"],
                y=match_df["y"],
                mode="markers",
                marker=dict(
                    size=match_df["gold"] / 1000,
                    color=match_df["team"].map({"Radiant": "blue", "Dire": "red"}),
                    sizemode="area",
                    sizeref=2.*match_df["gold"].max()/1000**2,
                    line=dict(width=1, color='white')
                ),
                text=[
                    f"{row['player']}<br>Gold: {row['gold']}<br>KDA: {row['kills']}/{row['deaths']}/{row['assists']}<br>LH/D: {row['lh']}/{row['denies']}"
                    for _, row in match_df.iterrows()
                ],
                hoverinfo="text"
            )
        ],
        name=match
    ))

initial_match = long_df["match_name"].unique()[0]
initial_df = long_df[long_df["match_name"] == initial_match]

fig = go.Figure(
    data=[go.Scatter(
        x=initial_df["x"],
        y=initial_df["y"],
        mode="markers",
        marker=dict(
            size=initial_df["gold"] / 1000,
            color=initial_df["team"].map({"Radiant": "blue", "Dire": "red"}),
            sizemode="area",
            sizeref=2.*initial_df["gold"].max()/1000**2,
            line=dict(width=1, color='white')
        ),
        text=[
            f"{row['player']}<br>Gold: {row['gold']}<br>KDA: {row['kills']}/{row['deaths']}/{row['assists']}<br>LH/D: {row['lh']}/{row['denies']}"
            for _, row in initial_df.iterrows()
        ],
        hoverinfo="text"
    )],
    layout=go.Layout(
        images=[dict(
            source=encoded_image,
            xref="x",
            yref="y",
            x=0,
            y=8000,
            sizex=8000,
            sizey=8000,
            sizing="stretch",
            layer="below"
        )],
        xaxis=dict(range=[0, 8000], showgrid=False, zeroline=False),
        yaxis=dict(range=[0, 8000], showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1),
        width=900,
        height=900,
        sliders=[{
            "steps": [
                {"method": "animate", "label": match, "args": [[match], {"mode": "immediate"}]}
                for match in long_df["match_name"].unique()[:100]
            ],
            "transition": {"duration": 0},
            "x": 0,
            "y": -0.1,
            "currentvalue": {"prefix": "Match: "}
        }],
        title="Dota 2 Player Stat Visualizer at Match End"
    ),
    frames=frames  
)

plotly(fig)