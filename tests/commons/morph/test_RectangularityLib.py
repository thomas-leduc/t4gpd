"""
Created on 25 Feb. 2025

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
from shapely import LineString, Polygon
from shapely.wkt import loads
from t4gpd.commons.morph.RectangularityLib import RectangularityLib


class RectangularityLibTest(unittest.TestCase):

    def setUp(self):
        mpts = loads("MULTIPOINT ((40 0), (60 20), (90 20), (90 70), (30 90), (20 40))")
        self.duos = [
            (
                mpts,
                {"stretching": nan, "a_rect_def": nan, "p_rect_def": nan},
            ),
            (
                LineString(mpts.geoms),
                {"stretching": nan, "a_rect_def": nan, "p_rect_def": nan},
            ),
            (
                Polygon(mpts.geoms),
                {"stretching": 0.841, "a_rect_def": 0.679, "p_rect_def": 1.189},
            ),
        ]

    def tearDown(self):
        pass

    def testIndices(self):
        for geom, expected in self.duos:
            geom = Series(geom, index=["geometry"])
            actual = RectangularityLib._indices(geom, with_geom=False)
            for indice in RectangularityLib._getColumns():
                if isnan(expected[indice]):
                    self.assertTrue(isnan(actual[indice]), f"Test {indice}")
                else:
                    self.assertAlmostEqual(
                        expected[indice], actual[indice], None, f"Test {indice}", 1e-3
                    )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
