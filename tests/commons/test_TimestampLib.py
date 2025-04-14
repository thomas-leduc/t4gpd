"""
Created on 14 Apr. 2025

@author: tleduc

Copyright 2020-2025 Thomas Leduc

This file is part of t4gpd.

t4gpd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

t4gpd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with t4gpd.  If not, see <https://www.gnu.org/licenses/>.
"""

import unittest
from datetime import timedelta, timezone
from pandas import Series, Timedelta, Timestamp
from pandas.api.types import is_datetime64_any_dtype
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.TimestampLib import TimestampLib


class TimestampLibTest(unittest.TestCase):

    def setUp(self):
        self.dts = [Timestamp(f"2025-{month}-21") for month in (3, 6, 12)]
        self.days = [dt.date() for dt in self.dts]
        self.gdf = LatLonLib.NANTES

    def tearDown(self):
        pass

    def testFrom_d0_to_d1_using_freq(self):
        trios = [
            (None, None, "1h"),
            (None, Timestamp("2025-01-21"), "6h"),
            (Timestamp("2025-03-21"), None, "6h"),
            (Timestamp("2025-06-21 10:00"), Timestamp("2025-06-21 14:00"), "1h"),
            (
                Timestamp("2025-09-21 16:00"),
                Timestamp("2025-09-21 19:00"),
                Timedelta("2h"),
            ),
            (
                Timestamp("2025-12-21 16:00"),
                Timestamp("2025-12-21 19:00"),
                timedelta(hours=2),
            ),
        ]
        actual = TimestampLib.from_d0_to_d1_using_freq(trios)
        self.assertIsInstance(actual, Series, "Is a Series")
        self.assertTrue(is_datetime64_any_dtype(actual), "Is a datetime Series")
        self.assertEqual(actual.dt.tz, timezone.utc, "Is UTC")

        pairs = [
            ("2025-01-21", 1),
            ("2025-03-21", 4),
            ("2025-06-21", 5),
            ("2025-09-21", 2),
            ("2025-12-21", 2),
        ]
        for day, count in pairs:
            self.assertEqual(
                count,
                len(actual[actual.dt.normalize() == Timestamp(day, tz="UTC")]),
                f"Count rows ({day})",
            )

    def testFrom_daystart_to_dayoff(self):
        actual = TimestampLib.from_daystart_to_dayoff(self.dts, freq="1h")

        self.assertIsInstance(actual, Series, "Is a Series")
        self.assertTrue(is_datetime64_any_dtype(actual), "Is a datetime Series")
        self.assertEqual(actual.dt.tz, timezone.utc, "Is UTC")
        self.assertTrue(
            all([dt.date() in self.days for dt in actual]),
            "All dates are in the day list",
        )
        self.assertEqual(3 * 24, len(actual), "Count rows")

    def testFrom_sunrise_to_sunset(self):
        actual = TimestampLib.from_sunrise_to_sunset(self.gdf, self.dts, freq="1h")

        self.assertIsInstance(actual, Series, "Is a Series")
        self.assertTrue(is_datetime64_any_dtype(actual), "Is a datetime Series")
        self.assertEqual(actual.dt.tz, timezone.utc, "Is UTC")
        self.assertTrue(
            all([dt.date() in self.days for dt in actual]),
            "All dates are in the day list",
        )
        self.assertEqual(12 + 16 + 9, len(actual), "Count rows")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
