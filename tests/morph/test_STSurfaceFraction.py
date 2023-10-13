'''
Created on 11 juin 2020

@author: tleduc

Copyright 2020 Thomas Leduc

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
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.demos.GeoDataFrameDemos2 import GeoDataFrameDemos2
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STSurfaceFraction import STSurfaceFraction

import matplotlib.pyplot as plt


class STSurfaceFractionTest(unittest.TestCase):

    def setUp(self):
        self.masks1 = GeoDataFrameDemos.regularGridOfPlots(2, 2)
        self.masks1["HAUTEUR"] = 1
        self.grid1 = STGrid(self.masks1, dx=5, dy=None,
                            indoor=None, intoPoint=False).run()

        self.masks2 = GeoDataFrameDemos2.irisMadeleineInNantesBuildings()
        self.grid2 = GeoDataFrameDemos2.irisMadeleineInNantesINSEEGrid()

    def tearDown(self):
        self.masks1 = None
        self.grid1 = None
        self.masks2 = None
        self.grid2 = None

    def __plot(self, masks, grid, result):
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        masks.plot(ax=ax, color="grey")
        grid.boundary.plot(ax=ax, color="black")
        result.plot(ax=ax, column="bsf", legend=True,
                    alpha=0.35, cmap="viridis")
        result.apply(lambda x: ax.annotate(
            text=f"{x.bsf:.2f}", xy=x.geometry.centroid.coords[0],
            color="red", size=12, ha="center"), axis=1)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        result = STSurfaceFraction(self.masks1, self.grid1).run()

        self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
        self.assertEqual(result.crs, self.grid1.crs, "Verify result CRS")
        self.assertEqual(16, len(result), "Count rows")
        self.assertEqual(len(result.columns), len(
            self.grid1.columns)+1, "Count columns")
        self.assertTrue(
            all(result.bsf.apply(lambda v: v == 1)), "Check BSF values")

        self.__plot(self.masks1, self.grid1, result)

    def testRun2(self):
        result = STSurfaceFraction(self.masks2, self.grid2).run()

        self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
        self.assertEqual(result.crs, self.grid2.crs, "Verify result CRS")
        self.assertEqual(len(result), len(self.grid2), "Count rows")
        self.assertEqual(len(result.columns), len(
            self.grid2.columns)+1, "Count columns")
        self.assertTrue(
            all(result.bsf.apply(lambda v: 0 <= v <= 1)), "Check BSF values")

        self.__plot(self.masks2, self.grid2, result)


if __name__ == "__main__":
    # import sys; sys.argv = ['', 'Test.testRun']
    unittest.main()
