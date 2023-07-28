'''
Created on 17 mai 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from t4gpd.comfort.indices.SETmist import SETmist
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from geopandas.geodataframe import GeoDataFrame


class SETmistTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun(self):
        AirTC, RH, WS_ms, T_mrt = 30.0, 30.0, 0.25, 40.0
        sensorsGdf = GeoDataFrame(data=[{
            'AirTC_Avg': AirTC,
            'RH_Avg': RH,
            'WS_ms_Avg': WS_ms,
            'T_mrt': T_mrt,
            'geometry': None
            }])
        op = SETmist(sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg',
                     WS_ms='WS_ms_Avg', T_mrt='T_mrt')
        result = STGeoProcess(op, sensorsGdf).run()
        result = result.SETmist.squeeze()
        print('SETmist = %.3f' % result)
        self.assertAlmostEqual(30.772, result, None, 'Test SETmist', 1e-3)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
