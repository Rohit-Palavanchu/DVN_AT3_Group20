# AI provenance matrix

One row per substantive AI use. Every member must own at least one row, written by them about what they actually did. Each verification must name a check that **could have failed**.

| # | Artefact | Who | Tool | What was asked | What came back | How it was verified (a check that could fail) | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Question wording, member split, `app.py`, `src/data.py`, docs templates | Member 2 (TO FILL: name) | Claude (Anthropic), claude.ai, Oct 2026 | Sharpen an arguable question on AI adoption; propose a four-way split; build a Streamlit app and transform for Eurostat `isoc_eb_ai` / `isoc_eb_ain2` | A draft question, four section designs, working app and transform code, README / dictionary / matrix templates | Traced the large-firm EU27 latest-year value from the raw CSV (filter `indic_is=E_AI_TANY`, `unit=PC_ENT`, size `GE250`, `geo=EU27_2020`) to the app. This would have failed if the size-code mapping in `src/data.py` were wrong. Result: TO FILL | TO FILL (e.g. accepted; fixed X) |
| 2 | TO FILL (Member 1) | | | | | | |
| 3 | TO FILL (Member 3) | | | | | | |
| 4 | TO FILL (Member 4) | | | | | | |

Examples of checks that could fail: a value traced to the raw CSV does not match; `python -m src.data` raises a validation error; a chart total disagrees with a hand calculation; a claim on screen is contradicted by a different year or country.
