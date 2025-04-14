"""
Created on 12 mar. 2025

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
from io import StringIO
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.demos.NantesBDT import NantesBDT
from t4gpd.indices.BufferIndices import BufferIndices
from t4gpd.morph.STBBox import STBBox


class BufferIndicesTest(unittest.TestCase):
    def setUp(self):
        _sio = StringIO(
            """,project_id,track_id,section_id,segment_id,point_id,section_duration,section_speed,section_warning,gnss_accuracy,section_weather,timestamp,lon_ontrack,lat_ontrack,lon_rtk,lat_rtk,sun_azimuth,sun_height,tair_thermohygro,tair_tc1,tair_tc2,tair_anemo,rh_thermohygro,ws,wdir,sw_up,sw_down,sw_front,sw_back,sw_left,sw_right,lw_up,lw_down,lw_front,lw_back,lw_left,lw_right,tmrt,pet,geometry
3629,picopatt_nantes,centre,47,82,3630,41.0,0.536274305764499,car,1233,veiledsun:partialsun,2025-01-20 15:49:29+01:00,-1.55646157155677,47.2169678714025,-1.5564471,47.2170246,204.390877576444,19.0246352915895,2.99114976729992,2.9140625,2.9140625,4,80.5758754863813,0.4115552,100,53.3219036843662,0.0,44.7869621261313,19.1099416744639,6.64406641054945,41.2338204662586,301.126384991691,351.067689474579,341.815422760936,349.540376849077,354.816147893877,342.983768778524,10.0661755820822,2.63848928729992,POINT (355352.42577205255 6689576.77557399)
142,picopatt_nantes,centre,2,2,143,112.0,0.66525595382952,,113,clouds,2025-01-20 14:33:00+01:00,-1.55584656766483,47.2164598870751,-1.5557576,47.2164609,185.548254536132,22.3762556692673,2.37697413595788,2.3984375,2.421875,4,81.0355535210193,0.0,271,43.4111375106737,0.0,21.1075540909236,14.8135503308237,0.0,10.1422417333414,349.676504438116,356.373852300118,358.994550989398,357.705645775113,364.5837634611,360.984169452336,10.8498431583173,7.89281669595788,POINT (355395.6388483966 6689517.759555683)
1367,picopatt_nantes,centre,20,36,1368,154.0,0.695777827139076,,117,clouds,2025-01-20 15:02:06+01:00,-1.55996717222325,47.2155421519171,-1.5599841,47.2155185,192.859666395393,21.5907361973788,2.80422674906538,2.6484375,2.5703125,4,79.8949416342412,0.9774436,0,73.656736869423,0.0,36.0233502415836,33.1346730154363,22.2347321790138,13.0510834516386,346.959615737925,357.410725646895,359.725637784689,358.644399014959,360.355969858574,367.415326058385,13.0059645613559,1.35690514906538,POINT (355078.418988138 6689433.980588855)
4646,picopatt_nantes,centre,58,119,4647,50.0,0.702140377784918,,1586,veiledsun,2025-01-20 16:10:26+01:00,-1.55841316580772,47.2157001074503,-1.5582988,47.2157073,209.281542150889,17.4227339717379,2.79888609140153,2.7578125,2.828125,3,81.7851529716945,1.8519984,161,39.862498386204,0.0,29.678516111197,11.5060686476312,4.11589743088453,9.19914742698043,336.055958898789,357.40073712427,355.062939797746,356.030340110373,358.989016031838,365.246999536567,10.6385551130045,-0.940889908598465,POINT (355196.8476428393 6689444.709696048)
3568,picopatt_nantes,centre,46,81,3569,94.0,0.66339826105371,,1395,veiledsun:partialsun,2025-01-20 15:48:17+01:00,-1.55596718192101,47.2170094710634,-1.5559194,47.21704,204.10648258767,19.1081045039978,3.01785305561914,2.8984375,2.8984375,4,80.5510795757992,2.0063316,328,37.1654939848774,0.0,27.1788515065731,14.1529945913547,0.0,12.0146688240372,313.053527921193,352.654827345228,344.015780533738,351.06086065235,362.828126154969,352.273431924029,9.18086634914187,-1.28343334438086,POINT (355390.0460132618 6689579.2309379615)
"""
        )
        self.sensors = GeoDataFrameLib.read_csv(_sio, sep=",", index_col=0)
        self.buildings = NantesBDT.buildings(STBBox(self.sensors, 100).run())

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1.75 * 8.26, 8.26))
        self.buildings.plot(ax=ax, color="lightgrey", edgecolor="dimgrey")
        self.sensors.plot(ax=ax, marker="P")
        result.plot(ax=ax, column="bsf", marker="o", legend=True)
        # result.plot(ax=ax, column="hre", marker="o", legend=True)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        actual = BufferIndices.indices(
            self.sensors, self.buildings, buffDist=100, merge_by_index=False
        )
        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.sensors), len(actual), "Count rows")
        self.assertEqual(2, len(actual.columns), "Count columns")
        self.assertIn("bsf", actual.columns, "Check 'bsf' column")
        self.assertIn("hre", actual.columns, "Check 'hre' column")

    def testRun2(self):
        actual = BufferIndices.indices(
            self.sensors, self.buildings, buffDist=100, merge_by_index=True
        )
        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.sensors), len(actual), "Count rows")
        self.assertEqual(
            len(self.sensors.columns) + 2, len(actual.columns), "Count columns"
        )
        self.assertIn("bsf", actual.columns, "Check 'bsf' column")
        self.assertIn("hre", actual.columns, "Check 'hre' column")
        self.__plot(actual)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
