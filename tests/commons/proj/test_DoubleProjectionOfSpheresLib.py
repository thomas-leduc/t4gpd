"""
Created on 13 mar. 2024

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
from shapely import box
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.proj.DoubleProjectionOfSpheresLib import DoubleProjectionOfSpheresLib
from t4gpd.morph.STGrid import STGrid


class DoubleProjectionOfSpheresLibTest(unittest.TestCase):

    def setUp(self):
        self.radius = 7
        gdf = GeoDataFrame([{"geometry": box(0, 0, 50, 50)}])
        self.trees = STGrid(
            gdf,
            dx=10,
            dy=None,
            indoor=None,
            intoPoint=True,
            encode=True,
            withDist=False,
        ).run()
        self.trees.geometry = self.trees.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(geom, 12)
        )
        self.trees["crown_radius"] = 3
        self.trees.drop(
            index=self.trees[(self.trees.row == 2) & (self.trees.column == 2)].index,
            inplace=True,
        )
        self.sensors = GeoDataFrame([{"geometry": gdf.loc[0, "geometry"].centroid}])

    def tearDown(self):
        pass

    def _plot(self, ax, projectionName, result):
        from matplotlib_scalebar.scalebar import ScaleBar

        ax.set_title(projectionName, size=28)
        self.sensors.buffer(self.radius).boundary.plot(ax=ax, color="red")
        self.trees.plot(ax=ax, color="lightgrey", marker="o")
        result.plot(ax=ax, column="depth", cmap="Spectral", marker="+", legend=True)
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

    def testTrees(self):
        fig, ax = plt.subplots(
            nrows=1, ncols=3, figsize=(3 * 0.7 * 8.26, 0.7 * 8.26), squeeze=False
        )

        for i, projectionName in enumerate(["Isoaire", "Orthogonal", "Stereographic"]):
            result = DoubleProjectionOfSpheresLib.trees(
                self.sensors,
                self.trees,
                horizon=30,
                crownRadiusFieldname="crown_radius",
                h0=0.0,
                size=self.radius,
                projectionName=projectionName,
                npts=12,
            )

            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            # self.assertEqual(len(self.streetlights), len(result), "Count rows")
            # self.assertEqual(len(self.streetlights.columns)+3,
            #                  len(result.columns), "Count columns")
            # self.assertLessEqual(result.depth.max(), sqrt(
            #     2 * 20**2 + 12**2), "Test depth attribute (1)")
            # self.assertGreaterEqual(result.depth.min(), 12,
            #                         "Test depth attribute (2)")
            # print(result)
            self._plot(ax[0, i], projectionName, result)

        fig.tight_layout()
        plt.show()
        plt.close(fig)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
