'''
Created on 15 dec. 2020

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
from t4gpd.commons.ColorTemperature import ColorTemperature


class ColorTemperatureTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConvert_K_to_RGB(self):
        result = ColorTemperature.convert_K_to_RGB(2850)
        self.assertIsInstance(result, tuple, 'Is a tuple')
        self.assertEqual((255, 172, 99), result,
                         'Is equal to (255, 172, 99)')

        result = ColorTemperature.convert_K_to_RGB(5400)
        self.assertIsInstance(result, tuple, 'Is a tuple')
        self.assertEqual((255, 236, 219), result,
                         'Is equal to (255, 236, 219)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
