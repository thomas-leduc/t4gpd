'''
Created on 11 juin 2021

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
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STToRoadsSectionsNodes import STToRoadsSectionsNodes
from t4gpd.morph.geoProcesses.CrossroadsStarDomain import CrossroadsStarDomain
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class CrossroadsStarDomainTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        self.roads = GeoDataFrameDemos.districtRoyaleInNantesRoads()
        self.nodes = STToRoadsSectionsNodes(self.roads).run()
        self.GIDS = [9, 27, 63, 89, 104, 115, 147]
        self.nodes = self.nodes.loc[self.nodes.gid.isin(self.GIDS)]

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=ax, color="lightgrey",
                            edgecolor="dimgrey", linewidth=0.2)
        self.roads.plot(ax=ax, color="black", linewidth=0.5)
        self.nodes.plot(ax=ax, color="red", marker="+", markersize=12)
        result.boundary.plot(ax=ax, color="red")
        result.apply(lambda x: ax.annotate(
            text=f"{x.gid} ({x.kern_drift:.1f})", xy=x.geometry.centroid.coords[0],
            color="black", size=10, ha="right", va="bottom"), axis=1)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        op = CrossroadsStarDomain(self.buildings)
        result = STGeoProcess(op, self.nodes).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.GIDS), len(result), "Count rows")
        self.assertEqual(6, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIn(row.gid, self.GIDS, "Test gid attr. value")
            self.assertTrue(0 <= row.MinLenRad <= row.MaxLenRad,
                            "Test MinLenRad/MaxLenRad attr. values")
            self.assertTrue(0 <= row.kern_drift, "Test kern_drift attr. value")

        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
