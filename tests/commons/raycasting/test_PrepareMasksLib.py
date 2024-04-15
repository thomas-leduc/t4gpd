'''
Created on 10 nov 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from shapely.geometry import LineString, MultiLineString
from t4gpd.commons.raycasting.PrepareMasksLib import PrepareMasksLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid


class PrepareMasksLibTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

        self.masks = GeoDataFrameDemos.regularGridOfPlots2(nlines=4, ncols=4)
        self.masks["HAUTEUR"] = 10
        self.viewpoints = STGrid(
            self.masks, dx=100, intoPoint=True, indoor=False).run()

    def tearDown(self):
        pass

    def testExtrudeBuildingsOnFlatland(self):
        result = PrepareMasksLib.extrudeBuildingsOnFlatland(
            self.buildings, elevationFieldname="HAUTEUR", oriented=True)

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(self.buildings, len(result), "Count rows")
        self.assertEqual(len(self.buildings), len(
            result.columns), "Count columns")

    def testExtrudeBuildingsOnFlatland(self):
        result = PrepareMasksLib.getMasksAsBipoints(
            self.buildings, oriented=True, make_valid=True, union=False)

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.buildings.columns),
                         len(result.columns), "Count columns")

        self.assertTrue(all(result.geometry.apply(lambda g: isinstance(
            g, LineString))), "Is a GeoDataFrame of LineString")
        self.assertTrue(all(result.geometry.apply(
            lambda g: 2 == len(g.coords))), "Is a GeoDataFrame of bipoints")

    def __plot(self, result):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.masks.plot(ax=ax, color="grey")
        self.viewpoints.plot(ax=ax, column="gid", marker="+")
        result.plot(ax=ax, column="gid", linewidth=5)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRemoveNonVisible25DMasks(self):
        result = PrepareMasksLib.removeNonVisible25DMasks(self.viewpoints, self.masks,
                                                          elevationFieldname="HAUTEUR",
                                                          horizon=40, h0=1.6)
        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.viewpoints), len(result), "Count rows")
        self.assertEqual(len(self.viewpoints.columns)+2,
                         len(result.columns), "Count columns")
        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, MultiLineString, "Is a MultiLineString")
            if (10 == row.gid):
                self.assertEqual(8, len(row.geometry.geoms),
                                 "Count MultiLineString sub components")
            else:
                self.assertEqual(2, len(row.geometry.geoms),
                                 "Count MultiLineString sub components")
        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
