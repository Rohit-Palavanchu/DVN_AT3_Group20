# AI provenance matrix

One row per substantive AI use. Every member must own at least one row, written by them about what they actually did. Each verification must name a check that **could have failed**.

| # | Artefact | Who | Tool | What was asked | What came back | How it was verified (a check that could fail) | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `src/data.py`, `pages/2_Firm_size.py`, first versions of `app.py`, the other pages and the docs templates | Rohit Palavanchu | Claude (Anthropic), claude.ai, Oct–Nov 2026 | Narrow our topic into an arguable question on AI adoption, suggest a four-way split of the app, and write a Streamlit app plus a script to clean the two Eurostat files | A sharper question, a four-page plan, working app and cleaning-script code, and templates for the README, data dictionary and this matrix | I opened the Firm size page and checked the EU large-firm figure for 2025 (55.03%) against `data/raw/isoc_eb_ai.csv`, filtered to "250 persons employed or more", "Enterprises using at least one of the AI technologies", "Percentage of enterprises", EU27, 2025. This would have failed if the script had mapped the size classes wrongly | Matched, so the code was kept. The first version expected Eurostat codes but our download used text labels, so the script was changed to read the labels |
| 2 | Repository check before submission | Rohit Palavanchu | Claude (Anthropic), claude.ai, Nov 2026 | Check the GitHub repo against the 30 marking checks and confirm the app runs from it | Every page ran without errors on a fresh install. Re-running `python -m src.data` gave processed files identical to the committed ones. It found a wording error in this matrix and leftover `__pycache__` files | The regeneration check would have failed if the committed processed files did not match the script's output. They matched exactly, and the wording error was fixed |
| 3 | TO FILL (Member 3) | | | | | | |
| 4 | TO FILL (Member 4) | | | | | | |

Examples of checks that could fail: a value traced to the raw CSV does not match; `python -m src.data` raises a validation error; a chart total disagrees with a hand calculation; a claim on screen is contradicted by a different year or country.
