'''
Created on 21 june 2024

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
along with t4gpd. If not, see <https://www.gnu.org/licenses/>.
'''
import unittest
from geopandas import GeoDataFrame
from shapely import box
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STMakeNeighborhood import STMakeNeighborhood


class STMakeNeighborhoodTest(unittest.TestCase):

    def setUp(self):
        gdf = GeoDataFrame([{"gid": 1, "geometry": box(0, 0, 3, 3)}])
        self.grid = STGrid(gdf, dx=1, intoPoint=False).run()

    def tearDown(self):
        pass

    @staticmethod
    def _plot(input, result):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        input.boundary.plot(ax=ax, color="grey", label="Input geoms")
        input.apply(lambda x: ax.annotate(
                    text=x.gid, xy=x.geometry.centroid.coords[0],
                    color="black", size=12, ha="center", va="bottom"), axis=1)
        # result.boundary.plot(ax=ax, color="red", label="Result")
        result.apply(lambda x: ax.annotate(
            text=x.neighbors, xy=x.geometry.centroid.coords[0],
            color="red", size=12, ha="center", va="top"), axis=1)
        ax.legend(fontsize=14)
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STMakeNeighborhood(self.grid, gidFieldName="gid").run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.grid), len(result), "Count rows")
        self.assertEqual(len(self.grid.columns)+1,
                         len(result.columns), "Count columns")

        expected = [[1, 3, 4],
                    [0, 1, 4, 6, 7],
                    [3, 4, 7],
                    [0, 2, 3, 4, 5],
                    [0, 1, 2, 3, 5, 6, 7, 8],
                    [3, 4, 5, 6, 8],
                    [1, 4, 5],
                    [1, 2, 4, 7, 8],
                    [4, 5, 7]]
        self.assertEqual(expected, result.neighbors.tolist(),
                         "Check actual neighbors")
        # STMakeNeighborhoodTest._plot(
        #     self.grid, result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
