"""
Created on 12 mar. 2024

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

import matplotlib.pyplot as plt
import unittest
from geopandas import GeoDataFrame
from numpy import sqrt
from shapely import box, Point, Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.proj.DoubleProjectionOfWallsLib import DoubleProjectionOfWallsLib


class DoubleProjectionOfWallsLibTest(unittest.TestCase):

    def setUp(self):
        h = 10.0
        self.masks1 = GeoDataFrame(
            [
                {
                    "gid": 1,
                    "geometry": Polygon(
                        [(0, 0), (0, 10), (10, 10), (10, 9), (1, 9), (1, 0), (0, 0)]
                    ),
                    "HAUTEUR": h,
                }
            ]
        )
        self.masks1.geometry = self.masks1.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(geom, h)
        )

        epsilon = 1e-6
        self.sensors1 = GeoDataFrame(
            [
                {"gid": 1, "geometry": Point([1 + epsilon, 9 - epsilon])},
                # {"gid": 2, "geometry": Point([5, 10+epsilon])},
                {"gid": 3, "geometry": Point([10 - epsilon, 0])},
            ]
        )

    def tearDown(self):
        pass

    @staticmethod
    def _plot(ax, projectionName, sensors, radius, masks, result):
        from matplotlib_scalebar.scalebar import ScaleBar

        minx, miny, maxx, maxy = result.buffer(5).total_bounds
        ax.set_title(projectionName, size=28)
        sensors.plot(ax=ax, color="black", marker="P")
        sensors.buffer(radius).boundary.plot(ax=ax, color="red")
        masks.plot(ax=ax, color="lightgrey")
        if "depth" in result:
            result.plot(ax=ax, column="depth", alpha=0.5, cmap="Spectral", legend=True)
        else:
            result.plot(ax=ax, color="red", alpha=0.5)
        ax.axis([minx, maxx, miny, maxy])
        ax.axis("off")
        scalebar = ScaleBar(
            dx=1.0,
            units="m",
            length_fraction=None,
            box_alpha=0.85,
            width_fraction=0.005,
            location="lower right",
            frameon=True,
        )
        ax.add_artist(scalebar)

    def testWalls1(self):
        radius = 4
        fig, ax = plt.subplots(
            nrows=1, ncols=3, figsize=(3 * 0.7 * 8.26, 0.7 * 8.26), squeeze=False
        )

        for i, projectionName in enumerate(["Isoaire", "Orthogonal", "Stereographic"]):
            result = DoubleProjectionOfWallsLib.walls(
                self.sensors1,
                self.masks1,
                horizon=100.0,
                maskidFieldname="gid",
                elevationFieldname="HAUTEUR",
                h0=0.0,
                size=radius,
                projectionName=projectionName,
                npts=5,
                aggregate=False,
            )

            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(4, len(result), "Count rows")
            DoubleProjectionOfWallsLibTest._plot(
                ax[0, i], projectionName, self.sensors1, radius, self.masks1, result
            )

        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testWalls2(self):
        radius = 4
        fig, ax = plt.subplots(
            nrows=1, ncols=3, figsize=(3 * 0.7 * 8.26, 0.7 * 8.26), squeeze=False
        )

        for i, projectionName in enumerate(["Isoaire", "Orthogonal", "Stereographic"]):
            result = DoubleProjectionOfWallsLib.walls(
                self.sensors1,
                self.masks1,
                horizon=100.0,
                maskidFieldname="gid",
                elevationFieldname="HAUTEUR",
                h0=0.0,
                size=radius,
                projectionName=projectionName,
                npts=5,
                aggregate=True,
            )

            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(len(self.sensors1), len(result), "Count rows")
            DoubleProjectionOfWallsLibTest._plot(
                ax[0, i], projectionName, self.sensors1, radius, self.masks1, result
            )

        fig.tight_layout()
        plt.show()
        plt.close(fig)

    """
    def testWalls3(self):
        radius = 12
        # Excerpt from GeoDataFrameDemos.ensaNantesBuildings()
        # buildings = buildings.loc[buildings[buildings.ID == "BATIMENT0000000302930047"].index]
        masks = GeoDataFrame([
            {"gid": 1, "geometry": Polygon([
                (355375.90000000002328306, 6688429.09999999962747097, 11.5),
                (355375.40000000002328306, 6688435.29999999981373549, 11.5),
                (355373.20000000001164153, 6688435.09999999962747097, 11.5),
                (355375.90000000002328306, 6688429.09999999962747097, 11.5)
            ]), "HAUTEUR": 11.5}], crs="epsg:2154")
        sensors = GeoDataFrame(
            [{"geometry": Point([355392, 6688437]), "gid": 111}], crs="epsg:2154")

        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(
            3 * 0.7 * 8.26, 0.7 * 8.26), squeeze=False)

        for i, projectionName in enumerate(["Isoaire", "Orthogonal", "Stereographic"]):
            result = DoubleProjectionOfWallsLib.walls(
                sensors, masks, horizon=50.0, 
                maskidFieldname="gid",
                elevationFieldname="HAUTEUR",
                h0=0.0, size=radius, projectionName="stereographic", npts=5, aggregate=False)

            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(1, len(result), "Count rows")
            DoubleProjectionOfWallsLibTest._plot(
                ax[0, i], projectionName, sensors, radius, masks, result)

        fig.tight_layout()
        plt.show()
        plt.close(fig)

        # fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.35 * 8.26))
        # buildings.plot(ax=ax, color="grey")
        # sensors.plot(ax=ax, color="black", marker="P")
        # result.plot(ax=ax, column="depth", cmap="Spectral", edgecolor="black", alpha=0.75)
        # ax.axis("off")
        # fig.tight_layout()
        # plt.show()
        # plt.close(fig)
    """

    def testWalls4(self):
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STGrid import STGrid

        radius = 4
        masks = GeoDataFrameDemos.ensaNantesBuildings()
        sensors = STGrid(
            masks,
            dx=10,
            dy=None,
            indoor=False,
            intoPoint=True,
            encode=True,
            withDist=False,
        ).run()
        sensors = sensors.loc[sensors[sensors.gid == 242].index]
        fig, ax = plt.subplots(
            nrows=1, ncols=3, figsize=(3 * 0.7 * 8.26, 0.7 * 8.26), squeeze=False
        )

        for i, projectionName in enumerate(["Isoaire", "Orthogonal", "Stereographic"]):
            result = DoubleProjectionOfWallsLib.walls(
                sensors,
                masks,
                horizon=100.0,
                elevationFieldname="HAUTEUR",
                h0=0.0,
                size=radius,
                projectionName=projectionName,
                npts=5,
                aggregate=False,
            )

            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            # self.assertEqual(6, len(result), "Count rows")
            DoubleProjectionOfWallsLibTest._plot(
                ax[0, i], projectionName, sensors, radius, masks, result
            )

        fig.tight_layout()
        plt.show()
        plt.close(fig)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
