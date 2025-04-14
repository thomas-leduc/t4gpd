"""
Created on 9 Apr. 2025

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
from pandas import Timestamp
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.shadow.STBuildingShadow import STBuildingShadow


class STBuildingShadowTest(unittest.TestCase):

    def setUp(self):
        # self.buildings = GeoDataFrameDemos.districtGraslinInNantesBuildings()
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        # self.buildings = GeoDataFrameDemos.singleBuildingInNantes()
        self.datetimes = [
            Timestamp(f"2025-07-21 {h}:00", tz="Europe/Paris").tz_convert("UTC")
            for h in [9, 12, 15]
        ]

    def tearDown(self):
        pass

    def __plot(self, actual):
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap

        actual.datetime = actual.datetime.apply(lambda dt: dt.strftime("%H:%M"))
        my_cmap = ListedColormap(["red", "green", "blue"])

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        actual.plot(ax=ax, column="datetime", cmap=my_cmap, alpha=0.25, legend=True)
        self.buildings.boundary.plot(ax=ax, color="red")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        actual = STBuildingShadow(
            self.buildings,
            self.datetimes,
            elevationFieldName="HAUTEUR",
            altitudeOfShadowPlane=0,
            aggregate=True,
            model="pvlib",
        ).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(3, len(actual), "Count rows")
        self.assertEqual(2, len(actual.columns), "Count columns")

        for _, shadowRow in actual.iterrows():
            self.assertIn(shadowRow.datetime, self.datetimes, "Datetime test")

            shadowGeom = shadowRow.geometry
            for _, buildingRow in self.buildings.iterrows():
                buildingGeom = buildingRow.geometry
                self.assertTrue(buildingGeom.within(shadowGeom), "Within test")

        # self.__plot(actual)

    def testRun2(self):
        actual = STBuildingShadow(
            self.buildings,
            self.datetimes,
            elevationFieldName="HAUTEUR",
            altitudeOfShadowPlane=0,
            aggregate=False,
            model="pvlib",
        ).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(3 * len(self.buildings), len(actual), "Count rows")
        self.assertEqual(
            1 + len(self.buildings.columns), len(actual.columns), "Count columns"
        )

        for _, shadowRow in actual.iterrows():
            self.assertIn(shadowRow.datetime, self.datetimes, "Datetime test")

            shadowGeom = shadowRow.geometry
            shadowId = shadowRow.ID
            for _, buildingRow in self.buildings[
                self.buildings.ID == shadowId
            ].iterrows():
                buildingGeom = buildingRow.geometry
                self.assertTrue(
                    buildingGeom.within(shadowGeom.buffer(1e-6)), "Within test"
                )

        # self.__plot(actual)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
