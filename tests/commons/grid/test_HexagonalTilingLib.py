"""
Created on 9 avr. 2021

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
from shapely import Polygon
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.grid.HexagonalTilingLib import HexagonalTilingLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class HexagonalTilingLibTest(unittest.TestCase):
    def setUp(self):
        self.gdf = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        pass

    def __plot(self, grid, title=None):
        import matplotlib.pyplot as plt
        from shapely import box

        bbox = GeoDataFrame([{"geometry": box(*self.gdf.total_bounds)}])
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        if title is not None:
            ax.set_title(title, fontsize=20)
        self.gdf.plot(ax=ax, color="lightgrey")
        bbox.boundary.plot(ax=ax, color="blue", linewidth=0.2)
        grid.boundary.plot(ax=ax, color="red", linewidth=0.2)
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

    def testGrid(self):
        result = HexagonalTilingLib(self.gdf, dx=10, dy=None, encode=True).grid()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(110, len(result), "Count rows")
        self.assertEqual(3, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Test is a GeoDataFrame of Polygon"
            )
            self.assertIn(row.gid, range(110), "Test gid attribute value")
            self.assertEqual(
                6,
                len(ArrayCoding.decode(row.neighbors6)),
                "Test neighbors6 attribute length",
            )
        # self.__plot(result, title="testGrid")

    def testIndoorGrid(self):
        result = HexagonalTilingLib(self.gdf, dx=10, dy=None, encode=True).indoorGrid()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(34, len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Test is a GeoDataFrame of Polygon"
            )
            self.assertIn(row.gid, range(110), "Test gid attribute value")
            self.assertEqual(
                6,
                len(ArrayCoding.decode(row.neighbors6)),
                "Test neighbors6 attribute length",
            )
            self.assertEqual(1, row.indoor, "Test indoor attribute value")
        # self.__plot(result, title="testIndoorGrid")

    def testIndoorOutdoorGrid(self):
        result = HexagonalTilingLib(
            self.gdf, dx=10, dy=None, encode=True
        ).indoorOutdoorGrid()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(110, len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Test is a GeoDataFrame of Polygon"
            )
            self.assertIn(row.gid, range(110), "Test gid attribute value")
            self.assertEqual(
                6,
                len(ArrayCoding.decode(row.neighbors6)),
                "Test neighbors6 attribute length",
            )
            self.assertIn(row.indoor, [0, 1], "Test indoor attribute value")
        # self.__plot(result, title="testIndoorOutdoorGrid")

    def testOutdoorGrid(self):
        result = HexagonalTilingLib(self.gdf, dx=10, dy=None, encode=True).outdoorGrid()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(76, len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Test is a GeoDataFrame of Polygon"
            )
            self.assertIn(row.gid, range(110), "Test gid attribute value")
            self.assertEqual(
                6,
                len(ArrayCoding.decode(row.neighbors6)),
                "Test neighbors6 attribute length",
            )
            self.assertEqual(0, row.indoor, "Test indoor attribute value")
        # self.__plot(result, title="testOutdoorGrid")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
