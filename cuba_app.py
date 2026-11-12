from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Chart colors: dark red, with lighter shades of the same red when a chart has more than one color.
DARK_RED = "#8E1111"
MID_RED = "#CF5C5C"
LIGHT_RED = "#EFADAD"
LABEL_SIZE = 20  # size of the numbers on the charts
AXIS_SIZE = 18  # size of the words on the charts (axis labels)
LEGEND_SIZE = 24  # size of the legend (the color key, like Elk and Mule deer)
LEGEND = dict(font=dict(size=LEGEND_SIZE), title=dict(font=dict(size=LEGEND_SIZE)))

st.set_page_config(page_title="Project Cuba Corridor", layout="wide")
st.title("Project Cuba Corridor")
st.write(
    "Crash safety in Cuba, NM and Sandoval County. "
    "Source: UNM Geospatial and Population Studies (UNM-GPS) community crash reports "
    "for NMDOT, 2025 release."
)


BASE = Path(__file__).parent


def find_data_dir():
    # Looks for a folder named data (or Data) next to this file.
    for name in ("data", "Data"):
        p = BASE / name
        if p.is_dir():
            return p
    return None


DATA_DIR = find_data_dir()


def find_file(name):
    # Finds the CSV even if a download added a suffix like " (1)".
    stem = name.replace(".csv", "")
    matches = sorted(DATA_DIR.glob(stem + "*.csv")) if DATA_DIR else []
    if not matches:
        st.error(f"Could not find {name}. Put all the CSV files in a folder named data, next to this app file.")
        st.write("Folders and files next to the app:", sorted(p.name for p in BASE.iterdir()))
        if DATA_DIR:
            st.write("Files found in the data folder:", sorted(p.name for p in DATA_DIR.iterdir()))
        st.stop()
    return matches[-1]


@st.cache_data
def read_csv_cached(path):
    return pd.read_csv(path)


def load(name):
    return read_csv_cached(find_file(name))


cuba_year = load("cuba_crashes_by_year.csv")
cuba_event = load("cuba_first_harmful_event.csv")
cuba_month = load("cuba_crashes_by_month.csv")
sand_year = load("sandoval_crashes_by_year.csv")
sand_event = load("sandoval_first_harmful_event.csv")

tab1, tab2, tab_us550, tab3 = st.tabs(
    ["Cuba crashes", "Animal crashes", "US 550 wildlife corridor", "About the data"]
)

# ---------- Tab 1: Cuba crashes ----------
with tab1:
    st.subheader("Crashes per year in Cuba village, 2016 to 2025")
    fig1 = px.bar(
        cuba_year,
        x="year",
        y=["fatal", "injury", "property_damage_only"],
        labels={"value": "Crashes", "year": "Year", "variable": "Severity"},
        color_discrete_sequence=[DARK_RED, MID_RED, LIGHT_RED],
    )
    fig1.update_xaxes(type="category")
    fig1.update_layout(bargap=0.6, font_size=AXIS_SIZE, legend=LEGEND)
    fig1.add_trace(
        go.Scatter(
            x=cuba_year["year"],
            y=cuba_year["total"],
            mode="text",
            text="<b>" + cuba_year["total"].astype(int).astype(str) + "</b>",
            textfont=dict(size=LABEL_SIZE + 2),
            textposition="top center",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig1.update_yaxes(range=[0, cuba_year["total"].max() * 1.2])
    st.plotly_chart(fig1)
    st.caption(
        f"Total crashes dropped from {int(cuba_year.total.iloc[0])} in 2016 "
        f"to {int(cuba_year.total.iloc[-1])} in 2025. Numbers are small, so one crash "
        "can change the trend."
    )

    st.subheader("Cuba crashes by month, 2021 to 2025 combined")
    months = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December",
    ]
    m = cuba_month.groupby("month", as_index=False)["crashes"].sum()
    m["month"] = pd.Categorical(m["month"], categories=months, ordered=True)
    m = m.sort_values("month")
    fig2 = px.bar(
        m,
        x="month",
        y="crashes",
        labels={"month": "Month", "crashes": "Crashes"},
        color_discrete_sequence=[DARK_RED],
        text_auto=True,
    )
    fig2.update_layout(bargap=0.65, font_size=AXIS_SIZE)
    fig2.update_traces(
        texttemplate="<b>%{y}</b>",
        textfont_size=LABEL_SIZE,
        textposition="outside",
        cliponaxis=False,
    )
    st.plotly_chart(fig2)
    st.caption(
        f"Only {int(m.crashes.sum())} crashes over five years, so this pattern is weak. "
        "One crash can move a bar. Treat it as a rough look, not a seasonal trend."
    )

# ---------- Tab 2: Animal crashes ----------
with tab2:
    def animal_by_year(event_df, year_df):
        a = event_df[event_df.first_harmful_event == "Collision with Animal"][["year", "crashes"]]
        t = year_df[year_df.year >= 2021][["year", "total"]]
        out = a.merge(t, on="year")
        out["percent"] = 100 * out["crashes"] / out["total"]
        return out

    cu = animal_by_year(cuba_event, cuba_year)
    cu["Area"] = "Cuba village"
    sa = animal_by_year(sand_event, sand_year)
    sa["Area"] = "Sandoval County"
    both = pd.concat([cu, sa])

    st.subheader("Share of crashes that started with hitting an animal, by year")
    fig3 = px.bar(
        both,
        x="year",
        y="percent",
        color="Area",
        barmode="group",
        text_auto=".1f",
        labels={"percent": "Percent of all crashes", "year": "Year"},
        color_discrete_map={"Cuba village": DARK_RED, "Sandoval County": MID_RED},
    )
    fig3.update_xaxes(type="category")
    fig3.update_layout(bargap=0.55, font_size=AXIS_SIZE, legend=LEGEND)
    fig3.update_traces(
        texttemplate="<b>%{y:.1f}</b>",
        textfont_size=LABEL_SIZE - 4,
        textposition="outside",
        cliponaxis=False,
    )
    st.plotly_chart(fig3)

    cu_a, cu_t = int(cu.crashes.sum()), int(cu.total.sum())
    sa_a, sa_t = int(sa.crashes.sum()), int(sa.total.sum())
    st.caption(
        f"2021 to 2025: Cuba had {cu_a} animal crashes out of {cu_t} total "
        f"({100 * cu_a / cu_t:.1f}%). Sandoval County had {sa_a} out of {sa_t:,} "
        f"({100 * sa_a / sa_t:.1f}%)."
    )


# ---------- Tab: US 550 wildlife corridor ----------
with tab_us550:
    ph = load("us550_phase_crashes.csv")
    structures = load("us550_planned_structures.csv")

    st.subheader("Reported elk and deer crashes on US 550 north of Cuba, 2008 to 2021")
    st.write(
        "NMDOT's scoping report split the wildlife hotspot (MP 64.93 to MP 80.64) into "
        "four building phases. These are the reported crashes in each phase."
    )
    ph["label"] = ph["phase"] + " (" + ph["mileposts"] + ")"
    long = ph.melt(
        id_vars=["label"],
        value_vars=["elk_crashes", "deer_crashes"],
        var_name="Animal",
        value_name="Crashes",
    )
    long["Animal"] = long["Animal"].map({"elk_crashes": "Elk", "deer_crashes": "Mule deer"})
    fig5 = px.bar(
        long,
        x="label",
        y="Crashes",
        color="Animal",
        labels={"label": ""},
        color_discrete_map={"Elk": DARK_RED, "Mule deer": MID_RED},
        text_auto=True,
    )
    fig5.update_layout(bargap=0.6, font_size=AXIS_SIZE, legend=LEGEND)
    fig5.update_traces(
        texttemplate="<b>%{y}</b>",
        textfont=dict(size=LABEL_SIZE, color="white"),
        textposition="inside",
    )
    fig5.add_trace(
        go.Scatter(
            x=ph["label"],
            y=ph["total_crashes"],
            mode="text",
            text="<b>" + ph["total_crashes"].astype(int).astype(str) + "</b>",
            textfont=dict(size=LABEL_SIZE + 2),
            textposition="top center",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig5.update_yaxes(range=[0, ph["total_crashes"].max() * 1.2])
    st.plotly_chart(fig5)

    st.subheader("Crashes per mile in each phase")
    fig6 = px.bar(
        ph,
        x="label",
        y="crashes_per_mile",
        text_auto=".1f",
        labels={"label": "", "crashes_per_mile": "Reported crashes per mile, 2008 to 2021"},
        color_discrete_sequence=[DARK_RED],
    )
    fig6.update_layout(bargap=0.7, font_size=AXIS_SIZE)
    fig6.update_traces(
        texttemplate="<b>%{y:.1f}</b>",
        textfont_size=LABEL_SIZE,
        textposition="outside",
        cliponaxis=False,
    )
    st.plotly_chart(fig6)
    st.caption(
        f"Total: {int(ph.total_crashes.sum())} crashes over {ph.miles.sum():.2f} miles "
        f"({int(ph.elk_crashes.sum())} elk, {int(ph.deer_crashes.sum())} mule deer). "
        "Crashes per mile are close to even across the four phases, about 24 to 27 per mile, "
        "so the whole stretch is a hotspot and not one single spot."
    )

    st.subheader("Which animals: elk vs mule deer")
    sp = pd.DataFrame(
        {
            "Animal": ["Elk", "Mule deer"],
            "Crashes": [int(ph.elk_crashes.sum()), int(ph.deer_crashes.sum())],
        }
    )
    sp["Label"] = sp["Crashes"].astype(str) + " (" + (100 * sp["Crashes"] / sp["Crashes"].sum()).round(1).astype(str) + "%)"
    fig7 = px.bar(
        sp,
        x="Animal",
        y="Crashes",
        text="Label",
        color="Animal",
        color_discrete_map={"Elk": DARK_RED, "Mule deer": MID_RED},
    )
    fig7.update_layout(showlegend=False)
    fig7.update_layout(bargap=0.75, font_size=AXIS_SIZE)
    fig7.update_traces(
        texttemplate="<b>%{text}</b>",
        textfont_size=LABEL_SIZE,
        textposition="outside",
        cliponaxis=False,
    )
    st.plotly_chart(fig7)
    st.caption(
        "Reported elk and mule deer crashes, MP 64.93 to 80.64, 2008 to 2021. "
        "Other animals such as bears or cougars are not in these tables."
    )

    st.subheader("Planned wildlife crossings (from the scoping report)")
    st.dataframe(structures, hide_index=True)


# ---------- Tab 3: About the data ----------
with tab3:
    st.subheader("Sources")
    st.markdown(
        "- UNM-GPS Community Crash Reports (NMDOT crash database): "
        "https://gps.unm.edu/tru/reports/community-reports/index.html\n"
        "- NMDOT US 550 Wildlife Crossing Project: "
        "https://www.dot.nm.gov/projects/active-projects/us550wildlifeproject/\n"
        "- NMDOT, US-550 MP 64.93 to MP 80.64 WVC Mitigation Scoping Report, July 2023 "
        "(crash counts by phase and planned crossing locations), linked from the project page above."
    )
    st.subheader("Limitations")
    st.markdown(
        "- Cuba numbers cover the village only, not US 550 north of town.\n"
        "- Counts are small, so trends can change with one or two crashes.\n"
        "- The county comparison is mostly Rio Rancho and other urban roads, so it is a rough "
        "baseline, not a like-for-like comparison.\n"
        "- The data covers reported crashes with a death, an injury, or at least $500 in damage.\n"
        "- The UNM data does not give crash locations, so the Cuba and county charts cannot be "
        "mapped by milepost. The US 550 tab uses the scoping report's counts by phase instead."
    )
