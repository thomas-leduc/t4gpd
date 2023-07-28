'''
Created on 7 janv. 2021

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
import unittest
from t4gpd.commons.ArrayCoding import ArrayCoding
from numpy import array


class ArrayCodingTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEncode(self):
        self.assertEqual('123', ArrayCoding.encode(123), 'Test encode ouput (1)')
        self.assertEqual('12.3', ArrayCoding.encode(12.3), 'Test encode ouput (2)')
        self.assertEqual('123#12.3', ArrayCoding.encode((123, 12.3)), 'Test encode ouput (3)')
        self.assertEqual('123#12.3', ArrayCoding.encode([123, 12.3]), 'Test encode ouput (4)')
        self.assertEqual('123#12.3', ArrayCoding.encode({123, 12.3}), 'Test encode ouput (5)')
        self.assertEqual('123#12.3', ArrayCoding.encode({123: 'a', 12.3: 'b'}), 'Test encode ouput (6)')
        self.assertEqual('123.0#12.3', ArrayCoding.encode(array([123, 12.3])), 'Test encode ouput (7)')

    def testDecode(self):
        self.assertEqual([123, 12.3], ArrayCoding.decode('123#12.3'), 'Test decode ouput (1)')
        self.assertEqual([123, 12.3], ArrayCoding.decode('123:12.3', separator=':'), 'Test decode ouput (2)')
        self.assertEqual(['123', '12.3'], ArrayCoding.decode('123#12.3', outputType=str), 'Test decode ouput (3)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
