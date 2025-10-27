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
from t4gpd.commons.grid.DichotomizedGrid import DichotomizedGrid
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class DichotomizedGridTest(unittest.TestCase):
    def setUp(self):
        self.gdf = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        pass

    def __plot(self, gdf, grid, title):
        import matplotlib.pyplot as plt
        from shapely.geometry import box

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        ax.set_title(title, fontsize=20)
        gdf.plot(ax=ax, color="lightgrey")
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

    def testGrid(self):
        niter = 5
        result = DichotomizedGrid(self.gdf, niter, encode=True).grid()

        self.assertIsInstance(result, dict, "Is a dict")
        self.assertEqual(niter, len(result), "Is a dict of %d keys" % niter)

        prevDx, prevDy = None, None
        for i, value in result.items():
            self.assertEqual(2 ** i, value["nrows"], "Test nrows value")
            if prevDx is None:
                self.assertIsInstance(value["dx"], float, "Test dx is a float")
                self.assertIsInstance(value["dy"], float, "Test dy is a float")
            else:
                self.assertAlmostEqual(
                    prevDx / 2.0, value["dx"], None, "Test dx value", 1e-6
                )
                self.assertAlmostEqual(
                    prevDy / 2.0, value["dy"], None, "Test dy value", 1e-6
                )
            prevDx, prevDy = value["dx"], value["dy"]
            self.assertIsInstance(
                value["grid"], GeoDataFrame, "Test grid is a GeoDataFrame"
            )
            self.assertLessEqual(
                len(value["grid"]),
                value["nrows"] * value["nrows"],
                "Test grid is not too big",
            )

        for niter, v in result.items():
            title = (
                f"niter={niter}, nrows={v['nrows']}, dx={v['dx']:.1f}, dy={v['dy']:.1f}"
            )
            # self.__plot(self.gdf, v["grid"], title=title)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
