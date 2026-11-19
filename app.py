"""Who has adopted AI? Home page: question, persona, headline facts and our answer.

Run:  streamlit run app.py   (after  python -m src.data  has built data/processed/)
Each section is its own page in pages/, owned by one group member.
"""

from __future__ import annotations

import altair as alt
import streamlit as st

from src.common import OI, SIZE_COLOURS, SIZE_DASH, SIZE_ORDER, footer, pct, setup

from src.common import QUESTION, SOURCE_LINE

size, country, sector, refresh, eu_all, years = setup("Who has adopted AI?")
first_year, last_year = years[0], years[-1]
eu_first = float(eu_all.iloc[0]["pct_enterprises"])
eu_last = float(eu_all.iloc[-1]["pct_enterprises"])

# ---------------------------------------------------------------- opening screen
st.title("Who has adopted AI?")
st.markdown(f"**Our question:** {QUESTION}")
st.markdown(
    "**Who this is for:** Maya, a policy adviser at a small-business association, deciding "
    "whether small firms need targeted support to adopt AI."
)
c1, c2, c3 = st.columns(3)
c1.metric(f"EU firms using AI, {last_year}", pct(eu_last),
          f"{eu_last - eu_first:+.2f} points since {first_year}", delta_color="off")
large = size.query("geo == 'EU27_2020' and size_class == 'Large (250+)' and year == @last_year")
small = size.query("geo == 'EU27_2020' and size_class == 'Small (10-49)' and year == @last_year")
if not large.empty and not small.empty:
    c2.metric(f"Large vs small firms, {last_year}",
              f"{pct(large.iloc[0]['pct_enterprises'])} vs {pct(small.iloc[0]['pct_enterprises'])}")
cy_last = country.query("year == @last_year and geo != 'EU27_2020'").sort_values("pct_enterprises")
if not cy_last.empty:
    c3.metric(f"Country range, {last_year}",
              f"{pct(cy_last.iloc[0]['pct_enterprises'])} to {pct(cy_last.iloc[-1]['pct_enterprises'])}",
              f"{cy_last.iloc[0]['country']} to {cy_last.iloc[-1]['country']}", delta_color="off")

# ---------------------------------------------------------------- answer
with st.container(border=True):
    st.subheader("Our answer")
    ratio = (large.iloc[0]["pct_enterprises"] / small.iloc[0]["pct_enterprises"]
             if not large.empty and not small.empty else float("nan"))
    sec_last = sector[sector["year"] == sector["year"].max()].sort_values("pct_enterprises")
    sec_txt = (f"{sec_last.iloc[-1]['sector']} ({pct(sec_last.iloc[-1]['pct_enterprises'])}) was "
               f"{sec_last.iloc[-1]['pct_enterprises'] / sec_last.iloc[0]['pct_enterprises']:.1f} times the rate in "
               f"{sec_last.iloc[0]['sector'].lower()} ({pct(sec_last.iloc[0]['pct_enterprises'])})"
               if len(sec_last) >= 2 else "sector data were unavailable")
    cy_txt = (f"{cy_last.iloc[-1]['country']} ({pct(cy_last.iloc[-1]['pct_enterprises'])}) was "
              f"{cy_last.iloc[-1]['pct_enterprises'] / cy_last.iloc[0]['pct_enterprises']:.1f} times the rate in "
              f"{cy_last.iloc[0]['country']} ({pct(cy_last.iloc[0]['pct_enterprises'])})"
              if len(cy_last) >= 2 else "country data were unavailable")
    st.markdown(
        f"Across the EU, adoption grew from {pct(eu_first)} of EU firms in {first_year} to "
        f"{pct(eu_last)} in {last_year}. **But it is not broad-based yet.** In {last_year}, large firms "
        f"were {ratio:.1f} times as likely as small firms to use AI; {sec_txt}; and {cy_txt}. "
        "Growth is widespread, but the level of adoption is still concentrated. Someone focused on "
        "growth rates could reasonably call this a broad boom, which is why we show both."
    )

st.caption(SOURCE_LINE)

st.markdown(
    "**Explore the four sections in the sidebar:**\n"
    "1. How fast has adoption grown across the EU?\n"
    "2. Are small firms keeping up?\n"
    "3. Which industries have adopted AI?\n"
    "4. Which countries lead and which lag?"
)
footer(refresh, limits=True)
