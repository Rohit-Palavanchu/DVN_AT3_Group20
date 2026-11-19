"""Member 3: industries. See docs/ai_provenance.md for how this page was produced and checked."""

from __future__ import annotations

import altair as alt
import streamlit as st

from src.common import OI, SIZE_COLOURS, SIZE_DASH, SIZE_ORDER, footer, pct, setup

size, country, sector, refresh, eu_all, years = setup("Who has adopted AI?")
first_year, last_year = years[0], years[-1]
eu_last = float(eu_all.iloc[-1]["pct_enterprises"])

st.caption("Who has adopted AI? · Industries")
st.divider()
st.header("3 · Which industries have adopted AI?")
sec_years = sorted(sector["year"].unique())
base_year = st.radio("Compare with", [y for y in sec_years if y != sec_years[-1]],
                     horizontal=True, key="sector_base")
latest_sec = sec_years[-1]
s2 = sector[sector["year"].isin([base_year, latest_sec])]
order = (s2[s2["year"] == latest_sec].sort_values("pct_enterprises", ascending=False)["sector"].tolist())
st.caption(f"Share of EU27 enterprises using AI by industry, {base_year} and {latest_sec}, "
           "sorted by the latest year. Unit: % of enterprises in that industry. "
           "Shares do not add to 100%: each is out of the firms in its own industry.")
if s2.empty or not order:
    st.info("No sector data for that year. Choose another year.")
else:
    s2 = s2.assign(year_label=s2["year"].astype(str))
    rule = alt.Chart(s2).mark_line(color="#bbbbbb", strokeWidth=2).encode(
        y=alt.Y("sector:N", sort=order, title=None,
                axis=alt.Axis(labelLimit=300, labelOverlap=False, labelFontSize=12)),
        x="pct_enterprises:Q", detail="sector:N")
    dots = alt.Chart(s2).mark_point(filled=True, size=120, opacity=1).encode(
        y=alt.Y("sector:N", sort=order),
        x=alt.X("pct_enterprises:Q", title="Enterprises using AI (%)",
                scale=alt.Scale(domain=[0, float(s2["pct_enterprises"].max()) * 1.12])),
        color=alt.Color("year_label:N", title="Year",
                        scale=alt.Scale(domain=[str(base_year), str(latest_sec)],
                                        range=[OI["sky"], OI["vermillion"]]),
                        legend=alt.Legend(orient="top")),
        shape=alt.Shape("year_label:N", scale=alt.Scale(domain=[str(base_year), str(latest_sec)],
                                                         range=["circle", "diamond"]), legend=None))
    lab = alt.Chart(s2[s2["year"] == latest_sec]).mark_text(dx=12, align="left", fontSize=12).encode(
        y=alt.Y("sector:N", sort=order), x="pct_enterprises:Q",
        text=alt.Text("pct_enterprises:Q", format=".2f"))
    st.altair_chart((rule + dots + lab).properties(
        height=34 * len(order) + 40, title=f"AI use by industry, EU27, {base_year} vs {latest_sec}"),
        width="stretch")

footer(refresh)
