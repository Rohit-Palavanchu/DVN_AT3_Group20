"""
Member 2: Firm size analysis.
See docs/ai_provenance.md for how this page was produced and checked.
"""

import altair as alt
import streamlit as st

from src.common import SIZE_COLOURS, SIZE_DASH, SIZE_ORDER, footer, setup

# Load shared data and page setup
size_df, _, _, refresh, _, years = setup("Who has adopted AI?")
first_year = years[0]
last_year = years[-1]

# Page header
st.caption("Who has adopted AI? · Firm size")
st.divider()
st.header("2 · Are small firms keeping up?")

# Country selector (EU27 first, then alphabetical)
other_countries = sorted(size_df.loc[size_df["geo"] != "EU27_2020", "country"].unique())
country_options = ["EU27"] + other_countries

selected_country = st.selectbox(
    "Choose a country",
    country_options,
    index=0,
    key="size_country",
)

# Filter to the selected country and valid size classes
country_data = size_df[
    (size_df["country"] == selected_country)
    & (size_df["size_class"].isin(SIZE_ORDER))
]

st.caption(
    f"Share of enterprises using AI by firm size, {selected_country}, {first_year}-{last_year}. "
    "Unit: % of enterprises in each size class."
)

if country_data.empty:
    st.info(f"Eurostat publishes no size breakdown for {selected_country}. Choose another country.")
else:
    color_scale = alt.Scale(domain=SIZE_ORDER, range=SIZE_COLOURS)
    dash_scale = alt.Scale(domain=SIZE_ORDER, range=SIZE_DASH)

    # Main trend lines
    lines = (
        alt.Chart(country_data)
        .mark_line(strokeWidth=3, point=True)
        .encode(
            x=alt.X(
                "year:Q",
                title="Survey year",
                axis=alt.Axis(format="d", values=years),
                scale=alt.Scale(domain=[first_year - 0.3, last_year + 1.2]),
            ),
            y=alt.Y("pct_enterprises:Q", title="Enterprises using AI (%)"),
            color=alt.Color(
                "size_class:N",
                title="Firm size (employees)",
                scale=color_scale,
                legend=alt.Legend(orient="top"),
            ),
            strokeDash=alt.StrokeDash("size_class:N", scale=dash_scale, legend=None),
        )
    )

    # Put labels above the line for medium/large firms and below for small firms to avoid overlap
    non_small_data = country_data[country_data["size_class"] != "Small (10-49)"]
    small_data = country_data[country_data["size_class"] == "Small (10-49)"]

    labels_above = (
        alt.Chart(non_small_data)
        .mark_text(dy=-12, fontSize=12)
        .encode(
            x="year:Q",
            y="pct_enterprises:Q",
            text=alt.Text("pct_enterprises:Q", format=".2f"),
            color=alt.Color("size_class:N", scale=color_scale, legend=None),
        )
    )

    labels_below = (
        alt.Chart(small_data)
        .mark_text(dy=16, fontSize=12)
        .encode(
            x="year:Q",
            y="pct_enterprises:Q",
            text=alt.Text("pct_enterprises:Q", format=".2f"),
            color=alt.Color("size_class:N", scale=color_scale, legend=None),
        )
    )

    chart = (lines + labels_above + labels_below).properties(
        height=320,
        title=f"AI use by firm size in {selected_country}, % of enterprises",
    )
    st.altair_chart(chart, width="stretch")

    # Calculate the percentage-point gap between large and small firms
    pivoted = country_data.pivot_table(
        index="year",
        columns="size_class",
        values="pct_enterprises",
    )

    if "Large (250+)" in pivoted.columns and "Small (10-49)" in pivoted.columns:
        gap_series = (pivoted["Large (250+)"] - pivoted["Small (10-49)"]).dropna()
        if len(gap_series) >= 2:
            start_year = int(gap_series.index[0])
            end_year = int(gap_series.index[-1])
            st.markdown(
                f"Gap between large and small firms in {selected_country}: "
                f"**{gap_series.iloc[0]:.2f} points** in {start_year}, "
                f"**{gap_series.iloc[-1]:.2f} points** in {end_year}."
            )

footer(refresh)
