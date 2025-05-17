"""
Created on 18 Apr. 2025

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
from shapely import MultiPoint, Polygon, box
from t4gpd.commons.morph.EllipticityLib import EllipticityLib


class EllipticityLibTest(unittest.TestCase):

    def setUp(self):
        igeom = box(0, 0, 10, 1)
        self.duos = [
            (
                Polygon([]),
                {
                    "mabe_azim": nan,
                    "mabe_area": nan,
                    "mabe_perim": nan,
                    "mabe_flattening": nan,
                    "mabe_mae": nan,
                    "mabe_mse": nan,
                    "a_elli_def": nan,
                    "p_elli_def": nan,
                },
            ),
            (
                igeom,
                {
                    "mabe_azim": 0,
                    "mabe_area": 15.7,
                    "mabe_perim": 28.7,
                    "mabe_flattening": 0.1,
                    "mabe_mae": 0.5,
                    "mabe_mse": 0.25,
                    "a_elli_def": igeom.area / 15.7,
                    "p_elli_def": 28.7 / igeom.length,
                },
            ),
            (
                igeom.exterior,
                {
                    "mabe_azim": 0,
                    "mabe_area": 15.7,
                    "mabe_perim": 28.7,
                    "mabe_flattening": 0.1,
                    "mabe_mae": 0.5,
                    "mabe_mse": 0.25,
                    "a_elli_def": 0,
                    "p_elli_def": 28.7 / igeom.length,
                },
            ),
            (
                MultiPoint(igeom.exterior.coords),
                {
                    "mabe_azim": 0,
                    "mabe_area": 15.7,
                    "mabe_perim": 28.7,
                    "mabe_flattening": 0.1,
                    "mabe_mae": 0.5,
                    "mabe_mse": 0.25,
                    "a_elli_def": 0,
                    "p_elli_def": nan,
                },
            ),
        ]

    def tearDown(self):
        pass

    def testIndices(self):
        for geom, expected in self.duos:
            geom = Series(geom, index=["geometry"])
            actual = EllipticityLib._indices(geom, with_geom=False)
            for indice in EllipticityLib._getColumns():
                if isnan(expected[indice]):
                    self.assertTrue(isnan(actual[indice]), f"Test {indice}")
                else:
                    self.assertAlmostEqual(
                        expected[indice], actual[indice], None, f"Test {indice}", 1e-1
                    )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
