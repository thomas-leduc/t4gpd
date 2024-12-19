'''
Created on 23 aug. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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

from datetime import datetime, timedelta, timezone
from geopandas import GeoDataFrame
from shapely import box
from shapely.wkt import loads
from t4gpd.commons.overlap.OverlapLib import OverlapLib


class OverlapLibTest(unittest.TestCase):

    def setUp(self):
        self.dt0 = datetime(2024, 8, 23, 12, tzinfo=timezone.utc)
        self.gdf = GeoDataFrame([
            {"gid": 100+i, "geometry": box(0, 0, i, i),
             "timestamp": (self.dt0 + timedelta(hours=i)).time()}
            for i in range(1, 4)
        ])

    def tearDown(self):
        pass

    def testOverlap(self):
        result = OverlapLib.overlap(
            self.gdf, ["gid", "timestamp"], patchid="patch_id")
        print(result)
        result.to_csv("/tmp/1.csv", index=False)

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(3, len(result), "Count rows")
        self.assertEqual(5, len(result.columns), "Count columns")

        t1, t2, t3 = [(self.dt0 + timedelta(hours=i)).time()
                      for i in range(1, 4)]
        p_id_0 = loads("POLYGON ((1 0, 1 1, 0 1, 0 2, 2 2, 2 0, 1 0))")
        p_id_1 = loads("POLYGON ((0 1, 1 1, 1 0, 0 0, 0 1))")
        p_id_2 = loads("POLYGON ((2 0, 2 2, 0 2, 0 3, 3 3, 3 0, 2 0))")

        expected = GeoDataFrame([
            {"patch_id": 0, "gid": [102, 103], "timestamp": [
                t2, t3], "noverlays": 2, "geometry": p_id_0},
            {"patch_id": 1, "gid": [101, 102, 103], "timestamp": [
                t1, t2, t3], "noverlays": 3, "geometry": p_id_1},
            {"patch_id": 2, "gid": [103], "timestamp": [
                t3], "noverlays": 1, "geometry": p_id_2},
        ])
        self.assertTrue(expected.equals(result), "GeoDataFrame equality")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
