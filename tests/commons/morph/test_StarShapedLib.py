"""
Created on 10 mar. 2025

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
from numpy import isnan, nan
from pandas import Series
from shapely import Polygon, get_parts, get_point
from shapely.wkt import loads
from t4gpd.commons.morph.StarShapedLib import StarShapedLib


class StarShapedLibTest(unittest.TestCase):

    def setUp(self):
        mls = loads(
            "MULTILINESTRING ((0 0, 10 0), (0 0, 0 10), (0 0, -10 0), (0 0, 0 -10))"
        )
        self.duos = [
            (
                loads("MULTILINESTRING (EMPTY)"),
                {
                    "min_raylen": nan,
                    "avg_raylen": nan,
                    "std_raylen": nan,
                    "max_raylen": nan,
                    "med_raylen": nan,
                    "entropy": nan,
                    "drift": nan,
                },
            ),
            (
                mls,
                {
                    "min_raylen": 10.0,
                    "avg_raylen": 10.0,
                    "std_raylen": 0.0,
                    "max_raylen": 10.0,
                    "med_raylen": 10.0,
                    "entropy": 0.0,
                    "drift": 0.0,
                },
            ),
            (
                Polygon(get_point(get_parts(mls), 1)),
                {
                    "min_raylen": nan,
                    "avg_raylen": nan,
                    "std_raylen": nan,
                    "max_raylen": nan,
                    "med_raylen": nan,
                    "entropy": nan,
                    "drift": nan,
                },
            ),
        ]

    def tearDown(self):
        pass

    def testIndices(self):
        for geom, expected in self.duos:
            geom = Series(geom, index=["geometry"])
            actual = StarShapedLib._indices(
                geom, precision=1.0, base=2, with_geom=False
            )
            for indice in [
                "min_raylen",
                "avg_raylen",
                "std_raylen",
                "max_raylen",
                "med_raylen",
                "entropy",
                "drift",
            ]:
                if isnan(expected[indice]):
                    self.assertTrue(isnan(actual[indice]), f"Test {indice}")
                else:
                    self.assertAlmostEqual(
                        expected[indice], actual[indice], None, f"Test {indice}", 1e-3
                    )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
