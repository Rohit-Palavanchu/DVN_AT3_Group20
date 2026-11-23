# AI provenance matrix

One row per substantive AI use. Every member must own at least one row, written by them about what they actually did. Each verification must name a check that **could have failed**.

| # | Artefact | Who | Tool | What was asked | What came back | How it was verified (a check that could fail) | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Question wording, member split, `app.py`, `src/data.py`, docs templates | Member 2 (TO FILL: name) | Claude (Anthropic), claude.ai, Oct 2026 | Sharpen an arguable question on AI adoption; propose a four-way split; build a Streamlit app and transform for Eurostat `isoc_eb_ai` / `isoc_eb_ain2` | A draft question, four section designs, working app and transform code, README / dictionary / matrix templates | Traced the large-firm EU27 latest-year value from the raw CSV (filter `indic_is=E_AI_TANY`, `unit=PC_ENT`, size `GE250`, `geo=EU27_2020`) to the app. This would have failed if the size-code mapping in `src/data.py` were wrong. Result: TO FILL | TO FILL (e.g. accepted; fixed X) |
| 2 | TO FILL (Member 1) | | | | | | |
| 3 | `pages/3_Industries.py` — Industry dashboard | Rohan Stanislaus (Member 3) | ChatGPT (OpenAI), November 2026 | Enhance the Industries section with interactive filters, four chart views, KPI cards, year comparisons, a heatmap, and industry-specific insights while preserving the group application structure. | Revised Streamlit and Altair code for the Industries page, including in-page filters, rankings, comparisons, trends, and explanatory text. | Checked Python syntax, verified 44 industry observations through four automated Eurostat data tests, regenerated processed data, and launched the Streamlit app locally. Confirmed all four chart views rendered. Source cross-check: information and communication increased from 25.37% (2021) to 62.52% (2025), a 37.15 pp change. Incorrect industry, year, or source filters would fail the checks. | Accepted after syntax, data, and visual checks; interactive filter and other-page regression checks pending. |
| 4 | TO FILL (Member 4) | | | | | | |

Examples of checks that could fail: a value traced to the raw CSV does not match; `python -m src.data` raises a validation error; a chart total disagrees with a hand calculation; a claim on screen is contradicted by a different year or country.
