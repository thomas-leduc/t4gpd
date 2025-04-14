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
from geopandas import GeoDataFrame, clip
from shapely import Polygon
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.sun.STTreeHardShadow import STTreeHardShadow


class STTreeHardShadowTest(unittest.TestCase):

    def setUp(self):
        self.trees = GeoDataFrameDemos.districtGraslinInNantesTrees()

        roi = GeoDataFrameDemos.coursCambronneInNantes()
        self.trees = clip(self.trees, roi)
        # self.trees = self.trees[self.trees.osm_id == 1961183678]

        ids = [
            "1937451436",
            "1937451458",
            "1937451469",
            "1937451497",
            "1937451525",
            "1937451548",
            "1937451563",
            "1937451582",
        ]

        h1, a1 = 15.0, 5.0
        h2, a2 = 9.0, 3.0
        self.trees["h_arbre"] = self.trees.osm_id.apply(
            lambda _id: h1 if _id in ids else h2
        )
        self.trees["r_houppier"] = self.trees.osm_id.apply(
            lambda _id: a1 if _id in ids else a2
        )

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
        self.trees.plot(ax=ax, color="red")
        roi = GeoDataFrameDemos.coursCambronneInNantes()
        roi.boundary.plot(ax=ax, color="red", linewidth=0.5)
        result.plot(ax=ax, column="datetime", alpha=0.5, legend=True)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STTreeHardShadow(
            self.trees,
            self.datetimes,
            treeHeightFieldname="h_arbre",
            treeCrownRadiusFieldname="r_houppier",
            altitudeOfShadowPlane=0.0,
            aggregate=False,
            tz=timezone.utc,
            model="pysolar",
            npoints=32,
        ).run()

        datetimes = [str(dt) for dt in list(self.datetimes.values())[0]]

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(3 * len(self.trees), len(result), "Count rows")
        self.assertEqual(5, len(result.columns), "Count columns")
        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Is a GeoDataFrame of Polygons"
            )
            self.assertIn(row.datetime, datetimes, "Datetime test")

        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
