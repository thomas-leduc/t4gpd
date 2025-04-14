"""
Created on 27 aug. 2020

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
from datetime import datetime, timedelta, timezone
from geopandas import GeoDataFrame
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.sun.STHardShadow import STHardShadow


class STHardShadowTest(unittest.TestCase):

    def setUp(self):
        # self.buildings = GeoDataFrameDemos.districtGraslinInNantesBuildings()
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        # self.buildings = GeoDataFrameDemos.singleBuildingInNantes()
        self.datetimes = [
            datetime(2020, 7, 21, 9),
            datetime(2020, 7, 21, 15),
            timedelta(hours=3),
        ]
        self.datetimes = DatetimeLib.generate(self.datetimes)

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        result.plot(ax=ax, column="datetime", alpha=0.5, legend=True)
        self.buildings.boundary.plot(ax=ax, color="red")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        result = STHardShadow(
            self.buildings,
            self.datetimes,
            occludersElevationFieldname="HAUTEUR",
            altitudeOfShadowPlane=0,
            aggregate=True,
            tz=timezone.utc,
            model="pysolar",
        ).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(3, len(result), "Count rows")
        self.assertEqual(2, len(result.columns), "Count columns")

        datetimes = [str(dt) for dt in list(self.datetimes.values())[0]]
        for _, shadowRow in result.iterrows():
            self.assertIn(shadowRow.datetime, datetimes, "Datetime test")

            shadowGeom = shadowRow.geometry
            for _, buildingRow in self.buildings.iterrows():
                buildingGeom = buildingRow.geometry
                self.assertTrue(buildingGeom.within(shadowGeom), "Within test")

        # self.__plot(result)

    def testRun2(self):
        result = STHardShadow(
            self.buildings,
            self.datetimes,
            occludersElevationFieldname="HAUTEUR",
            altitudeOfShadowPlane=0,
            aggregate=False,
            tz=timezone.utc,
            model="pysolar",
        ).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(3 * len(self.buildings), len(result), "Count rows")
        self.assertEqual(
            1 + len(self.buildings.columns), len(result.columns), "Count columns"
        )

        datetimes = [str(dt) for dt in list(self.datetimes.values())[0]]
        for _, shadowRow in result.iterrows():
            self.assertIn(shadowRow.datetime, datetimes, "Datetime test")

            shadowGeom = shadowRow.geometry
            shadowId = shadowRow.ID
            for _, buildingRow in self.buildings[
                self.buildings.ID == shadowId
            ].iterrows():
                buildingGeom = buildingRow.geometry
                self.assertTrue(
                    buildingGeom.within(shadowGeom.buffer(0.001)), "Within test"
                )

        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
