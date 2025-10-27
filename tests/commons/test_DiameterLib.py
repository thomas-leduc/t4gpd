"""
Created on 18 Jul. 2025

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

from shapely import LineString
from t4gpd.commons.DiameterLib import DiameterLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class DiameterLibTest(unittest.TestCase):
    def setUp(self):
        self.buildings = GeoDataFrameDemos.singleBuildingInNantes()
        self.geom = self.buildings.loc[0, "geometry"]

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt
        from geopandas import GeoDataFrame

        gdf = GeoDataFrame([{"geometry": result[0]}], crs=self.buildings.crs)

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=ax, color="lightgrey")
        gdf.plot(ax=ax, color="red")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testDiameter(self):
        expected = [
            LineString([(353869.6, 6695075.7, 46.2), (353942.6, 6695014, 46.2)]),
            95.6,
            139.8,
        ]
        actual = DiameterLib.diameter(self.geom)
        self.assertEqual(expected[0], actual[0], "Test geometry")
        self.assertAlmostEqual(expected[1], actual[1], None, "Test maxDist", 0.1)
        self.assertAlmostEqual(expected[2], actual[2], None, "Test orientation", 0.1)
        # self.__plot(actual)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
