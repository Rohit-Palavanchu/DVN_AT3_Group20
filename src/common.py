"""Shared data loading, constants and footer used by every page."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

# Okabe-Ito palette: distinguishable with the common colour vision deficiencies.
OI = {"orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73", "blue": "#0072B2",
      "vermillion": "#D55E00", "purple": "#CC79A7", "grey": "#666666"}
SIZE_ORDER = ["Small (10-49)", "Medium (50-249)", "Large (250+)"]
SIZE_COLOURS = [OI["sky"], OI["orange"], OI["blue"]]
SIZE_DASH = [[1, 0], [6, 3], [2, 2]]   # line style as a second cue, not colour alone

QUESTION = ("Since 2021, has AI adoption by European businesses been broad-based, "
            "or has it stayed concentrated in large firms, the tech sector and a few countries?")
SOURCE_LINE = ("Source: Eurostat, *Artificial intelligence by size class of enterprise* "
               "(isoc_eb_ai) and *Artificial intelligence by NACE Rev.2 activity* (isoc_eb_ain2). "
               "Unit: % of enterprises with 10 or more employees and self-employed persons, "
               "excluding the financial sector.")


@st.cache_data
def load() -> dict[str, pd.DataFrame]:
    files = ["adoption_by_size", "adoption_by_country", "adoption_by_sector", "refresh"]
    missing = [f for f in files if not (PROCESSED / f"{f}.csv").exists()]
    if missing:
        st.error(f"Processed data missing: {missing}. Run `python -m src.data` first.")
        st.stop()
    return {f: pd.read_csv(PROCESSED / f"{f}.csv", keep_default_na=False, na_values=[""])
            for f in files}


def pct(v: float) -> str:
    """Two decimals, exactly as Eurostat publishes, so every value traces to the CSV."""
    return f"{v:.2f}%"


def setup(title: str):
    """Page config plus the shared data. Returns size, country, sector, refresh, years."""
    st.set_page_config(page_title=title, layout="wide")
    d = load()
    size, country, sector, refresh = (d["adoption_by_size"], d["adoption_by_country"],
                                      d["adoption_by_sector"], d["refresh"])
    eu_all = size.query("geo == 'EU27_2020' and size_class == 'All (10+)'").sort_values("year")
    years = sorted(int(y) for y in eu_all["year"].unique())
    return size, country, sector, refresh, eu_all, years


def series_breaks() -> str:
    """Countries and years Eurostat flags with a break in series ('b')."""
    country = load()["adoption_by_country"]
    flagged = country[country["flag"].fillna("").astype(str).str.contains("b")]
    if flagged.empty:
        return ""
    return ("Eurostat flags a break in series for "
            + ", ".join(f"{r.country} {r.year}" for r in flagged.itertuples()) + ".")


def footer(refresh: pd.DataFrame, limits: bool = False) -> None:
    """Sources and last data refresh, shown on every page."""
    st.divider()
    if limits:
        st.subheader("What these data cannot show")
        st.markdown(
            "- **Whether AI made firms more productive.** These figures count firms that use AI, not how "
            "much they use it or what changed as a result.\n"
            "- **Intensity.** A firm using one AI tool once counts the same as a firm built around AI.\n"
            "- **Micro-businesses and finance.** The survey covers firms with 10 or more employees and "
            "excludes the financial sector.\n"
            "- **Causes.** Survey years bracket events like the release of ChatGPT, but timing is not cause.\n"
            "- **Sampling error.** These are survey estimates; small differences between countries may "
            "not be meaningful.\n"
            f"- **Breaks in series.** {series_breaks()} Some countries also fall between 2021 and 2023 "
            "(for example Denmark), which may reflect survey changes rather than firms dropping AI. These "
            "data cannot tell the two apart, so compare 2021 with later years cautiously."
        )
    st.subheader("Sources and data refresh")
    st.markdown(SOURCE_LINE)
    for _, r in refresh.iterrows():
        upd = pd.to_datetime(r["eurostat_last_update"], format="%d/%m/%y %H:%M:%S", errors="coerce")
        upd_txt = upd.strftime("%d %B %Y") if pd.notna(upd) else r["eurostat_last_update"]
        st.markdown(f"- `{r['dataset']}`: Eurostat last update **{upd_txt}**, "
                    f"latest observation **{r['latest_year']}**.")
    st.caption("Data dictionary, transforms and AI provenance: see the GitHub repository README.")
