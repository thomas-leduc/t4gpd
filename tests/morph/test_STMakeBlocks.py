'''
Created on 12 feb. 2021

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
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.morph.STBBox import STBBox
from t4gpd.morph.STMakeBlocks import STMakeBlocks
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class STMakeBlocksTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        self.roads = GeoDataFrameDemos.districtRoyaleInNantesRoads()
        self.roi = STBBox(self.buildings, buffDist=-1).run()

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.buildings.plot(ax=ax, color="grey")
        self.roads.plot(ax=ax, color="black")
        self.roi.boundary.plot(ax=ax, color="black")
        result.plot(ax=ax, column="gid", alpha=0.42, cmap="hot")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STMakeBlocks(self.buildings, self.roads, roi=self.roi).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(39, len(result), "Count rows")
        self.assertEqual(2, len(result.columns), "Count columns")
        self.assertTrue(all(result.geometry.apply(
            lambda g: GeomLib.isPolygonal(g))), "Is a GeoDataFrame of [Multi]Polygons")
        self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
