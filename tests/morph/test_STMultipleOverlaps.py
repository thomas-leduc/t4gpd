'''
Created on 12 sept. 2020

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
from numpy import asarray
from shapely.affinity import translate
from shapely.geometry import box, Polygon
from t4gpd.morph.STMultipleOverlaps import STMultipleOverlaps


class STMultipleOverlapsTest(unittest.TestCase):

    def setUp(self):
        a = box(0, 0, 10, 10)
        b = translate(a, xoff=5.0, yoff=5.0)
        c = translate(a, xoff=5.0)
        self.gdf = GeoDataFrame([
            {"gid": 10, "geometry": a},
            {"gid": 20, "geometry": b},
            {"gid": 30, "geometry": c}])

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(ncols=2, nrows=1, figsize=(
            1.5 * 8.26, 1.5 * 8.26), squeeze=False)

        ax = axes[0, 0]
        PAIRS = asarray([("/", "red"), ("+", "green"), ("\\", "blue")])
        for i, gid in enumerate(self.gdf.gid.unique()):
            self.gdf[self.gdf.gid == gid].boundary.plot(
                ax=ax, hatch=PAIRS[i, 0], color=PAIRS[i, 1], label=gid)
        ax.legend(loc="upper left")
        ax.axis("off")

        ax = axes[0, 1]
        result.plot(ax=ax, column="noverlays", alpha=0.2)
        result.apply(lambda x: ax.annotate(
            text=f"{x.noverlays}\n{x.gid}",
            xy=x.geometry.centroid.coords[0],
            color="black", size=11, ha="center"), axis=1)
        ax.axis("off")
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STMultipleOverlaps(
            self.gdf, pks=["gid"], patchid="patchid").run()
        print(result)

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(6, len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon,
                                  "Is a GeoDataFrame of Polygons")
            self.assertTrue(25 <= row.geometry.area < 50.1, "Areas test")
            self.assertIn(row["noverlays"], range(1, 4), "Test")
            print(row.noverlays, row.geometry.area)
            self.assertTrue(
                ((row["noverlays"] in [2, 3]) and (row.geometry.area == 25)) or
                ((row["noverlays"] == 1) and (row.geometry.area in [25, 50])),
                "Areas and noverlays field test")

        self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
