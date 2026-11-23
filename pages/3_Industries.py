"""Member 3: industry adoption intelligence, grounded in Eurostat survey observations."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.common import OI, footer, pct, setup

size, country, sector, refresh, eu_all, years = setup("Who has adopted AI?")

SURVEY_YEARS = sorted(int(y) for y in sector["year"].unique())
FIRST_YEAR, LATEST_YEAR = SURVEY_YEARS[0], SURVEY_YEARS[-1]
ALL_INDUSTRIES = sorted(sector["sector"].unique())
LABEL_COLOR = "#F5F5F5"

st.caption("Who has adopted AI? / Industries")
st.header("3 · Which industries have adopted AI?")
st.markdown(
    "**The story:** AI adoption is increasing across European industries, but the level of "
    "adoption remains very uneven. Explore the leaders, compare survey years, and investigate "
    "the industries that might benefit from further research into adoption barriers."
)
st.caption(
    f"**Source:** Eurostat `isoc_eb_ain2` · **Region:** EU27 · **Measure:** % of "
    f"enterprises with 10+ persons employed using at least one AI technology · "
    f"**Survey years:** {', '.join(str(y) for y in SURVEY_YEARS)} (no 2022 observation). "
    "Financial services excluded. Industry percentages have different denominators and do not add to 100%."
)


def latest_values(industries: list[str]) -> pd.DataFrame:
    return sector[
        (sector["year"] == LATEST_YEAR) & sector["sector"].isin(industries)
    ].sort_values("pct_enterprises", ascending=False)


def adoption_scale(values: pd.DataFrame) -> alt.Scale:
    maximum = float(values["pct_enterprises"].max())
    return alt.Scale(domain=[0, min(100, maximum + 14)])


def industry_axis(order: list[str]) -> alt.Y:
    return alt.Y(
        "sector:N",
        sort=order,
        title=None,
        axis=alt.Axis(labelLimit=315, labelFontSize=12, labelOverlap=False),
    )


def industry_selector(label: str, key: str) -> list[str]:
    return st.multiselect(
        label,
        ALL_INDUSTRIES,
        default=ALL_INDUSTRIES,
        key=key,
        help="Select the industries relevant to your comparison. Clear all to test the empty state.",
    )


def show_empty() -> None:
    st.info("No industries selected. Choose at least one industry above to display results.")


overview, comparison_tab, heatmap_tab, spotlight_tab = st.tabs(
    ["Overview & ranking", "Compare years", "Adoption heatmap", "Industry spotlight"],
    on_change="rerun",
    key="industry_active_tab",
)

with overview:
    st.subheader(f"Industry leaders and laggards · {LATEST_YEAR}")
    with st.expander("Choose industries for this ranking", expanded=False):
        ranking_selected = industry_selector("Industries in ranking", "industry_ranking_selected")
    ranking = latest_values(ranking_selected)
    if ranking.empty:
        show_empty()
    else:
        order = ranking["sector"].tolist()
        highest, lowest = ranking.iloc[0], ranking.iloc[-1]
        wide = sector[sector["sector"].isin(ranking_selected)].pivot(
            index="sector", columns="year", values="pct_enterprises"
        )
        gains = (wide[LATEST_YEAR] - wide[FIRST_YEAR]).dropna().sort_values(ascending=False)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Highest adoption", pct(float(highest["pct_enterprises"])))
            st.caption(highest["sector"])
        with k2:
            st.metric("Lowest adoption", pct(float(lowest["pct_enterprises"])))
            st.caption(lowest["sector"])
        with k3:
            st.metric("Adoption gap", f"{float(highest['pct_enterprises']-lowest['pct_enterprises']):.2f} pp")
            st.caption("Highest minus lowest, percentage points")
        with k4:
            if gains.empty:
                st.metric("Largest gain", "N/A")
                st.caption("No comparable observations")
            else:
                st.metric(f"Largest gain, {FIRST_YEAR}–{LATEST_YEAR}", f"{float(gains.iloc[0]):+.2f} pp")
                st.caption(gains.index[0])

        chart = alt.Chart(ranking).encode(
            y=industry_axis(order),
            x=alt.X(
                "pct_enterprises:Q",
                title="Enterprises using at least one AI technology (%)",
                scale=adoption_scale(ranking),
            ),
        )
        bars = chart.mark_bar(size=21, color=OI["blue"])
        labels = chart.mark_text(align="left", dx=8, fontSize=12, color=LABEL_COLOR).encode(
            text=alt.Text("pct_enterprises:Q", format=".2f")
        )
        st.altair_chart(
            (bars + labels).properties(
                title=f"EU27 adoption by industry, {LATEST_YEAR} (%)",
                height=max(310, len(order) * 37),
            ),
            width="stretch",
        )
        st.caption(
            "**Visual Vocabulary — ranking.** Bars show adoption rates within each industry. "
            "The percentages are printed so they can be read without hovering."
        )
        st.markdown(
            f"**Finding:** Among the {len(ranking)} selected industries, "
            f"**{highest['sector']}** reported **{pct(float(highest['pct_enterprises']))}** "
            f"adoption, versus **{pct(float(lowest['pct_enterprises']))}** in "
            f"**{lowest['sector']}**, in {LATEST_YEAR}."
        )

with comparison_tab:
    st.subheader("How much has adoption changed?")
    st.caption("Select an earlier year and industries here; the comparison updates directly below.")
    compare_year = st.radio(
        f"Compare {LATEST_YEAR} against",
        [y for y in SURVEY_YEARS if y != LATEST_YEAR],
        index=0,
        horizontal=True,
        key="industry_compare_year",
    )
    with st.expander("Choose industries for comparison", expanded=False):
        compare_selected = industry_selector("Industries to compare", "industry_compare_selected")
    selected_latest = latest_values(compare_selected)
    selected_comparison = sector[
        sector["year"].isin([compare_year, LATEST_YEAR])
        & sector["sector"].isin(compare_selected)
    ].copy()
    if selected_latest.empty or selected_comparison.empty:
        show_empty()
    else:
        order = selected_latest["sector"].tolist()
        selected_comparison["year_label"] = selected_comparison["year"].astype(str)
        common_x = alt.X(
            "pct_enterprises:Q",
            title="Enterprises using at least one AI technology (%)",
            scale=adoption_scale(selected_latest),
        )
        common_y = industry_axis(order)
        base = alt.Chart(selected_comparison).encode(x=common_x, y=common_y)
        connectors = base.mark_line(strokeWidth=2, color="#A0A0A0").encode(detail="sector:N")
        dots = base.mark_point(filled=True, size=120).encode(
            color=alt.Color(
                "year_label:N",
                title="Survey year",
                scale=alt.Scale(
                    domain=[str(compare_year), str(LATEST_YEAR)],
                    range=[OI["sky"], OI["vermillion"]],
                ),
                legend=alt.Legend(orient="top"),
            ),
            shape=alt.Shape(
                "year_label:N",
                scale=alt.Scale(
                    domain=[str(compare_year), str(LATEST_YEAR)],
                    range=["circle", "diamond"],
                ),
                legend=None,
            ),
        )
        prior_labels = alt.Chart(selected_comparison[selected_comparison["year"] == compare_year]).mark_text(
            dy=-13, fontSize=11, color=LABEL_COLOR
        ).encode(x=common_x, y=common_y, text=alt.Text("pct_enterprises:Q", format=".2f"))
        latest_labels = alt.Chart(selected_comparison[selected_comparison["year"] == LATEST_YEAR]).mark_text(
            dy=15, fontSize=11, color=LABEL_COLOR, fontWeight="bold"
        ).encode(x=common_x, y=common_y, text=alt.Text("pct_enterprises:Q", format=".2f"))
        st.altair_chart(
            (connectors + dots + prior_labels + latest_labels).properties(
                title=f"AI adoption by industry: {compare_year} versus {LATEST_YEAR} (%)",
                height=max(380, len(order) * 43),
            ),
            width="stretch",
        )
        st.caption(
            "**Visual Vocabulary — change.** Blue circles represent the earlier year; "
            f"orange diamonds represent {LATEST_YEAR}. Each value is labelled directly."
        )
        leader = "Information and communication"
        subset = selected_comparison[selected_comparison["sector"] == leader].set_index("year")
        if compare_year in subset.index and LATEST_YEAR in subset.index:
            previous = float(subset.loc[compare_year, "pct_enterprises"])
            current = float(subset.loc[LATEST_YEAR, "pct_enterprises"])
            st.markdown(
                f"**Example:** {leader} moved from **{pct(previous)}** in {compare_year} "
                f"to **{pct(current)}** in {LATEST_YEAR} "
                f"(**{current-previous:+.2f} percentage points**)."
            )

with heatmap_tab:
    st.subheader("Across all survey years")
    st.caption("Choose industries here to explore all four survey observations in one view.")
    with st.expander("Choose industries for the heatmap", expanded=False):
        heat_selected = industry_selector("Industries in heatmap", "industry_heatmap_selected")
    heat_latest = latest_values(heat_selected)
    heat_data = sector[sector["sector"].isin(heat_selected)].copy()
    if heat_latest.empty:
        show_empty()
    else:
        heat_data["survey_year"] = heat_data["year"].astype(str)
        heat_base = alt.Chart(heat_data).encode(
            x=alt.X(
                "survey_year:O",
                sort=[str(y) for y in SURVEY_YEARS],
                title="Survey year",
                axis=alt.Axis(labelAngle=0),
            ),
            y=industry_axis(heat_latest["sector"].tolist()),
        )
        cells = heat_base.mark_rect(stroke="#101820", strokeWidth=3).encode(
            color=alt.Color(
                "pct_enterprises:Q",
                title="AI adoption (%)",
                scale=alt.Scale(
                    domain=[0, max(70, int(sector["pct_enterprises"].max() + 10))],
                    range=["#263547", "#235873", "#0B6A8B", "#0072B2"],
                ),
            ),
            tooltip=[
                alt.Tooltip("sector:N", title="Industry"),
                alt.Tooltip("year:O", title="Survey year"),
                alt.Tooltip("pct_enterprises:Q", title="Adoption (%)", format=".2f"),
            ],
        )
        values = heat_base.mark_text(color=LABEL_COLOR, fontSize=12, fontWeight="bold").encode(
            text=alt.Text("pct_enterprises:Q", format=".2f")
        )
        st.altair_chart(
            (cells + values).properties(
                title="EU27 adoption by industry and survey year (%)",
                height=max(320, len(heat_latest) * 36),
            ),
            width="stretch",
        )
        st.caption(
            "**Visual Vocabulary — magnitude / heatmap.** Each cell is labelled. "
            "There is no observation for 2022; these are separate survey years, not a complete annual series."
        )

with spotlight_tab:
    st.subheader("Explore one industry")
    st.caption("Choose an industry here to update its trend and ranking below.")
    focus_sector = st.selectbox(
        "Industry spotlight",
        ALL_INDUSTRIES,
        index=ALL_INDUSTRIES.index("Information and communication")
        if "Information and communication" in ALL_INDUSTRIES else 0,
        key="industry_spotlight_sector",
    )
    focus = sector[sector["sector"] == focus_sector].sort_values("year")
    latest_focus = focus[focus["year"] == LATEST_YEAR]
    if latest_focus.empty:
        st.info("No observations are available for that industry.")
    else:
        now = float(latest_focus.iloc[0]["pct_enterprises"])
        all_latest = latest_values(ALL_INDUSTRIES)
        rank = int((all_latest["pct_enterprises"] > now).sum() + 1)
        first_focus = focus[focus["year"] == FIRST_YEAR]
        statement = f"**{focus_sector}** ranked **{rank} of {len(all_latest)}** industries in {LATEST_YEAR}, at **{pct(now)}**."
        if not first_focus.empty:
            previous = float(first_focus.iloc[0]["pct_enterprises"])
            statement += f" Its change since {FIRST_YEAR} was **{now-previous:+.2f} percentage points**."
        st.markdown(statement)
        x = alt.X(
            "year:Q", title="Survey year",
            scale=alt.Scale(domain=[FIRST_YEAR, LATEST_YEAR]),
            axis=alt.Axis(values=SURVEY_YEARS, format="d"),
        )
        y = alt.Y(
            "pct_enterprises:Q", title="Enterprises using AI (%)",
            scale=alt.Scale(domain=[0, min(100, max(15, now + 14))]),
        )
        line_base = alt.Chart(focus).encode(x=x, y=y)
        line = line_base.mark_line(color=OI["sky"], strokeWidth=3)
        points = line_base.mark_point(filled=True, color=OI["vermillion"], size=135, shape="diamond")
        labels = line_base.mark_text(color=LABEL_COLOR, dy=-17, fontWeight="bold", fontSize=12).encode(
            text=alt.Text("pct_enterprises:Q", format=".2f")
        )
        st.altair_chart(
            (line + points + labels).properties(
                title=f"{focus_sector}: reported AI adoption by survey year (%)", height=290
            ),
            width="stretch",
        )
        st.caption(
            "The timeline uses the actual survey-year intervals. Connecting lines do not imply "
            "that the missing years were measured."
        )
        with st.container(border=True):
            st.markdown("**What this means for policy**")
            st.write(
                f"A reported adoption rate of {pct(now)} for {focus_sector.lower()} "
                "can guide further investigation, but does not establish why firms adopt AI, "
                "whether adoption improves productivity, or which intervention would work."
            )

st.caption(
    "**Limits of interpretation:** These are survey-based adoption rates, not numbers of firms, "
    "AI intensity, productivity or causal effects. Cross-year comparisons may be affected by "
    "changes in survey definitions or breaks in series."
)
footer(refresh)
