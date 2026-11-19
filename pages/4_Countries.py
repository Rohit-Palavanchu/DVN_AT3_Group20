"""Member 4: countries. See docs/ai_provenance.md for how this page was produced and checked."""

from __future__ import annotations

import altair as alt
import streamlit as st

from src.common import OI, SIZE_COLOURS, SIZE_DASH, SIZE_ORDER, footer, pct, setup

size, country, sector, refresh, eu_all, years = setup("Who has adopted AI?")
first_year, last_year = years[0], years[-1]
eu_last = float(eu_all.iloc[-1]["pct_enterprises"])

st.caption("Who has adopted AI? · Countries")
st.divider()
st.header("4 · Which countries lead and which lag?")
cy_years = sorted(country["year"].unique())
c_year = st.select_slider("Year", options=cy_years, value=cy_years[-1], key="country_year")
all_names = sorted(country.loc[country["geo"] != "EU27_2020", "country"].unique())
chosen = st.multiselect("Countries shown", all_names, default=all_names, key="country_pick")
eu_val = country.query("geo == 'EU27_2020' and year == @c_year")["pct_enterprises"]
rows = country[(country["year"] == c_year) & country["country"].isin(chosen)].copy()
st.caption(f"Each country's share of enterprises using AI in {c_year}, minus the EU27 average "
           f"({pct(eu_val.iloc[0]) if not eu_val.empty else 'n/a'}). Unit: percentage points. "
           "Bars right of zero are above the EU average.")
if rows.empty or eu_val.empty:
    st.info("No countries selected, or no data for that year. Choose at least one country.")
else:
    rows["diff"] = rows["pct_enterprises"] - float(eu_val.iloc[0])
    rows["side"] = rows["diff"].map(lambda v: "Above EU average" if v >= 0 else "Below EU average")
    rows["label"] = rows.apply(lambda r: f"{r['pct_enterprises']:.2f}%", axis=1)
    rank = rows.sort_values("diff", ascending=False)["country"].tolist()
    span = max(abs(rows["diff"].min()), abs(rows["diff"].max()))
    bars = alt.Chart(rows).mark_bar(size=18).encode(
        y=alt.Y("country:N", sort=rank, title=None,
                axis=alt.Axis(labelOverlap=False, labelLimit=200, labelFontSize=12)),
        x=alt.X("diff:Q", title=f"Difference from EU27 average (percentage points), {c_year}",
                scale=alt.Scale(domain=[min(rows["diff"].min(), 0) - span * 0.15,
                                        max(rows["diff"].max(), 0) + span * 0.15])),
        color=alt.Color("side:N", title=None,
                        scale=alt.Scale(domain=["Above EU average", "Below EU average"],
                                        range=[OI["blue"], OI["orange"]]),
                        legend=alt.Legend(orient="top")))
    pos = alt.Chart(rows[rows["diff"] >= 0]).mark_text(fontSize=11, color="#222", align="left", dx=4).encode(
        y=alt.Y("country:N", sort=rank), x="diff:Q", text="label:N")
    neg = alt.Chart(rows[rows["diff"] < 0]).mark_text(fontSize=11, color="#222", align="right", dx=-4).encode(
        y=alt.Y("country:N", sort=rank), x="diff:Q", text="label:N")
    txt = pos + neg
    st.altair_chart((bars + txt).properties(
        height=26 * len(rows) + 60,
        title=f"Countries above and below the EU27 average, {c_year} (labels: % of enterprises)"),
        width="stretch")

footer(refresh)
