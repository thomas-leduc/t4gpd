'''
Created on 21 janv. 2021

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
from datetime import date, datetime, time, timedelta
import unittest

from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunLib import SunLib


class DatetimeLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGenerate1(self):
        dtStart = datetime(2021, 1, 21)
        dtStop = datetime(2021, 1, 31)
        dtStep = timedelta(days=1)

        result = DatetimeLib.generate([dtStart, dtStop, dtStep])

        self.assertIsInstance(result, dict, 'Is a dict')
        _key = list(result.keys())[0]
        self.assertEqual(11, len(result[_key]), 'Test length')
        for i, _dt in enumerate(result[_key]):
            self.assertIsInstance(_dt, datetime, 'Test return type')
            self.assertEqual(2021, _dt.year, 'Test year')
            self.assertEqual(1, _dt.month, 'Test month')
            self.assertEqual(21 + i, _dt.day, 'Test day')
            self.assertEqual(0, _dt.hour, 'Test hour')
            self.assertEqual(0, _dt.minute, 'Test minute')

    def testGenerate2(self):
        dt = date(2021, 1, 21)
        result = DatetimeLib.generate(dt)

        self.assertIsInstance(result, dict, 'Is a dict')
        self.assertEqual(32, len(result[str(dt)]), 'Test length')
        for _dt in result[str(dt)]:
            self.assertIsInstance(_dt, datetime, 'Test return type')
            self.assertEqual(2021, _dt.year, 'Test year')
            self.assertEqual(1, _dt.month, 'Test month')
            self.assertEqual(21, _dt.day, 'Test day')
            self.assertIn(_dt.hour, range(4, 20), 'Test hours')
            self.assertIn(_dt.minute, (0, 30), 'Test minutes')

    def testGenerate3(self):
        dt = time(12, 10)
        result = DatetimeLib.generate(dt)

        self.assertIsInstance(result, dict, 'Is a dict')
        self.assertEqual(36, len(result[str(dt)]), 'Test length')
        for _dt in result[str(dt)]:
            self.assertIsInstance(_dt, datetime, 'Test return type')
            self.assertIn(_dt.day, (1, 11, 21), 'Test days')
            self.assertEqual(12, _dt.hour, 'Test hours')
            self.assertEqual(10, _dt.minute, 'Test minutes')

    def testGenerate4(self):
        dt = [ date(2020, month, 21) for month in (3, 6, 12)]
        dt += [ time(hour) for hour in range(7, 18) ]
        result = DatetimeLib.generate(dt)

        self.assertIsInstance(result, dict, 'Is a dict')
        self.assertEqual(14, len(result), 'Test length')

        for _, v in result.items():
            self.assertIsInstance(v, list, 'Is a dict of list')
            for _v in v:
                self.assertIsInstance(_v, datetime, 'Is a dict of list of datetime')

    def testFromDatetimesDictToListOfSunPositions(self):
        dt = [date(2020, month, 21) for month in (6, 12)]
        sunModel = SunLib(gdf=LatLonLib.NANTES, model='pysolar')
        result = DatetimeLib.fromDatetimesDictToListOfSunPositions(dt, sunModel)

        self.assertIsInstance(result, list, 'Is a list')
        self.assertEqual(64, len(result), 'Test length')

        for _dt, _radDir, _solarAlti, _solarAzim in result:
            self.assertIsInstance(_radDir, tuple, 'radDir is a tuple')
            self.assertEqual(3, len(_radDir), 'radDir is a 3-uple')
            self.assertLess(AngleLib.toDegrees(_solarAlti), 70, 'Test solarAlti')
            self.assertTrue(0 <= AngleLib.toDegrees(_solarAzim) <= 360, 'Test solarAzim')

            if (12 == _dt.hour) and (0 == _dt.minute):
                if (6 == _dt.month):
                    self.assertAlmostEqual(70, AngleLib.toDegrees(_solarAlti), None,
                                           'Test solarAlti at noon (summer solstice)', 4)
                elif (12 == _dt.month):
                    self.assertAlmostEqual(20, AngleLib.toDegrees(_solarAlti), None,
                                           'Test solarAlti at noon (winter solstice)', 0.6)

    def testRange(self):
        dtStart = date(2022, 3, 1)
        dtStop = date(2022, 3, 1)
        result = DatetimeLib.range(dtStart, dtStop, dtDelta=timedelta(hours=6))
        self.assertIsInstance(result, list, 'DatetimeLib.range(...) is a list')
        self.assertEqual(4, len(result), 'DatetimeLib.range(...) is a 4-item list')
        for _dt in result:
            self.assertIsInstance(_dt, datetime, 'DatetimeLib.range(...) is a list of datetimes')
        self.assertListEqual([1, 1, 1, 1], [dt.day for dt in result], 'Test days')
        self.assertListEqual([0, 6, 12, 18], [dt.hour for dt in result], 'Test hours')
        self.assertListEqual([0, 0, 0, 0], [dt.minute for dt in result], 'Test minutes')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
