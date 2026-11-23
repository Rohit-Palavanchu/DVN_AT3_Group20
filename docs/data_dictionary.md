# Data dictionary

All figures are Eurostat survey estimates from the *ICT usage and e-commerce in enterprises* survey. Coverage: enterprises with 10 or more employees and self-employed persons, excluding the financial sector (NACE K).

Licence for both sources: Eurostat data may be reused free of charge with the source acknowledged (Commission Decision 2011/833/EU; European Commission reuse policy, CC BY 4.0).

> Fill in the download date (`TO FILL`) with the day you downloaded the files.

## Source samples (`data/raw/`)

### `isoc_eb_ai.csv`: Artificial intelligence by size class of enterprise

| Field | Value |
| --- | --- |
| Publisher | Eurostat |
| URL | https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table |
| Format | Linear CSV with labels, full dataset, from the Eurostat data browser (72,527 rows) |
| Downloaded | 25 OCT |
| Eurostat last update | 15 June 2026 (`LAST UPDATE` = 15/06/26 11:00:00) |
| Primary key | `freq`, `size_emp`, `nace_r2`, `indic_is`, `unit`, `geo`, `TIME_PERIOD` |
| Time coverage | Survey years 2021, 2023, 2024, 2025 (no 2022 survey of this indicator) |
| Latest observation | 2025 |
| Columns used | `size_emp`, `nace_r2` (all activities only), `indic_is`, `unit`, `geo`, `TIME_PERIOD`, `OBS_VALUE` (% of enterprises), `OBS_FLAG`, `LAST UPDATE` |

### `isoc_eb_ain2.csv`: Artificial intelligence by NACE Rev.2 activity

| Field | Value |
| --- | --- |
| Publisher | Eurostat |
| URL | https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ain2/default/table |
| Format | Linear CSV with labels, default view (5,159 rows) |
| Downloaded | TO FILL |
| Eurostat last update | 15 June 2026 |
| Primary key | `freq`, `size_emp`, `nace_r2`, `indic_is`, `unit`, `geo`, `TIME_PERIOD` |
| Time coverage | Survey years 2021, 2023, 2024, 2025 |
| Latest observation | 2025 |
| Columns used | `nace_r2`, `size_emp` (10+ only), `indic_is`, `unit`, `geo` (EU27 only), `TIME_PERIOD`, `OBS_VALUE` (% of enterprises), `OBS_FLAG` |

## Processed files (`data/processed/`), produced by `python -m src.data`

The transform (`src/data.py`) does the following, in order:
1. Keeps rows where `indic_is` starts with "Enterprises using at least one of the AI technologies" (Eurostat code E_AI_TANY) and `unit` is "Percentage of enterprises".
2. Drops empty or confidential values.
3. Maps Eurostat labels to short labels: size classes, industry names, and country names with their two-letter codes.
4. Validates that every value lies between 0 and 100, that there are no duplicate keys, and that the EU27 has all size classes and all 11 industries.

No values are rescaled or edited. The app displays them to two decimals, exactly as published.

### `adoption_by_size.csv`

| Column | Type | Unit / meaning |
| --- | --- | --- |
| `geo` | string | Eurostat country code (`EU27_2020` for the EU) |
| `country` | string | Country name |
| `size_class` | string | `All (10+)`, `Small (10-49)`, `Medium (50-249)`, `Large (250+)` employees |
| `year` | integer | Survey year |
| `pct_enterprises` | number | % of enterprises in that size class using at least one AI technology |
| `flag` | string | Eurostat observation flag (e.g. `b` break in series, `u` low reliability) |

Primary key: `geo`, `size_class`, `year`. Source: `isoc_eb_ai.csv`.

### `adoption_by_country.csv`

This is the subset of `adoption_by_size.csv` with `size_class == "All (10+)"`, covering the 27 EU member states plus the EU27 aggregate (28 geographies × 4 years = 112 rows). It has the same columns, without `size_class`. Primary key: `geo`, `year`.

### `adoption_by_sector.csv`

| Column | Type | Unit / meaning |
| --- | --- | --- |
| `sector` | string | Readable industry label |
| `nace_label` | string | Eurostat NACE Rev.2 activity label |
| `year` | integer | Survey year |
| `pct_enterprises` | number | % of enterprises in that industry using at least one AI technology (EU27) |
| `flag` | string | Eurostat observation flag |

Primary key: `sector`, `year`. Source: `isoc_eb_ain2.csv`, filtered to `geo == EU27_2020`.

### `refresh.csv`

One row per source dataset, with the Eurostat `LAST UPDATE` date and the latest survey year. The app shows these on screen as the last data refresh.
