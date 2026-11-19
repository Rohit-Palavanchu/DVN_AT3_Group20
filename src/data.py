"""Transform the two Eurostat source files into the tidy tables the app reads.

Sources (Eurostat data browser, "linear" CSV download with labels):
  data/raw/isoc_eb_ai.csv    Artificial intelligence by size class of enterprise
  data/raw/isoc_eb_ain2.csv  Artificial intelligence by NACE Rev.2 activity (default view)

Outputs (data/processed/):
  adoption_by_size.csv     EU27 and each country, by size class and year
  adoption_by_country.csv  EU27 member states + EU27, all enterprises (10+), by year
  adoption_by_sector.csv   EU27, by economic activity and year
  refresh.csv              Eurostat last-update date and latest year per source

Run:  python -m src.data
Every output is rebuilt from the raw files; no values are edited by hand.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# Indicator E_AI_TANY and unit PC_ENT, as they appear in the labelled download.
INDICATOR_PREFIX = "Enterprises using at least one of the AI technologies"
UNIT = "Percentage of enterprises"
EU_LABEL = "European Union - 27 countries (from 2020)"
ALL_10 = "10 persons employed or more"
ALL_ACTIVITIES_PREFIX = "All activities"

SIZE_LABELS = {
    "10 persons employed or more": "All (10+)",
    "From 10 to 49 persons employed": "Small (10-49)",
    "From 50 to 249 persons employed": "Medium (50-249)",
    "250 persons employed or more": "Large (250+)",
}

# Eurostat geo label -> (code, short name). EU27 member states plus the EU aggregate;
# candidate and EFTA countries are kept in the size table but not in the EU comparison.
GEO = {
    EU_LABEL: ("EU27_2020", "EU27"),
    "Belgium": ("BE", "Belgium"), "Bulgaria": ("BG", "Bulgaria"), "Czechia": ("CZ", "Czechia"),
    "Denmark": ("DK", "Denmark"), "Germany": ("DE", "Germany"), "Estonia": ("EE", "Estonia"),
    "Ireland": ("IE", "Ireland"), "Greece": ("EL", "Greece"), "Spain": ("ES", "Spain"),
    "France": ("FR", "France"), "Croatia": ("HR", "Croatia"), "Italy": ("IT", "Italy"),
    "Cyprus": ("CY", "Cyprus"), "Latvia": ("LV", "Latvia"), "Lithuania": ("LT", "Lithuania"),
    "Luxembourg": ("LU", "Luxembourg"), "Hungary": ("HU", "Hungary"), "Malta": ("MT", "Malta"),
    "Netherlands": ("NL", "Netherlands"), "Austria": ("AT", "Austria"), "Poland": ("PL", "Poland"),
    "Portugal": ("PT", "Portugal"), "Romania": ("RO", "Romania"), "Slovenia": ("SI", "Slovenia"),
    "Slovakia": ("SK", "Slovakia"), "Finland": ("FI", "Finland"), "Sweden": ("SE", "Sweden"),
    "Norway": ("NO", "Norway"), "Serbia": ("RS", "Serbia"), "Türkiye": ("TR", "Türkiye"),
    "Bosnia and Herzegovina": ("BA", "Bosnia and Herzegovina"), "Montenegro": ("ME", "Montenegro"),
    "North Macedonia": ("MK", "North Macedonia"), "Albania": ("AL", "Albania"),
}
NON_EU = {"NO", "RS", "TR", "BA", "ME", "MK", "AL"}

SECTOR_LABELS = {
    "Information and communication": "Information and communication",
    "Professional, scientific and technical activities": "Professional, scientific and technical",
    "Electricity, gas, steam and air conditioning supply": "Electricity and gas supply",
    "Real estate activities": "Real estate",
    "Administrative and support service activities": "Administrative and support services",
    "Wholesale and retail trade; repair of motor vehicles and motorcycles": "Wholesale and retail trade",
    "Manufacturing": "Manufacturing",
    "Water supply; sewerage, waste management and remediation activities": "Water supply and waste",
    "Accommodation and food service activities": "Accommodation and food",
    "Transportation and storage": "Transport and storage",
    "Construction": "Construction",
}


def read_raw(name: str) -> pd.DataFrame:
    path = RAW / name
    if not path.exists():
        sys.exit(f"Missing {path}. Download it from the Eurostat data browser (see docs/data_dictionary.md).")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    needed = {"LAST UPDATE", "size_emp", "nace_r2", "indic_is", "unit", "geo",
              "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"{name}: missing columns {sorted(missing)}")
    keep = df["indic_is"].str.startswith(INDICATOR_PREFIX) & (df["unit"] == UNIT)
    if not keep.any():
        raise ValueError(f"{name}: no rows for indicator '{INDICATOR_PREFIX}' with unit '{UNIT}'")
    out = df[keep].copy()
    out["year"] = out["TIME_PERIOD"].astype(int)
    out["value"] = pd.to_numeric(out["OBS_VALUE"].replace("", None), errors="coerce")
    out = out.dropna(subset=["value"])
    out.attrs["last_update"] = df["LAST UPDATE"].max()
    return out


def build() -> dict[str, pd.DataFrame]:
    ai = read_raw("isoc_eb_ai.csv")
    ai_updated = ai.attrs["last_update"]
    ai = ai[ai["nace_r2"].str.startswith(ALL_ACTIVITIES_PREFIX) & ai["geo"].isin(GEO)
            & ai["size_emp"].isin(SIZE_LABELS)].copy()
    ai["geo_code"] = ai["geo"].map(lambda g: GEO[g][0])
    ai["country"] = ai["geo"].map(lambda g: GEO[g][1])
    ai["size_class"] = ai["size_emp"].map(SIZE_LABELS)
    by_size = (ai[["geo_code", "country", "size_class", "year", "value", "OBS_FLAG"]]
               .rename(columns={"geo_code": "geo", "value": "pct_enterprises", "OBS_FLAG": "flag"})
               .sort_values(["geo", "size_class", "year"]).reset_index(drop=True))
    by_country = (by_size[(by_size["size_class"] == "All (10+)") & ~by_size["geo"].isin(NON_EU)]
                  .drop(columns="size_class").reset_index(drop=True))

    sec = read_raw("isoc_eb_ain2.csv")
    sec_updated = sec.attrs["last_update"]
    sec = sec[(sec["geo"] == EU_LABEL) & (sec["size_emp"] == ALL_10)
              & sec["nace_r2"].isin(SECTOR_LABELS)].copy()
    sec["sector"] = sec["nace_r2"].map(SECTOR_LABELS)
    by_sector = (sec[["sector", "nace_r2", "year", "value", "OBS_FLAG"]]
                 .rename(columns={"nace_r2": "nace_label", "value": "pct_enterprises", "OBS_FLAG": "flag"})
                 .sort_values(["sector", "year"]).reset_index(drop=True))

    refresh = pd.DataFrame([
        {"dataset": "isoc_eb_ai", "eurostat_last_update": ai_updated, "latest_year": int(by_size["year"].max())},
        {"dataset": "isoc_eb_ain2", "eurostat_last_update": sec_updated, "latest_year": int(by_sector["year"].max())},
    ])
    return {"adoption_by_size": by_size, "adoption_by_country": by_country,
            "adoption_by_sector": by_sector, "refresh": refresh}


def validate(t: dict[str, pd.DataFrame]) -> None:
    keys = {"adoption_by_size": ["geo", "size_class", "year"],
            "adoption_by_country": ["geo", "year"],
            "adoption_by_sector": ["sector", "year"]}
    for name, key in keys.items():
        df = t[name]
        if df.empty:
            raise ValueError(f"{name} is empty")
        if df.duplicated(key).any():
            raise ValueError(f"{name}: duplicate rows for key {key}")
        if not df["pct_enterprises"].between(0, 100).all():
            raise ValueError(f"{name}: a percentage lies outside 0-100")
    eu = t["adoption_by_size"].query("geo == 'EU27_2020'")
    if set(eu["size_class"]) != set(SIZE_LABELS.values()):
        raise ValueError("EU27 is missing a size class")
    if len(t["adoption_by_sector"]["sector"].unique()) != len(SECTOR_LABELS):
        raise ValueError("A sector is missing from the EU27 sector table")


def main() -> None:
    tables = build()
    validate(tables)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
        years = f", years {df['year'].min()}-{df['year'].max()}" if "year" in df else ""
        print(f"wrote {name}.csv: {len(df)} rows{years}")


if __name__ == "__main__":
    main()
