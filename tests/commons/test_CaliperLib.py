"""
Created on 15 dec. 2020

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

import matplotlib.pyplot as plt
import unittest
from geopandas import GeoDataFrame
from numpy import sqrt
from shapely import LineString, Point, Polygon, box, points
from t4gpd.commons.CaliperLib import CaliperLib


class CaliperLibTest(unittest.TestCase):

    def setUp(self):
        self.rectangle = Polygon(
            [(1, 0), (3, 0), (4, 1), (3, 1.9), (1, 1.9), (0, 1), (1, 0)]
        )
        pass

    def tearDown(self):
        pass

    def __plot(self):
        mabr, _, _ = CaliperLib.mabr(self.rectangle)
        mpbr, _, _ = CaliperLib.mpbr(self.rectangle)
        a1, p1 = mabr.area, mabr.length
        a2, p2 = mpbr.area, mpbr.length
        gdf1 = GeoDataFrame({"geometry": [self.rectangle]})
        gdf2 = GeoDataFrame({"geometry": points(self.rectangle.exterior.coords)})
        mabr = GeoDataFrame({"geometry": [mabr]})
        mpbr = GeoDataFrame({"geometry": [mpbr]})

        fig, ax = plt.subplots(figsize=(8, 8))
        gdf1.plot(ax=ax, color="blue", label="Input rectangle", linewidth=0, alpha=0.3)
        gdf2.plot(ax=ax, color="blue", marker="o")
        gdf2.apply(
            lambda x: ax.annotate(
                text=x.geometry.coords[0],
                xy=x.geometry.coords[0],
                color="black",
                size=14,
                ha="center",
                va="center",
            ),
            axis=1,
        )
        mabr.boundary.plot(
            ax=ax, color="red", label=f"MABR (area={a1:.1f}, perim={p1:.1f})"
        )
        mpbr.boundary.plot(
            ax=ax, color="black", label=f"MPBR (area={a2:.1f}, perim={p2:.1f})"
        )
        ax.legend(loc="upper center", fontsize=16)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testMabr(self):
        mabr, len1, len2 = CaliperLib.mabr(self.rectangle)
        self.assertIsInstance(mabr, Polygon, "MABR is a Polygon")
        self.assertTrue(len1 >= len2, "MABR is a Polygon")
        self.assertEqual(4 * 1.9, len1 * len2, "Test MABR area")
        self.assertEqual(2 * (4 + 1.9), 2 * (len1 + len2), "Test MABR perim")

    def testMabr2(self):
        pairs = [
            [box(0, 0, 0, 0), [Point([0, 0]), 0, 0]],
            [box(0, 0, 1, 0), [LineString([(0, 0), (1, 0)]), 1, 0]],
            [
                box(0, 0, 1, 1),
                [Polygon([(1, 0), (1, 1), (0, 1), (0, 0), (1, 0)]), 1, 1],
            ],
        ]
        for geom, expected in pairs:
            actual = CaliperLib.mabr(geom)
            self.assertEqual(expected[0], actual[0], "Test geometry")
            self.assertEqual(expected[1], actual[1], "Test len1")
            self.assertEqual(expected[2], actual[2], "Test len2")

    def testMpbr(self):
        mpbr, len1, len2 = CaliperLib.mpbr(self.rectangle)
        self.assertIsInstance(mpbr, Polygon, "MPBR is a Polygon")
        self.assertTrue(len1 >= len2, "MPBR is a Polygon")
        self.assertAlmostEqual(
            (2 * sqrt(2)) ** 2, len1 * len2, None, "Test MPBR area", 1e-6
        )
        self.assertAlmostEqual(
            4 * (2 * sqrt(2)), 2 * (len1 + len2), None, "Test MPBR perim", 1e-12
        )
        self.__plot()

    def testMajorAxis(self):
        mabr, _, _ = CaliperLib.mabr(self.rectangle)
        major = CaliperLib.major_axis(mabr)
        self.assertEqual(
            LineString([(0, 0.95), (4, 0.95)]), major, "Check major axis value"
        )

    def testMinorAxis(self):
        mabr, _, _ = CaliperLib.mabr(self.rectangle)
        minor = CaliperLib.minor_axis(mabr)
        self.assertEqual(
            LineString([(2, 1.9), (2, 0)]), minor, "Check minor axis value"
        )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
