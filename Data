import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Dataset Initialization
df = pd.DataFrame(
    {
        "milepost": [55.0, 59.5, 63.0, 68.0, 72.5, 77.0, 82.0, 85.0],
        "segment_name": [
            "South Approach",
            "Cuba South Main St",
            "Cuba Village Center",
            "Cuba North Outlet",
            "Coyote Canyon / Ridge",
            "Wildlife Hotspot North 1",
            "Wildlife Hotspot North 2",
            "San Juan County Line",
        ],
        "aadt_total": [5800, 6400, 7100, 5300, 4900, 4600, 4400, 4200],
        "truck_traffic_pct": [22.4, 18.1, 15.5, 21.8, 24.5, 25.1, 24.8, 26.0],
        "speed_limit_mph": [65, 45, 35, 55, 65, 65, 65, 65],
        "elk_collisions_yr": [2, 1, 0, 8, 14, 18, 11, 5],
        "deer_collisions_yr": [5, 3, 1, 12, 22, 27, 19, 9],
        "nighttime_pct": [78.0, 65.0, 50.0, 82.0, 89.0, 91.0, 85.0, 80.0],
        "severity_index": [3.2, 2.1, 1.5, 6.4, 8.7, 9.2, 7.8, 5.1],
    }
)

# 2. Subplot Layout Setup (Dual-Y per subplot)
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.12,
    subplot_titles=(
        "<b>Traffic Volume (AADT) vs. Wildlife Collisions (Elk & Deer)</b>",
        "<b>Heavy Freight Share (%) vs. Collision Severity Index</b>",
    ),
    specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
)

# 3. Trace 1: AADT Traffic Volume
fig.add_trace(
    go.Scatter(
        x=df["milepost"],
        y=df["aadt_total"],
        name="AADT Total Traffic",
        mode="lines+markers",
        line=dict(color="#1f77b4", width=3),
        text=df["segment_name"],
        hovertemplate="<b>%{text} (MP %{x})</b><br>AADT: %{y:,} vehicles/day<extra></extra>",
    ),
    row=1,
    col=1,
    secondary_y=False,
)

# 4. Trace 2 & 3: Elk & Deer Collisions
fig.add_trace(
    go.Bar(
        x=df["milepost"],
        y=df["elk_collisions_yr"],
        name="Elk Collisions/Yr",
        marker_color="#d62728",
        opacity=0.75,
        hovertemplate="<b>MP %{x}</b><br>Elk Collisions: %{y}/yr<extra></extra>",
    ),
    row=1,
    col=1,
    secondary_y=True,
)

fig.add_trace(
    go.Bar(
        x=df["milepost"],
        y=df["deer_collisions_yr"],
        name="Deer Collisions/Yr",
        marker_color="#ff7f0e",
        opacity=0.75,
        hovertemplate="<b>MP %{x}</b><br>Deer Collisions: %{y}/yr<extra></extra>",
    ),
    row=1,
    col=1,
    secondary_y=True,
)

# 5. Trace 4 & 5: Freight Percentage & Crash Severity Index
fig.add_trace(
    go.Scatter(
        x=df["milepost"],
        y=df["truck_traffic_pct"],
        name="Freight Truck Traffic %",
        mode="lines+markers",
        line=dict(color="#2ca02c", width=2.5),
        hovertemplate="<b>MP %{x}</b><br>Freight Share: %{y}%<extra></extra>",
    ),
    row=2,
    col=1,
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(
        x=df["milepost"],
        y=df["severity_index"],
        name="Crash Severity Index (1-10)",
        mode="lines+markers",
        line=dict(color="#9467bd", width=2.5, dash="dash"),
        hovertemplate="<b>MP %{x}</b><br>Severity Index: %{y}/10<extra></extra>",
    ),
    row=2,
    col=1,
    secondary_y=True,
)

# 6. Highlight Critical Hotspot Zone
fig.add_vrect(
    x0=71.0,
    x1=80.0,
    fillcolor="rgba(255, 0, 0, 0.1)",
    layer="below",
    line_width=0,
    annotation_text="Critical Wildlife Hotspot Zone",
    annotation_position="top left",
    row=1,
    col=1,
)

# 7. Layout & Styling Customization
fig.update_layout(
    title_text="<b>U.S. 550 Corridor Safety Analysis: Cuba, NM</b>",
    template="plotly_white",
    height=750,
    hovermode="x unified",
    barmode="group",
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
    ),
)

fig.update_xaxes(title_text="U.S. 550 Milepost (MP)", row=2, col=1)
fig.update_yaxes(
    title_text="AADT Volume", row=1, col=1, secondary_y=False
)
fig.update_yaxes(
    title_text="Collisions / Year", row=1, col=1, secondary_y=True
)
fig.update_yaxes(
    title_text="Truck Traffic (%)", row=2, col=1, secondary_y=False
)
fig.update_yaxes(
    title_text="Severity Index (1-10)", row=2, col=1, secondary_y=True
)

# Render or export
fig.show()
fig.write_html("us550_safety_dashboard.html")
