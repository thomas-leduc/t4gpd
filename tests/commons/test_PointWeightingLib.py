"""
Created on 4 Nov. 2025

@author: tleduc

Copyright 2020-2026 Thomas Leduc

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
from numpy.random import default_rng
from shapely import points
from t4gpd.commons.PointWeightingLib import PointWeightingLib


class PointWeightingLibTest(unittest.TestCase):

    def setUp(self):
        self.maxDist, N = 2.5, 12
        rng = default_rng(123)
        pts = rng.integers(low=0, high=10, size=(N, 2))
        self.pts = GeoDataFrame({"gid": range(N), "geometry": points(pts)})

    def tearDown(self):
        pass

    def __plot(self, actual):
        import matplotlib.pyplot as plt

        actual["count_neighbors"] = actual.neighbors.apply(lambda t: len(t))

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_title(f"MaxDist = {self.maxDist}", fontsize=24)
        actual.plot(ax=ax, column="count_neighbors", cmap="cividis", legend=True)
        actual.apply(
            lambda x: ax.annotate(
                text=f"P$_{{{x.gid}}}$ ({x.count_neighbors})\nw={x.weight:.2f}",
                xy=x.geometry.coords[0],
                color="black",
                size=10,
                ha="left",  # if (0 == x.gid%2) else "right",
                va="bottom",  # if (0 == x.gid%2) else "top",
            ),
            axis=1,
        )
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testWeighByInverseDistance1(self):
        actual = PointWeightingLib.weighByInverseDistance(
            self.pts, self.maxDist, listOfNeighbors=False, copy=True
        )
        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.pts), len(actual), "Count rows")
        self.assertEqual(
            len(self.pts.columns) + 1, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            self.assertTrue(
                0 <= row.weight < 3,
                "Check weight values",
            )

    def testWeighByInverseDistance2(self):
        actual = PointWeightingLib.weighByInverseDistance(
            self.pts, self.maxDist, listOfNeighbors=True, copy=True
        )
        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.pts), len(actual), "Count rows")
        self.assertEqual(
            len(self.pts.columns) + 2, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            self.assertTrue(
                0 <= row.weight < 3,
                "Check weight values",
            )
            self.assertIsInstance(row.neighbors, list, "Check neighbors type")
            self.assertTrue(
                0 <= len(row.neighbors) <= 4,
                "Count neighbors",
            )
        # self.__plot(actual)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
