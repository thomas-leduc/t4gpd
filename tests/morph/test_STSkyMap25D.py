'''
Created on 25 sep. 2023

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
from shapely import Point, Polygon
from shapely.geometry import CAP_STYLE
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.demos.GeoDataFrameDemos2 import GeoDataFrameDemos2
from t4gpd.morph.STSkyMap25D import STSkyMap25D


class STSkyMap25DTest(unittest.TestCase):
    def setUp(self):
        h = 10.0
        self.masks1 = GeoDataFrame([{
            "gid": 1,
            "geometry": Polygon([(0, 0), (0, 10), (10, 10), (10, 9), (1, 9), (1, 0), (0, 0)]),
            "HAUTEUR": h
        }])
        self.masks2 = self.masks1.copy(deep=True)
        self.masks2.geometry = self.masks2.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(geom, z0=h))

        epsilon = 1e-6
        self.sensors1 = GeoDataFrame([
            {"gid": 1, "geometry": Point([1+epsilon, 9-epsilon])},
            {"gid": 2, "geometry": Point([5, 10+epsilon])},
            {"gid": 3, "geometry": Point([10, 0])},
        ])
        self.sensors2 = self.sensors1.copy(deep=True)
        self.sensors2.geometry = self.sensors2.geometry.apply(
            lambda geom: geom.buffer(0.5, cap_style=CAP_STYLE.square))

    def tearDown(self):
        self.masks1 = None
        self.masks2 = None
        self.sensors1 = None
        self.sensors2 = None

    def __plot(self, masks, sensors, result, indic=None):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        masks.plot(ax=ax, color="grey")
        sensors.plot(ax=ax, color="black", marker="+")
        result.plot(ax=ax, color="blue", alpha=0.35)
        if indic is not None:
            result.apply(lambda x: ax.annotate(
                text=f"{x[indic]:.2f}", xy=x.geometry.centroid.coords[0],
                color="red", size=12, ha="center"), axis=1)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        for sensors in [self.sensors1, self.sensors2]:
            for masks in [self.masks1, self.masks2]:
                result = STSkyMap25D(masks, sensors,
                                    nRays=64, rayLength=100.0,
                                    elevationFieldname="HAUTEUR",
                                    h0=0.0, size=2.0, epsilon=1e-2,
                                    projectionName="Stereographic",
                                    withIndices=False,
                                    withAngles=False).run()
                self.assertIsInstance(result, GeoDataFrame,
                                    "result is a GeoDataFrame")
                self.assertEqual(len(sensors), len(result), "Count rows")
                self.assertEqual(len(sensors.columns)+1,
                                len(result.columns), "Count columns")
                # self.__plot(masks, sensors, result)

    def testRun2(self):
        for sensors in [self.sensors1, self.sensors2]:
            for masks in [self.masks1, self.masks2]:
                result = STSkyMap25D(masks, sensors,
                                    nRays=64, rayLength=100.0,
                                    elevationFieldname="HAUTEUR",
                                    h0=0.0, size=2.0, epsilon=1e-2,
                                    projectionName="Stereographic",
                                    withIndices=True,
                                    withAngles=False).run()
                self.assertIsInstance(result, GeoDataFrame,
                                    "result is a GeoDataFrame")
                self.assertEqual(len(sensors), len(result), "Count rows")
                self.assertEqual(len(sensors.columns)+6,
                                len(result.columns), "Count columns")
                self.assertTrue(
                    all(result.apply(lambda row: row.w_mean > row.gid * 25, axis=1)), "Check w_mean values")
                self.assertTrue(
                    all(result.apply(lambda row: row.gid * 0.25 < row.svf < 1, axis=1)), "Check svf values")

                epsilon = 1e-3
                self.assertAlmostEqual(
                    result.at[0, "svf"], 0.266, None, "Check svf value (0)", epsilon)
                self.assertAlmostEqual(
                    result.at[1, "svf"], 0.516, None, "Check svf value (1)", epsilon)
                self.assertAlmostEqual(
                    result.at[2, "svf"], 0.889, None, "Check svf value (2)", epsilon)

                # self.__plot(masks, sensors, result, "svf")

    def testRun3(self):
        for sensors in [self.sensors1, self.sensors2]:
            for masks in [self.masks1, self.masks2]:
                result = STSkyMap25D(masks, sensors,
                                    nRays=64, rayLength=100.0,
                                    elevationFieldname="HAUTEUR",
                                    h0=0.0, size=2.0, epsilon=1e-2,
                                    projectionName="Stereographic",
                                    withIndices=True,
                                    withAngles=True).run()
                self.assertIsInstance(result, GeoDataFrame,
                                    "result is a GeoDataFrame")
                self.assertEqual(len(sensors), len(result), "Count rows")
                self.assertEqual(len(sensors.columns)+7,
                                len(result.columns), "Count columns")
                self.assertTrue(
                    all(result.apply(lambda row: row.w_mean > row.gid * 25, axis=1)), "Check w_mean values")
                self.assertTrue(
                    all(result.apply(lambda row: row.gid * 0.25 < row.svf < 1, axis=1)), "Check svf values")

                epsilon = 1e-3
                self.assertAlmostEqual(
                    result.at[0, "svf"], 0.266, None, "Check svf value (0)", epsilon)
                self.assertAlmostEqual(
                    result.at[1, "svf"], 0.516, None, "Check svf value (1)", epsilon)
                self.assertAlmostEqual(
                    result.at[2, "svf"], 0.889, None, "Check svf value (2)", epsilon)

                # result.drop(columns=["geometry"]).to_csv(
                #     "/tmp/1.csv", index=False, sep=";")
                self.__plot(masks, sensors, result, "svf")


if __name__ == "__main__":
    # import sys; sys.argv = ['', 'Test.testRun']
    unittest.main()
