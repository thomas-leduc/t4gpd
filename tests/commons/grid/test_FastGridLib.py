"""
Created on 31 mars 2021

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

from geopandas import GeoDataFrame
from shapely import Point, Polygon
from t4gpd.commons.grid.FastGridLib import FastGridLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class FastGridLibTest(unittest.TestCase):
    def setUp(self):
        self.building = GeoDataFrameDemos.singleBuildingInNantes()
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        pass

    def __plot(self, buildings, grid, title=None):
        import matplotlib.pyplot as plt
        from shapely.geometry import box

        bbox = GeoDataFrame([{"geometry": box(*buildings.total_bounds)}])
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        if title is not None:
            ax.set_title(title, fontsize=20)
        buildings.plot(ax=ax, color="lightgrey")
        bbox.boundary.plot(ax=ax, color="red", linewidth=0.2)

        if grid.geometry.apply(lambda geom: isinstance(geom, Point)).all():
            grid.plot(ax=ax, color="blue", linewidth=0.3)
        else:
            grid.boundary.plot(ax=ax, color="blue", linewidth=0.3)
        grid.apply(
            lambda x: ax.annotate(
                text=x.gid,
                xy=x.geometry.centroid.coords[0],
                color="blue",
                size=12,
                ha="center",
            ),
            axis=1,
        )

        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testGrid1(self):
        result = FastGridLib.grid(
            self.building, dx=10, dy=None, intoPoint=True, withRowsCols=False
        )

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(72, len(result), "Count rows")
        self.assertEqual(2, len(result.columns), "Count columns")
        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Point, "Test is a GeoDataFrame of Point"
            )

        # self.__plot(self.building, result, title="testGrid")

    def testGrid2(self):
        result = FastGridLib.grid(
            self.buildings, dx=50, dy=None, intoPoint=False, withRowsCols=True
        )

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(25, len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")
        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Test is a GeoDataFrame of Polygon"
            )

        # self.__plot(self.buildings, result, title="testGrid")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
