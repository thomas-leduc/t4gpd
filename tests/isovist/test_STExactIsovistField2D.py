'''
Created on 19 dec. 2021

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

from geopandas import GeoDataFrame
from shapely import Point, Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.isovist.STExactIsovistField2D import STExactIsovistField2D


class STExactIsovistField2DTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoints = GeoDataFrame([
            {"geometry": Point((355388.222, 6688408.698)), "rayLength": 25},
            {"geometry": Point((355262.596, 6688405.552)), "rayLength": 50},
            {"geometry": Point((355350.125, 6688445.012)), "rayLength": 15},
            {"geometry": Point((355271.557, 6688570.859)), "rayLength": 75},
            # {"geometry": Point((355184.075, 6688676.868)) },
            # {"geometry": Point((355159.626, 6688560.735)) },
        ], crs=self.buildings.crs)

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        result.plot(ax=ax, color="yellow", edgecolor="orange", alpha=0.4)
        self.buildings.plot(ax=ax, color="lightgrey", edgecolor="dimgrey")
        self.viewpoints.plot(ax=ax, color="red", marker="+")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        result = STExactIsovistField2D(
            self.buildings, self.viewpoints, rayLength=100.0, delta=3.0).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.viewpoints), len(result), "Count rows")
        self.assertEqual(len(self.viewpoints.columns) + 12,
                         len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon,
                                  "Is a GeoDataFrame of Polygons")

        # self.__plot(result)

    def testRun2(self):
        result = STExactIsovistField2D(
            self.buildings, self.viewpoints, rayLength="rayLength", delta=3.0).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.viewpoints), len(result), "Count rows")
        self.assertEqual(len(self.viewpoints.columns) + 12,
                         len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon,
                                  "Is a GeoDataFrame of Polygons")

        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
