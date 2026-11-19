"""Member 1: EU trend. See docs/ai_provenance.md for how this page was produced and checked."""

from __future__ import annotations

import altair as alt
import streamlit as st

from src.common import OI, SIZE_COLOURS, SIZE_DASH, SIZE_ORDER, footer, pct, setup

size, country, sector, refresh, eu_all, years = setup("Who has adopted AI?")
first_year, last_year = years[0], years[-1]
eu_last = float(eu_all.iloc[-1]["pct_enterprises"])

st.caption("Who has adopted AI? · EU trend")
st.divider()
st.header("1 · How fast has adoption grown across the EU?")
st.caption(f"Share of EU27 enterprises using at least one AI technology, {first_year}-{last_year}. "
           "Unit: % of enterprises (10+ employees). Points mark the survey years: "
           "Eurostat did not collect this indicator in every year.")
base = alt.Chart(eu_all).encode(
    x=alt.X("year:Q", title="Survey year", axis=alt.Axis(format="d", values=years),
            scale=alt.Scale(domain=[first_year - 0.3, last_year + 0.3])),
    y=alt.Y("pct_enterprises:Q", title="Enterprises using AI (%)",
            scale=alt.Scale(domain=[0, max(25, eu_last * 1.25)])),
)
trend = (base.mark_line(color=OI["blue"], strokeWidth=3)
         + base.mark_point(color=OI["blue"], filled=True, size=90)
         + base.mark_text(dy=-14, fontSize=13, fontWeight="bold", color="#222").encode(
             text=alt.Text("pct_enterprises:Q", format=".2f")))
st.altair_chart(trend.properties(height=300, title="EU firms using AI, % of enterprises"),
                width="stretch")
st.caption("Context: ChatGPT was released in November 2022, between the 2021 and 2023 surveys. "
           "These data show timing only; they cannot show that ChatGPT caused the increase.")

footer(refresh)
