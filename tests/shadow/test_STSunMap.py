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
from shapely import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STBBox import STBBox
from t4gpd.shadow.STSunMap import STSunMap


class STSunMapTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        self.buildings.fillna({"HAUTEUR": 3.33}, inplace=True)
        self.sensors = GeoDataFrame(
            [
                {"gid": 1, "geometry": Point((355143.0, 6689359.4))},
                {"gid": 2, "geometry": Point((355166.0, 6689328.0))},
            ],
            crs=self.buildings.crs,
        )
        self.projectionName = "Stereographic"

    def tearDown(self):
        pass

    def __plot(self, actual):
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        skymaps = STSkyMap25D(
            self.buildings,
            self.sensors,
            nRays=180,
            rayLength=100.0,
            elevationFieldname="HAUTEUR",
            h0=0,
            size=6.0,
            epsilon=0.01,
            projectionName=self.projectionName,
        ).run()

        STSunMap.plot(
            self.sensors,
            sunmaps=actual,
            buildings=self.buildings,
            skymaps=skymaps,
            roi=STBBox(actual, buffDist=7).run(),
        )

    def testRun(self):
        actual = STSunMap(
            self.sensors,
            dts=None,
            size=6.0,
            projectionName=self.projectionName,
            model="pvlib",
        ).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual((1 + 2 + 7 + 3) * len(self.sensors), len(actual), "Count rows")
        self.assertEqual(
            len(self.sensors.columns) + 4, len(actual.columns), "Count columns"
        )

        for cnt, filter in [
            (1, "circle"),
            (2, "axis"),
            (7, "analemma"),
            (3, "parallel"),
        ]:
            self.assertEqual(
                cnt * len(self.sensors),
                len(actual.query(f"__label__ == '{filter}'")),
                f"Count rows ({filter})",
            )

        # self.__plot(actual)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
