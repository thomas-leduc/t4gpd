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
from t4gpd.picoclim.SensirionReader import SensirionReader


class SensirionReaderTest(unittest.TestCase):

    def setUp(self):
        self.V1 = StringIO("""# EdfVersion=4.0
# Date=2022-07-11T18:49:50.435746
# ApplicationName=Sensirion_MyAmbience
# ApplicationVersion=2.4.4 (50)
# OperatingSystem=ios
# SensorFamily=SHT40 Gadget
# SensorId=0F:0E
# SensorName=SHT40 Gadget 0F:0E
# Type=float64,Format=.3f,Unit=s    Type=string    Product=SHT40 Gadget,Device=SHT40 Gadget,Unit=°C,Sensor_Serial_Number=0F:0E,Type=float,Signal=Temperature    Product=SHT40 Gadget,Device=SHT40 Gadget,Unit=%RH,Sensor_Serial_Number=0F:0E,Type=float,Signal=Relative Humidity
Epoch_UTC    Local_Date_Time    T    RH
1656418510.2    2022-06-28T14:15:10.158880    24.770    41.257
1656418511.6    2022-06-28T14:15:11.642124    24.760    41.333
1656418517.6    2022-06-28T14:15:17.648058    24.784    41.311
1656418531.7    2022-06-28T14:15:31.694423    24.776    41.335
1656418537.7    2022-06-28T14:15:37.713030    24.760    41.290
""")

    def tearDown(self):
        pass

    def testRunV1(self):
        df = SensirionReader(self.V1).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(6, len(df.columns), "Count columns")
        self.assertEqual(5, len(df), "Count rows")
        self.assertTrue(df.timestamp.is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamp.is_unique, "The timestamps are strictly increasing")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
