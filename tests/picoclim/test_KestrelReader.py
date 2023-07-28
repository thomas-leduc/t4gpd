'''
Created on 29 avr. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from io import StringIO
import unittest

from pandas import DataFrame
from t4gpd.picoclim.KestrelReader import KestrelReader


class KestrelReaderTest(unittest.TestCase):

    def setUp(self):
        self.V1 = StringIO("""Device Name,HEAT - 2414248
Device Model,5400CL
Serial Number,2414248
FORMATTED DATE-TIME,Direction – True,Wind Speed,Crosswind Speed,Headwind Speed,Temperature,Globe Temperature,Wind Chill,Relative Humidity,Heat Stress Index,Dew Point,Psychro Wet Bulb Temperature,Station Pressure,Barometric Pressure,Altitude,Density Altitude,NA Wet Bulb Temperature,WBGT,￼TWL,Direction – Mag
YYYY-MM-DD HH:MM:SS,°,m/s,m/s,m/s,°C,°C,°C,%,°C,°C,°C,mb,mb,m,m,°C,°C,w/m^2 ,°
2020-05-18 11:39:50,7,"0,7","0,1","0,7","21,5","35,2","21,5","41,1","20,8","7,7","13,6","1027,0","1028,0",8,132,"16,3","20,4","271,9",7
2020-05-18 11:40:00,26,"1,4","0,7","1,2","21,4","34,8","21,4","40,4","20,5","7,4","13,5","1027,0","1028,0",8,128,"16,4","20,5","274,7",26
2020-05-18 11:40:10,352,"1,0","0,2","1,0","20,6","34,6","20,6","39,8","19,3","6,5","12,8","1027,0","1028,0",8,98,"16,4","20,5","276,2",351
2020-05-18 11:40:20,57,"0,8","0,7","0,4","21,2","34,6","21,2","39,8","20,2","7,0","13,2","1026,9","1028,0",8,122,"16,4","20,5","275,8",57
2020-05-18 11:40:30,17,"0,5","0,2","0,5","21,6","34,5","21,6","40,0","20,7","7,5","13,6","1026,9","1028,0",8,137,"16,6","20,6","275,1",16
""")
        self.V2 = StringIO("""Device Name,HEAT - 2414248
Device Model,5400CL
Serial Number,2414248
FORMATTED DATE_TIME,Temperature,Wet Bulb Temp,Globe Temperature,Relative Humidity,Barometric Pressure,Altitude,Station Pressure,Wind Speed,Heat Index,Dew Point,Density Altitude,Crosswind,Headwind,Compass Magnetic Direction,NWB Temp,Compass True Direction,Thermal Work Limit,Wet Bulb Globe Temperature,Wind Chill
yyyy-MM-dd hh:mm:ss a,°C,°C,°C,%,mb,m,mb,km/h,°C,°C,m,km/h,km/h,Deg,°C,Deg,w/m2,°C,°C,Data Type,Record name,Start time,Duration (H:M:S),Location description,Location address,Location coordinates,Notes
2022-06-20 05:14:48 PM,28.9,20.2,31.5,45.7,1019.2,39,1012.0,0.0,29.2,16.0,572,--,--,--,20.5,--,194.6,23.3,28.9,point,,,,PHONE/TABLET LOCATION,"22 Rue Federico Garcia Lorca, 44400 Rezé, France","https://www.google.com/maps/search/?api=1&query=47.1926611,-1.5481433",
2022-06-20 05:14:50 PM,29.0,20.3,31.4,45.5,1019.2,39,1012.0,0.0,29.2,16.0,574,--,--,--,20.5,--,194.7,23.3,28.9,point,,,,PHONE/TABLET LOCATION,"22 Rue Federico Garcia Lorca, 44400 Rezé, France","https://www.google.com/maps/search/?api=1&query=47.1926611,-1.5481433",
2022-06-20 05:14:52 PM,29.0,20.3,31.4,45.5,1019.2,39,1012.0,0.0,29.4,16.1,575,--,--,--,20.5,--,194.8,23.3,29.0,point,,,,PHONE/TABLET LOCATION,"22 Rue Federico Garcia Lorca, 44400 Rezé, France","https://www.google.com/maps/search/?api=1&query=47.1926611,-1.5481433",
2022-06-20 05:14:54 PM,29.1,20.4,31.4,45.5,1019.4,39,1012.1,0.0,29.4,16.1,577,--,--,--,20.5,--,194.8,23.3,29.0,point,,,,PHONE/TABLET LOCATION,"22 Rue Federico Garcia Lorca, 44400 Rezé, France","https://www.google.com/maps/search/?api=1&query=47.1926611,-1.5481433",
2022-06-20 05:14:56 PM,29.1,20.4,31.4,45.5,1019.4,39,1012.1,0.0,29.6,16.2,580,--,--,--,20.5,--,194.9,23.3,29.1,point,,,,PHONE/TABLET LOCATION,"22 Rue Federico Garcia Lorca, 44400 Rezé, France","https://www.google.com/maps/search/?api=1&query=47.1926611,-1.5481433",
""")

    def tearDown(self):
        pass

    def testRunV1(self):
        df = KestrelReader(self.V1).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(21, len(df.columns), "Count columns")
        self.assertEqual(5, len(df), "Count rows")
        self.assertTrue(df.timestamp.is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamp.is_unique, "The timestamps are strictly increasing")

    def testRunV2(self):
        df = KestrelReader(self.V2).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(22, len(df.columns), "Count columns")
        self.assertEqual(5, len(df), "Count rows")
        self.assertTrue(df.timestamp.is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamp.is_unique, "The timestamps are strictly increasing")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
