'''
Created on 3 dec. 2024

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

from datetime import datetime, timezone
from geopandas import GeoDataFrame
from numpy import cos, deg2rad
from pandas import DataFrame, date_range
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.energy.PvlibProxy import PvlibProxy


class PvlibProxyTest(unittest.TestCase):

    def setUp(self):
        dt0 = datetime(2024, 12, 21, 8, tzinfo=timezone.utc)
        dt1 = datetime(2024, 12, 21, 16, tzinfo=timezone.utc)
        dts = date_range(start=dt0, end=dt1, freq="1h")
        geom = LatLonLib.NANTES.loc[0, "geometry"]
        self.gdf = GeoDataFrame({
            "timestamp": dts,
            "geometry": [geom]*len(dts)
        }, crs="epsg:4326")

    def tearDown(self):
        pass

    def testGet_ghi_dni_dhi_positions(self):
        actual = PvlibProxy.get_ghi_dni_dhi_positions(self.gdf, "timestamp")

        self.assertIsInstance(actual, DataFrame, "Is a DataFrame")
        self.assertEqual(len(self.gdf), len(actual), "Count rows")
        self.assertEqual(10, len(actual.columns), "Count columns")
        print(actual.apparent_elevation)

        for _, row in actual.iterrows():
            self.assertTrue(126 < row.azimuth < 232, "Check azimuths")
            # The Earth's axis is tilted about 23.5 degrees from the plane
            # of its orbit around the sun. But this tilt changes.
            self.assertTrue(0 < row.apparent_elevation < 90 - 47.2 - 23.4,
                            "Check apparent_elevation")
            self.assertTrue(0 < row.elevation, "Check elevation")

            ghi = row.dhi + cos(deg2rad(90-row.apparent_elevation)) * row.dni
            self.assertEqual(
                row.ghi, ghi, "Check ghi, dhi, dni and apparent_elevation")

    def testAppend_ghi_dni_dhi_positions(self):
        actual = PvlibProxy.append_ghi_dni_dhi_positions(self.gdf, "timestamp")

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.gdf), len(actual), "Count rows")
        self.assertEqual(11, len(actual.columns), "Count columns")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
