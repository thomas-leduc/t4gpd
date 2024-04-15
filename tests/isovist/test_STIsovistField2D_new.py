'''
Created on 9 nov 2023

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
from numpy import pi
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.wkt import loads
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.isovist.STIsovistField2D_new import STIsovistField2D_new
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STPointsDensifier2 import STPointsDensifier2


class STIsovistField2D_newTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoints = STGrid(
            self.buildings, 50, dy=None, indoor=False, intoPoint=True).run()

    def tearDown(self):
        self.buildings = None
        self.viewpoints = None

    def __plot(self, buildings, sensors, isovField, isovRaysField):
        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        buildings.boundary.plot(ax=basemap, color="grey",
                                edgecolor="grey", hatch="/")
        sensors.plot(ax=basemap, color="black")
        isovField.plot(ax=basemap, color="yellow", alpha=0.4)
        isovRaysField.plot(ax=basemap, color="black", linewidth=0.4)
        plt.show()
        plt.close(fig)

    def testRun1(self):
        nRays, rayLength = 64, 20.0
        isovRaysField, isovField = STIsovistField2D_new(
            self.buildings, self.viewpoints, nRays, rayLength, 
            withIndices=True).run()

        for result in [isovRaysField, isovField]:
            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(result.crs, self.buildings.crs, "Verify CRS")
            self.assertEqual(len(self.viewpoints), len(result), "Count rows")
            self.assertEqual(8 + len(self.viewpoints.columns),
                             len(result.columns), "Count columns")

        approxRayLength = rayLength + 1e-6
        for _, row in isovRaysField.iterrows():
            self.assertIsInstance(
                row.geometry, MultiLineString, "Is a GeoDataFrame of MultiLineString")
            self.assertEqual(0, row["indoor"], "indoor attribute values")
            self.assertEqual(nRays, len(row.geometry.geoms),
                             "Verify number of rays")
            self.assertTrue(all(
                [0 <= g.length <= approxRayLength for g in row.geometry.geoms]), "Verify ray lengths")
            self.assertIsInstance(
                row["viewpoint"], Point, "Test viewpoint attribute")
            self.assertIsInstance(
                row["vect_drift"], LineString, "Test vect_drift attribute")
            self.assertEqual(row["viewpoint"].coords[0], row["vect_drift"].coords[0],
                             "Test viewpoint and vect_drift attribute values")

        for _, row in isovField.iterrows():
            self.assertIsInstance(row.geometry, Polygon,
                                  "Is a GeoDataFrame of Polygon")
            self.assertEqual(0, row["indoor"], "indoor attribute values")
            self.assertTrue(0 <= row.geometry.area <= pi *
                            rayLength ** 2, "Verify isovist field areas")
            self.assertIsInstance(
                row["viewpoint"], Point, "Test viewpoint attribute")
            self.assertIsInstance(
                row["vect_drift"], LineString, "Test vect_drift attribute")
            self.assertEqual(row["viewpoint"].coords[0], row["vect_drift"].coords[0],
                             "Test viewpoint and vect_drift attribute values")

        # self.__plot(self.buildings, self.viewpoints, isovField, isovRaysField)

    def testRun2(self):
        nlines, ncols = 2, 2
        bdx, bdy = 50, 50  # building size
        sdx, sdy = 10, 20  # street widths
        buildings = GeoDataFrameDemos.regularGridOfPlots2(
            nlines, ncols, bdx, bdy, sdx, sdy)

        sensors = STPointsDensifier2(
            buildings, curvAbsc=[0.5], pathidFieldname=None).run()

        nRays, rayLength = 64, 20.0
        isovRaysField, isovField = STIsovistField2D_new(
            buildings, sensors, nRays, rayLength, withIndices=True).run()

        for result in [isovRaysField, isovField]:
            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(result.crs, buildings.crs, "Verify CRS")
            self.assertEqual(16, len(result), "Count rows")
            self.assertEqual(8 + len(sensors.columns),
                             len(result.columns), "Count columns")

        # self.__plot(buildings, sensors, isovField, isovRaysField)

    def testRun3(self):
        buildings = GeoDataFrame([
            {"geometry": loads(
                "POLYGON ((50 80, 60 80, 60 70, 50 70, 50 80))")},
            {"geometry": loads(
                "POLYGON ((0 100, 10 100, 10 10, 90 10, 90 30, 60 30, 60 60, 70 60, 70 40, 90 40, 90 90, 80 90, 80 80, 70 80, 70 90, 30 90, 30 50, 20 50, 20 100, 100 100, 100 0, 0 0, 0 100))")},
        ])
        for x, y in [(30, 80), (40, 70), (60, 70)]:
            sensors = GeoDataFrame([
                {"geometry": loads(f"POINT ({x} {y})")},
            ])

            nRays, rayLength = 64, 100.0
            isovRaysField, isovField = STIsovistField2D_new(
                buildings, sensors, nRays, rayLength, withIndices=True).run()

            for result in [isovRaysField, isovField]:
                self.assertIsInstance(
                    result, GeoDataFrame, "Is a GeoDataFrame")
                self.assertEqual(result.crs, buildings.crs, "Verify CRS")
                self.assertEqual(1, len(result), "Count rows")
                self.assertEqual(8 + len(sensors.columns), len(result.columns), "Count columns")

            # self.__plot(buildings, sensors, isovField, isovRaysField)

    def testRun4(self):
        buildings = GeoDataFrame([{
            "gid": 1,
            "geometry": loads("POLYGON ((353471.90000000002328306 6684814 33.5, 353463.5 6684812.09999999962747097 33.5, 353461.79999999998835847 6684819.79999999981373549 33.5, 353462.70000000001164153 6684820.20000000018626451 33.5, 353461.5 6684825.79999999981373549 33.5, 353468.59999999997671694 6684827.5 33.5, 353471.90000000002328306 6684814 33.5))"),
            "HAUTEUR": 4.0
        }])
        sensors = GeoDataFrame([
            {"gid": 1, "geometry": loads(
                "POINT (353469.15000000008149073 6684825.25)")},
        ])
        nRays, rayLength = 64, 20.0
        isovRaysField, isovField = STIsovistField2D_new(
            buildings, sensors, nRays, rayLength, withIndices=True).run()

        for result in [isovRaysField, isovField]:
            self.assertIsInstance(
                result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(result.crs, buildings.crs, "Verify CRS")
            self.assertEqual(1, len(result), "Count rows")
            self.assertEqual(8 + len(sensors.columns), len(result.columns), "Count columns")

        # self.__plot(buildings, sensors, isovField, isovRaysField)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
