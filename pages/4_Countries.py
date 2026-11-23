"""Member 4: countries. See docs/ai_provenance.md for how this page was produced and checked."""

from __future__ import annotations

import altair as alt
import streamlit as st

from src.common import OI, SIZE_COLOURS, SIZE_DASH, SIZE_ORDER, footer, pct, setup

size, country, sector, refresh, eu_all, years = setup("Who has adopted AI?")

st.caption("Who has adopted AI? · Countries")
st.header("4 · Which countries lead and which lag?")

st.markdown(
    "**The story:** AI adoption differs substantially between EU "
    "member states. Explore which countries lead, which lag, "
    "and whether the gap has changed over time."
)

cy_years = sorted(int(y) for y in country["year"].unique())
all_names = sorted(
    country.loc[country["geo"] != "EU27_2020", "country"]
    .unique().tolist()
)

with st.sidebar:
    st.divider()
    st.subheader("Country explorer")

    c_year = st.select_slider(
        "Survey year",
        options=cy_years,
        value=cy_years[-1],
        key="country_year"
    )

    chosen = st.multiselect(
        "Countries shown",
        options=all_names,
        default=all_names,
        key="country_pick"
    )

    focus_country = st.selectbox(
        "Country spotlight",
        options=all_names,
        index=all_names.index("Denmark"),
        key="country_focus"
    )

    st.caption(
        f"{len(chosen)} of {len(all_names)} countries selected"
    )

current = country[
    (country["year"] == c_year)
    & (country["geo"] != "EU27_2020")
    & country["country"].isin(chosen)
].copy()

eu_rows = country[
    (country["year"] == c_year)
    & (country["geo"] == "EU27_2020")
]

eu_value = (
    float(eu_rows.iloc[0]["pct_enterprises"])
    if not eu_rows.empty else None
)

st.caption(
    "Source: Eurostat `isoc_eb_ai`. Unit: % of enterprises "
    "using at least one AI technology (10+ persons employed, "
    "excluding financial services). "
    f"Survey years: {', '.join(map(str, cy_years))}. "
    "EU27 is an aggregate, not a simple average of countries."
)

ranking_tab, heatmap_tab, trend_tab = st.tabs([
    "Country comparison",
    "Across survey years",
    "Country spotlight"
])

with ranking_tab:
    st.subheader(f"Countries versus EU27 · {c_year}")
    st.caption(
    "Rankings and highest–lowest gaps use only the "
    "currently selected countries. EU27 remains the "
    "full EU aggregate."
    )

    if current.empty or eu_value is None:
        st.info(
            "No countries selected or EU27 reference unavailable. "
            "Choose at least one country."
        )

    else:
        current["diff"] = (
            current["pct_enterprises"] - eu_value
        )

        ordered = current.sort_values(
            "diff", ascending=False
        )

        leader = ordered.iloc[0]
        laggard = ordered.iloc[-1]

        gap = float(
            leader["pct_enterprises"]
            - laggard["pct_enterprises"]
        )

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric(
                "Highest adoption",
                pct(float(leader["pct_enterprises"]))
            )
            st.caption(leader["country"])

        with m2:
            st.metric(
                "Lowest adoption",
                pct(float(laggard["pct_enterprises"]))
            )
            st.caption(laggard["country"])

        with m3:
            st.metric(
                "Highest–lowest gap",
                f"{gap:.2f} pp"
            )
            st.caption(
                f"Among {len(ordered)} selected countries"
            )

        with m4:
            st.metric(
                "EU27 aggregate",
                pct(eu_value)
            )
            st.caption(f"Survey year {c_year}")

        st.markdown(
            f"**Finding:** Among the selected countries, "
            f"**{leader['country']}** leads at "
            f"**{pct(float(leader['pct_enterprises']))}**, "
            f"while **{laggard['country']}** is at "
            f"**{pct(float(laggard['pct_enterprises']))}**. "
            f"The gap is **{gap:.2f} percentage points**."
        )

        ordered["side"] = ordered["diff"].map(
            lambda v: "Above EU27" if v >= 0 else "Below EU27"
        )

        ordered["label"] = ordered["pct_enterprises"].map(
            lambda v: f"{v:.2f}%"
        )

        order = ordered["country"].tolist()
        span = max(float(ordered["diff"].abs().max()), 1)

        x_axis = alt.X(
            "diff:Q",
            title="Difference from EU27 (percentage points)",
            scale=alt.Scale(domain=[
                min(0, float(ordered["diff"].min()))
                - 0.25 * span,
                max(0, float(ordered["diff"].max()))
                + 0.25 * span
            ])
        )

        y_axis = alt.Y(
            "country:N",
            sort=order,
            title=None,
            axis=alt.Axis(
                labelLimit=180,
                labelOverlap=False
            )
        )

        bars = alt.Chart(ordered).mark_bar(
            size=17
        ).encode(
            x=x_axis,
            y=y_axis,
            color=alt.Color(
                "side:N",
                title="Compared with EU27",
                scale=alt.Scale(
                    domain=["Above EU27", "Below EU27"],
                    range=[OI["blue"], OI["orange"]]
                )
            )
        )

        positive_labels = alt.Chart(
            ordered[ordered["diff"] >= 0]
        ).mark_text(
            align="left",
            dx=5,
            color="#F5F5F5",
            fontSize=11
        ).encode(
            x=x_axis,
            y=y_axis,
            text="label:N"
        )

        negative_labels = alt.Chart(
            ordered[ordered["diff"] < 0]
        ).mark_text(
            align="right",
            dx=-5,
            color="#F5F5F5",
            fontSize=11
        ).encode(
            x=x_axis,
            y=y_axis,
            text="label:N"
        )

        st.altair_chart(
            (
                bars + positive_labels + negative_labels
            ).properties(
                title=f"Country AI adoption versus EU27, {c_year}",
                height=max(280, len(ordered) * 27 + 35)
            ),
            width="stretch"
        )

        st.caption(
            "Bars show percentage-point differences from EU27. "
            "Direct labels show each country's adoption rate (%)."
        )


with heatmap_tab:
    st.subheader("Country adoption across survey years")

    historical = country[
        (country["geo"] != "EU27_2020")
        & country["country"].isin(chosen)
    ].copy()

    if historical.empty:
        st.info(
            "Select at least one country to view the heatmap."
        )

    else:
        historical["year_label"] = (
            historical["year"].astype(str)
        )

        order = (
            historical[
                historical["year"] == cy_years[-1]
            ]
            .sort_values(
                "pct_enterprises", ascending=False
            )["country"].tolist()
        )

        base = alt.Chart(historical).encode(
            x=alt.X(
                "year_label:O",
                title="Survey year",
                sort=[str(y) for y in cy_years],
                axis=alt.Axis(labelAngle=0)
            ),
            y=alt.Y(
                "country:N",
                sort=order,
                title=None,
                axis=alt.Axis(
                    labelLimit=180,
                    labelOverlap=False
                )
            )
        )

        cells = base.mark_rect(
            stroke="#151c25",
            strokeWidth=2
        ).encode(
            color=alt.Color(
                "pct_enterprises:Q",
                title="AI adoption (%)",
                scale=alt.Scale(
                    domain=[0, 
                            max(55, float(country["pct_enterprises"].max()))
                            ],
                    range=[
                        "#263547",
                        "#235873",
                        "#0072B2"
                    ]
                )
            )
        )

        labels = base.mark_text(
            color="#FFFFFF",
            fontSize=11
        ).encode(
            text=alt.Text(
                "pct_enterprises:Q",
                format=".2f"
            )
        )

        st.altair_chart(
            (cells + labels).properties(
                title="AI adoption by country and survey year (%)",
                height=max(
                    300,
                    len(order) * 28 + 30
                )
            ),
            width="stretch"
        )

        st.caption(
            "Each cell shows the percentage of enterprises "
            "using AI. The years are separate survey observations; "
            "2022 is not available."
        )

with trend_tab:
    st.subheader(
        f"Country spotlight · {focus_country}"
    )

    history = country[
        country["country"].isin([
            focus_country, "EU27"
        ])
    ].copy()

    history["series"] = history["country"].replace({
        "EU27": "EU27 aggregate"
    })

    focus = history[
        history["country"] == focus_country
    ].sort_values("year")

    if focus.empty:
        st.info("No observations available.")

    else:
        earliest = focus.iloc[0]
        latest = focus.iloc[-1]

        change = float(
            latest["pct_enterprises"]
            - earliest["pct_enterprises"]
        )

        st.markdown(
            f"**{focus_country}** moved from "
            f"**{pct(float(earliest['pct_enterprises']))}** "
            f"in {int(earliest['year'])} to "
            f"**{pct(float(latest['pct_enterprises']))}** "
            f"in {int(latest['year'])}. "
            f"Change: **{change:+.2f} percentage points**."
        )

        chart = alt.Chart(history).encode(
            x=alt.X(
                "year:Q",
                title="Survey year",
                axis=alt.Axis(
                    values=cy_years,
                    format="d"
                ),
                scale=alt.Scale(
                    domain=[
                        cy_years[0],
                        cy_years[-1]
                    ]
                )
            ),
            y=alt.Y(
                "pct_enterprises:Q",
                title="Enterprises using AI (%)",
                scale=alt.Scale(zero=True)
            ),
            color=alt.Color(
                "series:N",
                title="Series",
                scale=alt.Scale(
                    domain=[
                        focus_country,
                        "EU27 aggregate"
                    ],
                    range=[
                        OI["blue"],
                        OI["orange"]
                    ]
                )
            )
        )

        lines = chart.mark_line(
            strokeWidth=3,
            point=True
        )

        labels = chart.mark_text(
            dy=-14,
            fontSize=12
        ).encode(
            text=alt.Text(
                "pct_enterprises:Q",
                format=".2f"
            )
        )

        st.altair_chart(
            (lines + labels).properties(
                title=(
                    f"{focus_country} versus EU27, "
                    f"{cy_years[0]}–{cy_years[-1]}"
                ),
                height=340
            ),
            width="stretch"
        )

        flagged = focus[
            focus["flag"]
            .fillna("")
            .astype(str)
            .str.contains("b")
        ]

        if not flagged.empty:
            flagged_years = ", ".join(
                str(int(y)) for y in flagged["year"]
            )
            st.warning(
                f"Eurostat flags a break in series for "
                f"{focus_country} in {flagged_years}. "
                "Interpret changes cautiously."
            )

        st.caption(
            "Lines connect observed survey years only. "
            "No 2022 observation is available."
        )

st.subheader("What these country data cannot show")

st.caption(
    "Country differences do not establish why firms adopt AI, "
    "whether AI has improved productivity, or whether policies "
    "caused the observed changes. Survey estimates and breaks "
    "in series can affect comparisons."
)

footer(refresh)
