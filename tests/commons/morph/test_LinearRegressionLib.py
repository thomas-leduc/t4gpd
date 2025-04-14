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
from shapely.wkt import loads
from t4gpd.commons.morph.LinearRegressionLib import LinearRegressionLib


class LinearRegressionLibTest(unittest.TestCase):

    def setUp(self):
        mpts = loads("MULTIPOINT ((10 20), (20 30), (30 20), (40 40), (50 70))")
        self.duos = [
            (
                loads("MULTIPOINT (EMPTY)"),
                {
                    "slope": nan,
                    "intercept": nan,
                    "score": nan,
                    "mae": nan,
                    "mse": nan,
                },
            ),
            (
                mpts,
                {
                    "slope": 1.1,
                    "intercept": 3.0,
                    "score": 0.703,
                    "mae": 9.2,
                    "mse": 102.0,
                },
            ),
        ]

    def tearDown(self):
        pass

    def testIndices(self):
        for geom, expected in self.duos:
            geom = Series(geom, index=["geometry"])
            actual = LinearRegressionLib._indices(geom, with_geom=False)
            for indice in [
                "slope",
                "intercept",
                "score",
                "mae",
                "mse",
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
