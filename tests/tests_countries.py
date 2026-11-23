import unittest
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from src.data import build

PROCESSED = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
)


class CountryDataTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = pd.read_csv(
            PROCESSED / "adoption_by_country.csv"
        )

    def test_country_year_coverage(self):
        df = self.data

        self.assertEqual(len(df), 112)
        self.assertEqual(df["geo"].nunique(), 28)
        self.assertEqual(
            set(df["year"]),
            {2021, 2023, 2024, 2025}
        )
        self.assertFalse(
            df.duplicated(["geo", "year"]).any()
        )

    def test_2025_summary(self):
        df = self.data[self.data["year"] == 2025]

        members = df[df["geo"] != "EU27_2020"]

        top = members.loc[
            members["pct_enterprises"].idxmax()
        ]
        low = members.loc[
            members["pct_enterprises"].idxmin()
        ]
        eu = df.loc[
            df["geo"] == "EU27_2020",
            "pct_enterprises"
        ].iloc[0]

        self.assertEqual(
            (top["country"], float(top["pct_enterprises"])),
            ("Denmark", 42.03)
        )

        self.assertEqual(
            (low["country"], float(low["pct_enterprises"])),
            ("Romania", 5.21)
        )

        self.assertAlmostEqual(float(eu), 19.95)

        self.assertAlmostEqual(
            float(
                top["pct_enterprises"]
                - low["pct_enterprises"]
            ),
            36.82
        )

    def test_country_eu_deviation(self):
        df = self.data[self.data["year"] == 2025]

        denmark = float(
            df.loc[
                df["country"] == "Denmark",
                "pct_enterprises"
            ].iloc[0]
        )

        eu = float(
            df.loc[
                df["geo"] == "EU27_2020",
                "pct_enterprises"
            ].iloc[0]
        )

        self.assertAlmostEqual(denmark - eu, 22.08)

    def test_country_data_regenerates(self):
        actual = build()["adoption_by_country"]
        expected = self.data

        cols = [
            "geo",
            "country",
            "year",
            "pct_enterprises",
            "flag"
        ]

        actual = (
            actual[cols]
            .fillna("")
            .sort_values(["geo", "year"])
            .reset_index(drop=True)
        )

        expected = (
            expected[cols]
            .fillna("")
            .sort_values(["geo", "year"])
            .reset_index(drop=True)
        )

        assert_frame_equal(
            actual,
            expected,
            check_dtype=False
        )


if __name__ == "__main__":
    unittest.main()
