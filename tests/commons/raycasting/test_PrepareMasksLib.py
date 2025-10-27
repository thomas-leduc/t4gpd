"""
Created on 10 nov 2023

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
from shapely.geometry import LineString, MultiLineString
from t4gpd.commons.raycasting.PrepareMasksLib import PrepareMasksLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid


class PrepareMasksLibTest(unittest.TestCase):
    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

        self.masks = GeoDataFrameDemos.regularGridOfPlots2(nlines=4, ncols=4)
        self.masks["HAUTEUR"] = 10
        self.viewpoints = STGrid(self.masks, dx=100, intoPoint=True, indoor=False).run()

    def tearDown(self):
        pass

    def __plot(self, buildings, viewpoints, vpcol, result, rcol):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        buildings.plot(ax=ax, color="grey")
        viewpoints.plot(ax=ax, column=vpcol, marker="+")
        result.plot(ax=ax, column=rcol, linewidth=5)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testExtrudeBuildingsOnFlatland(self):
        result = PrepareMasksLib.extrudeBuildingsOnFlatland(
            self.buildings, elevationFieldname="HAUTEUR", oriented=True
        )

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.buildings), len(result), "Count rows")
        self.assertEqual(
            len(self.buildings.columns), len(result.columns), "Count columns"
        )

    def testGetMasksAsBipoints(self):
        result = PrepareMasksLib.getMasksAsBipoints(
            self.buildings, oriented=True, make_valid=True, union=False
        )

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(
            len(self.buildings.columns), len(result.columns), "Count columns"
        )

        self.assertTrue(
            all(result.geometry.apply(lambda g: isinstance(g, LineString))),
            "Is a GeoDataFrame of LineString",
        )
        self.assertTrue(
            all(result.geometry.apply(lambda g: 2 == len(g.coords))),
            "Is a GeoDataFrame of bipoints",
        )

    def testLocalMaskClipping(self):
        buildings = GeoDataFrameDemos.regularGridOfPlots2(nlines=10, ncols=10)
        buildings.rename(columns={"gid": "buildings_id"}, inplace=True)
        viewpoints = STGrid(
            buildings, dx=750, dy=250, indoor=False, intoPoint=True
        ).run()

        for strict in [True, False]:
            actual = PrepareMasksLib.localMaskClipping(
                viewpoints, buildings, vp_pk="gid", buffDist=100, strict=strict
            )
            self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(28, len(actual), "Count rows")
            self.assertEqual(
                len(buildings.columns) + 1, len(actual.columns), "Count columns"
            )
            # self.__plot(buildings, viewpoints, "gid", actual, "gid")

    def testRemoveNonVisible25DMasks(self):
        result = PrepareMasksLib.removeNonVisible25DMasks(
            self.viewpoints,
            self.masks,
            elevationFieldname="HAUTEUR",
            horizon=40,
            h0=1.6,
        )
        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertLess(len(self.viewpoints), len(result), "Count rows")
        self.assertEqual(
            len(self.viewpoints.columns) + len(self.masks.columns) - 1 + 2,
            len(result.columns),
            "Count columns",
        )
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiLineString, "Is a MultiLineString")
        # self.__plot(self.masks, self.viewpoints, "gid", result, "gid_2")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
