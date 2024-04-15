'''
Created on 5 janv. 2021

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

from geopandas.geodataframe import GeoDataFrame
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.demos.GeoDataFrameDemos2 import GeoDataFrameDemos2
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STPolygonize import STPolygonize
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.morph.geoProcesses.SurfaceFraction import SurfaceFraction


class SurfaceFractionTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos2.irisMadeleineInNantesBuildings()
        self.grid = GeoDataFrameDemos2.irisMadeleineInNantesINSEEGrid()

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=ax, color="grey")
        self.grid.boundary.plot(ax=ax, color="black")
        result.plot(ax=ax, column="surf_ratio", legend=True,
                    alpha=0.35, cmap="viridis")
        result.apply(lambda x: ax.annotate(
            text=f"{x.surf_ratio:.2f}", xy=x.geometry.centroid.coords[0],
            color="red", size=12, ha="center"), axis=1)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        op = SurfaceFraction(self.buildings, buffDist=None)
        result = STGeoProcess(op, self.grid).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(result.crs, self.grid.crs, "Verify result CRS")
        self.assertEqual(len(self.grid), len(result), "Count rows")
        self.assertEqual(len(self.grid.columns)+1,
                         len(result.columns), "Count columns")
        for _, row in result.iterrows():
            self.assertTrue(0.0 <= row["surf_ratio"] <=
                            1.0, "Test 'surf_ratio' attribute value")
        self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
