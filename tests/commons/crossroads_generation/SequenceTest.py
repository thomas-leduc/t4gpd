'''
Created on 8 nov. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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

from t4gpd.commons.crossroads_generation.Sequence import Sequence


class SequenceTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGetMinModel(self):
        actual = Sequence(nbranchs=8, seq=[0, 2, 4]).getMinModel()
        self.assertEqual(4, actual, 'Test getMinModel method (1)')

        actual = Sequence(nbranchs=16, seq=[0, 4, 12]).getMinModel()
        self.assertEqual(4, actual, 'Test getMinModel method (2)')

        actual = Sequence(nbranchs=16, seq=[0, 2, 4]).getMinModel()
        self.assertEqual(8, actual, 'Test getMinModel method (3)')

    def testMirror(self):
        actual = Sequence(nbranchs=4, seq=[0, 1, 2]).mirror()
        expected = Sequence(nbranchs=4, seq=[0, 2, 3])
        self.assertEqual(actual, expected, 'Test mirror method (1)')

        actual = Sequence(nbranchs=8, seq=[0, 1, 2, 3, 5]).mirror()
        expected = Sequence(nbranchs=8, seq=[0, 3, 5, 6, 7])
        self.assertEqual(actual, expected, 'Test mirror method (2)')

    def testRotate(self):
        actual = Sequence(nbranchs=4, seq=[0, 1, 2]).rotate(offset=1)
        expected = Sequence(nbranchs=4, seq=[1, 2, 3])
        self.assertEqual(actual, expected, 'Test rotate method (1)')

        actual = Sequence(nbranchs=8, seq=[0, 1, 2, 3, 5]).rotate(offset=1)
        expected = Sequence(nbranchs=8, seq=[1, 2, 3, 4, 6])
        self.assertEqual(actual, expected, 'Test rotate method (2)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
