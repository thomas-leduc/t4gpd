"""
Created on 10 mar. 2025

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

from numpy.random import default_rng
from scipy.stats import entropy
from t4gpd.commons.Entropy import Entropy


class EntropyTest(unittest.TestCase):

    def setUp(self):
        rng = default_rng(1234)
        self.int_values = [1] * 5 + [3] * 12 + [4] * 33
        self.double_values = [1.25] * 5 + [3.25] * 12 + [4.25] * 33
        self.string = f"{'a' * 5}{'c' * 12}{'d' * 33}"

    def tearDown(self):
        pass

    def testCreateFromDoubleValuesArray(self):
        actual = Entropy.createFromDoubleValuesArray(self.double_values).probs.tolist()
        expected = [5 / (5 + 12 + 33), 12 / (5 + 12 + 33), 33 / (5 + 12 + 33)]
        self.assertListEqual(expected, actual, "Test probabilities")

    def testCreateFromIntValuesArray(self):
        actual = Entropy.createFromIntValuesArray(self.int_values).probs.tolist()
        expected = [5 / (5 + 12 + 33), 12 / (5 + 12 + 33), 33 / (5 + 12 + 33)]
        self.assertListEqual(expected, actual, "Test probabilities")

    def testCreateFromString(self):
        actual = Entropy.createFromString(self.string).probs.tolist()
        expected = [5 / (5 + 12 + 33), 12 / (5 + 12 + 33), 33 / (5 + 12 + 33)]
        self.assertListEqual(expected, actual, "Test probabilities")

    def testH(self):
        actual = Entropy.createFromIntValuesArray(self.int_values).h()
        expected = entropy([5 / (5 + 12 + 33), 12 / (5 + 12 + 33), 33 / (5 + 12 + 33)])
        self.assertEqual(expected, actual, "Test entropy")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
