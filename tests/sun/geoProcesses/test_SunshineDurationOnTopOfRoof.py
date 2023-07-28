'''
Created on 3 mars 2021

@author: tleduc

Copyright 2020 Thomas Leduc

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
from datetime import datetime, timezone
import unittest

from geopandas.geodataframe import GeoDataFrame
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.sun.geoProcesses.SunshineDurationOnTopOfRoof import SunshineDurationOnTopOfRoof


class SunshineDurationOnTopOfRoofTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

        _roi = self.buildings[self.buildings.ID == 'BATIMENT0000000302929767']
        _roi.reset_index(drop=True, inplace=True)
        self.sensors = STGrid(_roi, 2, dy=None, indoor=True, intoPoint=True).run()

        # Grande Braderie - 29 et 30 mars 2019
        self.givenDatetime = [
            datetime(2019, 3, 29, _h, _m, tzinfo=timezone.utc) for _m in (17, 47) for _h in range(4, 21)
            ]

    def tearDown(self):
        pass

    def testRun(self):
        op = SunshineDurationOnTopOfRoof(self.buildings, 'HAUTEUR', self.givenDatetime, model='pysolar')
        # op = SunshineDurationOnTopOfRoof(self.buildings, 'HAUTEUR', self.givenDatetime, model='solene')
        result = STGeoProcess(op, self.sensors).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(37, len(result), 'Count rows')
        self.assertEqual(9, len(result.columns), 'Count columns')

        nMaxSunHits = len(self.givenDatetime)
        for _, row in result.iterrows():
            self.assertIn(row['sun_hits'], range(0, nMaxSunHits), 'Test sun_hits attribute values')
            self.assertTrue(0 <= row['sun_ratio'] <= 1, 'Test sun_ratio attribute values')

        '''
        import matplotlib.pyplot as plt
        my_map_base = self.buildings.boundary.plot(edgecolor='black', linewidth=0.3)
        result.plot(ax=my_map_base, edgecolor='dimgrey', linewidth=0.3, column='sun_hits',
                    legend=True, cmap='plasma')
        plt.show()
        # result.to_file('/tmp/xxx.shp')
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
