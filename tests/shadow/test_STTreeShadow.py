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
from geopandas import GeoDataFrame, clip
from matplotlib.colors import ListedColormap
from pandas import Timestamp
from shapely import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.shadow.STTreeShadow import STTreeShadow


class STTreeShadowTest(unittest.TestCase):

    def setUp(self):
        self.trees = GeoDataFrameDemos.districtGraslinInNantesTrees()

        roi = GeoDataFrameDemos.coursCambronneInNantes()
        self.trees = clip(self.trees, roi)

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
            Timestamp(f"2025-07-21 {h}:00", tz="Europe/Paris").tz_convert("UTC")
            for h in [9, 12, 15]
        ]

    def tearDown(self):
        pass

    def __plot(self, actual):
        actual.datetime = actual.datetime.apply(lambda dt: dt.strftime("%H:%M"))
        my_cmap = ListedColormap(["red", "green", "blue"])

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.trees.plot(ax=ax, color="red")
        roi = GeoDataFrameDemos.coursCambronneInNantes()
        roi.boundary.plot(ax=ax, color="red", linewidth=0.5)
        actual.plot(ax=ax, column="datetime", cmap=my_cmap, alpha=0.5, legend=True)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STTreeShadow(
            self.trees,
            self.datetimes,
            treeHeightFieldname="h_arbre",
            treeCrownRadiusFieldname="r_houppier",
            altitudeOfShadowPlane=0.0,
            aggregate=False,
            model="pvlib",
            npoints=32,
        ).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(3 * len(self.trees), len(result), "Count rows")
        self.assertEqual(5, len(result.columns), "Count columns")
        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Is a GeoDataFrame of Polygons"
            )
            self.assertIn(row.datetime, self.datetimes, "Datetime test")

        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
