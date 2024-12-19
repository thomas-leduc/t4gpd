'''
Created on 24 aug. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
'''
import unittest
import geopandas as gpd
from shapely.geometry import Polygon
from t4gpd.morph.STPolygonize import STPolygonize
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class STPolygonizeTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.districtRoyaleInNantesRoads()

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1.0*8.26, 1.0*8.26))
        self.roads.plot(ax=ax)
        result.plot(ax=ax, column="gid")
        result.apply(lambda x: ax.annotate(
	        text=x.gid, xy=x.geometry.centroid.coords[0],
	        color="red", size=12, ha="center"), axis=1)
        plt.show()

    def testRun(self):
        result = STPolygonize(self.roads, patchid="gid").run()

        self.assertIsInstance(result, gpd.GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(22, len(result), "Count rows")
        self.assertEqual(2, len(result.columns), "Count columns")
        self.assertIn("gid", result, "Check patchid fieldname")
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygon')

        self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
