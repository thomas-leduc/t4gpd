'''
Created on 17 sept. 2020

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from shapely import LineString, Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.IdentifyTheClosestPolyline import IdentifyTheClosestPolyline
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class IdentifyTheClosestPolylineTest(unittest.TestCase):

    def setUp(self):
        self.trees1 = GeoDataFrameDemos.ensaNantesTrees()
        self.roads1 = GeoDataFrameDemos.ensaNantesRoads()

        rows = [
            {"geometry": Point((5, -5)), "gid": 1},
            {"geometry": Point((50, 5)), "gid": 2},
            {"geometry": Point((75, 5)), "gid": 3}
            ]
        self.trees2 = GeoDataFrame(rows)

        rows = [
            {"geometry": LineString([(0, 10), (0, 0)]), "ID": 10},
            {"geometry": LineString([(0, 0), (100, 0)]), "ID": 20},
            ]
        self.roads2 = GeoDataFrame(rows)

    def tearDown(self):
        pass

    def __plot(self, roads, roads_id, result, result_id):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        result.plot(ax=ax, column=result_id, marker="o", markersize=100)
        roads.plot(ax=ax, column=roads_id, linewidth=3)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        op = IdentifyTheClosestPolyline(self.roads1, "ID")
        result = STGeoProcess(op, self.trees1).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(116, len(result), "Count rows")
        self.assertEqual(11, len(result.columns), "Count columns")

        print(self.roads1.head(2))
        print(result.head(2))
        self.__plot(self.roads1, "ID", result, "road_id")
        """
        import matplotlib.pyplot as plt
        ax = self.trees1.plot(edgecolor="green", linewidth=0.3)
        self.roads1.plot(ax=ax, column="ID", linewidth=2.3)
        result.plot(ax=ax, column="road_id", linewidth=0.3)
        plt.show()
        """
        # result.to_file("/tmp/xxx.shp")

    def testRun2(self):
        op = IdentifyTheClosestPolyline(self.roads2, "ID")
        result = STGeoProcess(op, self.trees2).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(3, len(result), "Count rows")
        self.assertEqual(6, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            currGeom = row.geometry
            self.assertIsInstance(currGeom, Point, "Is a GeoDataFrame of Point")
            self.assertEqual(row["road_id"], 20, "Road id attribute test")
            self.assertEqual(row["road_dist"], 5.0, "Road distance attribute test")
            self.assertEqual(currGeom.coords[0][0], row["road_absc"], "Road abscissa attribute test")
            self.assertTrue(row["road_side"] in [-1, 1], "Road side attribute test")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
