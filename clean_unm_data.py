"""
clean_unm_data.py

Turns the raw crash data into the small CSV files that the Streamlit app reads.

RAW DATA (put these two files in data/raw/):
  city-2025-excel.xlsx    https://gps.unm.edu/assets/documents/community/city-2025-excel.xlsx
  county-2025-excel.xlsx  https://gps.unm.edu/assets/documents/community/county-2025-excel.xlsx
  Source page: https://gps.unm.edu/tru/reports/community-reports/index.html
  (UNM Geospatial and Population Studies, from the NMDOT crash database)

OUTPUT (written to data/):
  cuba_crashes_by_year.csv, cuba_first_harmful_event.csv, cuba_crashes_by_month.csv,
  sandoval_crashes_by_year.csv, sandoval_first_harmful_event.csv,
  us550_phase_crashes.csv, us550_planned_structures.csv

NEEDS: pip install pandas openpyxl
RUN (from the main repo folder): python scripts/clean_unm_data.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

CITY_FILE = RAW / "city-2025-excel.xlsx"
COUNTY_FILE = RAW / "county-2025-excel.xlsx"

# The UNM workbook has one sheet per table. Every city (or county) is stacked in the
# same sheet, with the place name in the first column.
#   ACB = Table 1: total crashes by severity, 2016 to 2025
#   FCF = Table 12: crashes by first harmful event (this is where "Collision with Animal" is), 2021 to 2025
#   DCB = Table 2: crashes by month, 2021 to 2025
SHEET_BY_YEAR = "ACB"
SHEET_BY_EVENT = "FCF"
SHEET_BY_MONTH = "DCB"

# Keep the main crash types and drop the sub-categories.
EVENTS_TO_KEEP = [
    "Collision with Animal",
    "Collision with Fixed Object",
    "Collision with Motor Vehicle",
    "Collision with Other Non-Fixed Object",
    "Collision with Person",
    "Pedestrian",
    "Non-Collision",
]


def pick_place(path, sheet, place):
    """Read one sheet and keep only the rows for one place (for example CUBA)."""
    df = pd.read_excel(path, sheet_name=sheet)
    names = df.iloc[:, 0].fillna("").astype(str).str.upper().str.strip()
    return df[names == place].copy()


def crashes_by_year(path, place):
    df = pick_place(path, SHEET_BY_YEAR, place)
    df = df[["Year", "Fatal Crash", "Injury Crash", "Property Damage Only Crash", "Total Crashes"]]
    df.columns = ["year", "fatal", "injury", "property_damage_only", "total"]
    return df.astype(int)


def crashes_by_first_harmful_event(path, place):
    df = pick_place(path, SHEET_BY_EVENT, place)
    df = df[df["First Harmful Event"].isin(EVENTS_TO_KEEP)]
    df = df[["First Harmful Event", "2021", "2022", "2023", "2024", "2025"]]
    # Turn the five year columns into rows: one row per event and year.
    df = df.melt(id_vars="First Harmful Event", var_name="year", value_name="crashes")
    df.columns = ["first_harmful_event", "year", "crashes"]
    df["year"] = df["year"].astype(int)
    df["crashes"] = df["crashes"].astype(int)
    return df


def crashes_by_month(path, place):
    df = pick_place(path, SHEET_BY_MONTH, place)
    df = df[["Month", "2021", "2022", "2023", "2024", "2025"]]
    df = df.melt(id_vars="Month", var_name="year", value_name="crashes")
    df.columns = ["month", "year", "crashes"]
    df["year"] = df["year"].astype(int)
    df["crashes"] = df["crashes"].astype(int)
    return df


def us550_tables():
    """
    US 550 wildlife hotspot numbers. These come from a PDF, so they are typed in by hand
    from the NMDOT scoping report: "US-550 MP 64.93 to MP 80.64 WVC Mitigation Scoping
    Report", July 2023 (linked from
    https://www.dot.nm.gov/projects/active-projects/us550wildlifeproject/).

    Crash counts are reported elk and mule deer crashes, 2008 to 2021, from Tables 6, 9, 12
    and 15. Each phase lists property damage crashes plus injury crashes.
    """
    # phase, start MP, end MP, deer property damage, deer injury, elk property damage, elk injury
    phases = [
        ("Phase 1", 64.93, 69.14, 41, 1, 69, 4),  # Table 6
        ("Phase 2", 69.14, 72.98, 33, 5, 58, 2),  # Table 9
        ("Phase 3", 72.98, 75.62, 32, 1, 29, 2),  # Table 12
        ("Phase 4", 75.62, 80.64, 50, 2, 69, 1),  # Table 15
    ]
    rows = []
    for name, start, end, deer_pd, deer_inj, elk_pd, elk_inj in phases:
        miles = round(end - start, 2)
        deer = deer_pd + deer_inj
        elk = elk_pd + elk_inj
        total = deer + elk
        rows.append(
            (name, f"MP {start} to {end}", miles, deer, elk, total, round(total / miles, 1))
        )
    phase_df = pd.DataFrame(
        rows,
        columns=["phase", "mileposts", "miles", "deer_crashes", "elk_crashes",
                 "total_crashes", "crashes_per_mile"],
    )
    # Check against the report's Table 18 (whole corridor): 399 crashes, 165 deer, 234 elk.
    assert phase_df["total_crashes"].sum() == 399
    assert phase_df["deer_crashes"].sum() == 165
    assert phase_df["elk_crashes"].sum() == 234

    # Planned crossings by milepost, from the report's phase descriptions (Section 7).
    structures = pd.DataFrame(
        [
            ("WC-01", "Overpass", 65.97, "Phase 1"),
            ("WC-04", "Underpass", 67.55, "Phase 1"),
            ("WC-07", "Overpass", 70.28, "Phase 2"),
            ("WC-08", "Underpass", 71.81, "Phase 2"),
            ("WC-10", "Underpass", 72.99, "Phase 3"),
            ("WC-12", "Underpass", 74.85, "Phase 3"),
            ("WC-16", "Overpass", 76.98, "Phase 4"),
        ],
        columns=["structure", "type", "milepost", "phase"],
    )
    return phase_df, structures


def main():
    for f in (CITY_FILE, COUNTY_FILE):
        if not f.exists():
            raise SystemExit(f"Missing {f}. Download it from the UNM page (see the top of this file).")

    OUT.mkdir(exist_ok=True)

    crashes_by_year(CITY_FILE, "CUBA").to_csv(OUT / "cuba_crashes_by_year.csv", index=False)
    crashes_by_first_harmful_event(CITY_FILE, "CUBA").to_csv(
        OUT / "cuba_first_harmful_event.csv", index=False
    )
    crashes_by_month(CITY_FILE, "CUBA").to_csv(OUT / "cuba_crashes_by_month.csv", index=False)

    crashes_by_year(COUNTY_FILE, "SANDOVAL").to_csv(
        OUT / "sandoval_crashes_by_year.csv", index=False
    )
    crashes_by_first_harmful_event(COUNTY_FILE, "SANDOVAL").to_csv(
        OUT / "sandoval_first_harmful_event.csv", index=False
    )

    phase_df, structures = us550_tables()
    phase_df.to_csv(OUT / "us550_phase_crashes.csv", index=False)
    structures.to_csv(OUT / "us550_planned_structures.csv", index=False)

    # Quick sanity check printout.
    cuba = pd.read_csv(OUT / "cuba_crashes_by_year.csv")
    print("Cuba crashes 2016 to 2025:", int(cuba["total"].sum()))
    print("Wrote 7 CSV files to", OUT)


if __name__ == "__main__":
    main()
