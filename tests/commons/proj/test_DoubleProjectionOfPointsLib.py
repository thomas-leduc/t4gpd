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
from shapely import box
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.proj.DoubleProjectionOfPointsLib import DoubleProjectionOfPointsLib
from t4gpd.morph.STGrid import STGrid


class DoubleProjectionOfPointsLibTest(unittest.TestCase):

    def setUp(self):
        self.radius = 7
        gdf = GeoDataFrame([{"geometry": box(0, 0, 50, 50)}])
        self.streetlights = STGrid(
            gdf,
            dx=10,
            dy=None,
            indoor=None,
            intoPoint=True,
            encode=True,
            withDist=False,
        ).run()
        self.streetlights.geometry = self.streetlights.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(geom, 12)
        )
        self.sensors = GeoDataFrame([{"geometry": gdf.loc[0, "geometry"].centroid}])

    def tearDown(self):
        pass

    def _plot(self, ax, projectionName, result):
        from matplotlib_scalebar.scalebar import ScaleBar

        ax.set_title(projectionName, size=28)
        self.sensors.buffer(self.radius).boundary.plot(ax=ax, color="red")
        self.streetlights.plot(ax=ax, color="lightgrey", marker="o")
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

    def testPoints(self):
        projections = ["Isoaire", "Orthogonal", "Polar", "Stereographic"]

        fig, ax = plt.subplots(
            nrows=2, ncols=2, figsize=(2 * 0.7 * 8.26, 2 * 0.7 * 8.26), squeeze=False
        )

        for i, projectionName in enumerate(projections):
            result = DoubleProjectionOfPointsLib.points(
                self.sensors,
                self.streetlights,
                horizon=None,
                h0=0.0,
                size=self.radius,
                projectionName=projectionName,
                encode=True,
            )
            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(len(self.streetlights), len(result), "Count rows")
            self.assertEqual(
                len(self.streetlights.columns) + 3, len(result.columns), "Count columns"
            )
            self.assertLessEqual(
                result.depth.max(), sqrt(2 * 20**2 + 12**2), "Test depth attribute (1)"
            )
            self.assertGreaterEqual(result.depth.min(), 12, "Test depth attribute (2)")
            # print(result)
            self._plot(ax[i // 2, i % 2], projectionName, result)

        fig.tight_layout()
        plt.show()
        plt.close(fig)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
