# Data and AI disclosure statement

## Data

All data come from two public Eurostat datasets, `isoc_eb_ai` and `isoc_eb_ain2` (see `docs/data_dictionary.md`). They are reused under Eurostat's free reuse policy with the source acknowledged. The raw files in `data/raw/` are exactly as downloaded. Every processed file is regenerated from them by `python -m src.data`. No values were entered or edited by hand.

The figures are survey estimates of the share of enterprises using at least one AI technology. They cover firms with 10 or more employees and exclude the financial sector. They measure whether a firm uses AI, not how much it uses it or what effect it had.

## AI use

We used Claude (Anthropic), a large language model, during this project. Its uses are recorded row by row in `docs/ai_provenance.md`. In summary:
- It helped sharpen the research question and propose how to divide the work.
- It wrote the first versions of `app.py`, `src/data.py` and the documentation templates.
- It drafted outline talking points for the Part 1 recordings.

Every number shown in the app is computed from the Eurostat files, not produced by the AI. Each member checked at least one displayed value against the raw CSV and recorded that check in the provenance matrix.

- Rohit Palavanchu: owned the Firm size page and the data cleaning script, set up the GitHub repository and deployment, and checked the large-firm figure against the raw Eurostat file.
- Mohan Krishna: owned the home page and EU trend page.
- Rohan Stanislaus: extended the Industries page with filters, four chart views and a heatmap, and checked industry values against Eurostat.
- Brandon: built the Countries page and four automated data tests, and traced Belgium's values against Eurostat.
