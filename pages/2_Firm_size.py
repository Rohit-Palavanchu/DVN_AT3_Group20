"""Member 2: firm size. See docs/ai_provenance.md for how this page was produced and checked."""

from __future__ import annotations

import altair as alt
import streamlit as st

from src.common import OI, SIZE_COLOURS, SIZE_DASH, SIZE_ORDER, footer, pct, setup

size, country, sector, refresh, eu_all, years = setup("Who has adopted AI?")
first_year, last_year = years[0], years[-1]
eu_last = float(eu_all.iloc[-1]["pct_enterprises"])

st.caption("Who has adopted AI? · Firm size")
st.divider()
st.header("2 · Are small firms keeping up?")
countries = ["EU27"] + sorted(size.loc[size["geo"] != "EU27_2020", "country"].unique())
pick = st.selectbox("Choose a country", countries, index=0, key="size_country")
geo_rows = size[(size["country"] == pick) & size["size_class"].isin(SIZE_ORDER)]
st.caption(f"Share of enterprises using AI by firm size, {pick}, {first_year}-{last_year}. "
           "Unit: % of enterprises in each size class.")
if geo_rows.empty:
    st.info(f"Eurostat publishes no size breakdown for {pick}. Choose another country.")
else:
    enc = dict(
        x=alt.X("year:Q", title="Survey year", axis=alt.Axis(format="d", values=years),
                scale=alt.Scale(domain=[first_year - 0.3, last_year + 1.2])),
        y=alt.Y("pct_enterprises:Q", title="Enterprises using AI (%)"),
        color=alt.Color("size_class:N", title="Firm size (employees)",
                        scale=alt.Scale(domain=SIZE_ORDER, range=SIZE_COLOURS),
                        legend=alt.Legend(orient="top")),
        strokeDash=alt.StrokeDash("size_class:N", scale=alt.Scale(domain=SIZE_ORDER, range=SIZE_DASH),
                                  legend=None),
    )
    lines = alt.Chart(geo_rows).mark_line(strokeWidth=3, point=True).encode(**enc)
    labels_above = alt.Chart(geo_rows[geo_rows["size_class"] != "Small (10-49)"]).mark_text(
        dy=-12, fontSize=12).encode(
        x="year:Q", y="pct_enterprises:Q",
        text=alt.Text("pct_enterprises:Q", format=".2f"),
        color=alt.Color("size_class:N", scale=alt.Scale(domain=SIZE_ORDER, range=SIZE_COLOURS),
                        legend=None))
    labels = alt.Chart(geo_rows[geo_rows["size_class"] == "Small (10-49)"]).mark_text(dy=16, fontSize=12).encode(
        x="year:Q", y="pct_enterprises:Q",
        text=alt.Text("pct_enterprises:Q", format=".2f"),
        color=alt.Color("size_class:N", scale=alt.Scale(domain=SIZE_ORDER, range=SIZE_COLOURS),
                        legend=None))
    st.altair_chart((lines + labels_above + labels).properties(
        height=320, title=f"AI use by firm size in {pick}, % of enterprises"), width="stretch")
    gap = geo_rows.pivot_table(index="year", columns="size_class", values="pct_enterprises")
    if {"Large (250+)", "Small (10-49)"} <= set(gap.columns):
        g = (gap["Large (250+)"] - gap["Small (10-49)"]).dropna()
        if len(g) >= 2:
            st.markdown(f"Gap between large and small firms in {pick}: **{g.iloc[0]:.2f} points** in "
                        f"{int(g.index[0])}, **{g.iloc[-1]:.2f} points** in {int(g.index[-1])}.")

footer(refresh)
