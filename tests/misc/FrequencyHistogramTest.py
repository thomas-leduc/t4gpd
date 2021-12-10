'''
Created on 16 juin 2021

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
from random import randint, random, seed
import unittest

from pandas import DataFrame
from t4gpd.misc.FrequencyHistogram import FrequencyHistogram


class FrequencyHistogramTest(unittest.TestCase):

    def setUp(self):
        seed(123)
        self.nitems = 100
        self.maxValue = 100
        self.nClusters = 10
        self.df = DataFrame(data=[{'colA': randint(0, self.maxValue), 'colB': self.maxValue * random()}
                                  for _ in range(self.nitems)])

    def tearDown(self):
        pass

    def testRun1(self):
        result = FrequencyHistogram(self.df, ['colA', 'colB'], nClusters=self.nClusters, outputFile=None).run()
        self.assertIsInstance(result, list, 'Result is a list')
        self.assertEqual(2, len(result), 'Result is a pair of items')
        for _sublist in result:
            self.assertIsInstance(_sublist, list, 'Result is a list of list')
            self.assertEqual(self.nClusters, len(_sublist[0]), 'Test bins length')
            self.assertEqual(self.nClusters + 1, len(_sublist[1]), 'Test edges of the bins length')
            self.assertEqual(self.nitems, sum(_sublist[0]), 'Test the sum of the histogram bins')
            self.assertGreaterEqual(self.maxValue, max(_sublist[1]), 'Test the edges of the bins')

    def testRun2(self):
        result = FrequencyHistogram(self.df, ['colA', 'colB'], nClusters=self.nClusters,
                                    rangeValues=(30, 70), outputFile=None).run()
        self.assertIsInstance(result, list, 'Result is a list')
        self.assertEqual(2, len(result), 'Result is a pair of items')
        for _sublist in result:
            self.assertIsInstance(_sublist, list, 'Result is a list of list')
            self.assertEqual(self.nClusters, len(_sublist[0]), 'Test bins length')
            self.assertEqual(self.nClusters + 1, len(_sublist[1]), 'Test edges of the bins length')
            self.assertGreater(self.nitems, sum(_sublist[0]), 'Test the sum of the histogram bins')
            self.assertGreaterEqual(self.maxValue, max(_sublist[1]), 'Test the edges of the bins')

    def testRun3(self):
        result = FrequencyHistogram(self.df, ['colA', 'colB'], nClusters=self.nClusters,
                                    rangeValues=[(10, 40), (60, 90)], outputFile=None).run()
        self.assertIsInstance(result, list, 'Result is a list')
        self.assertEqual(2, len(result), 'Result is a pair of items')
        for _sublist in result:
            self.assertIsInstance(_sublist, list, 'Result is a list of list')
            self.assertEqual(self.nClusters, len(_sublist[0]), 'Test bins length')
            self.assertEqual(self.nClusters + 1, len(_sublist[1]), 'Test edges of the bins length')
            self.assertGreater(self.nitems, sum(_sublist[0]), 'Test the sum of the histogram bins')
            self.assertGreaterEqual(self.maxValue, max(_sublist[1]), 'Test the edges of the bins')

    def testRun4(self):
        result = FrequencyHistogram(self.df, ['colA', 'colB'], outputFile=None).run()
        self.assertIsInstance(result, list, 'Result is a list')
        self.assertEqual(2, len(result), 'Result is a pair of items')
        for _sublist in result:
            self.assertIsInstance(_sublist, list, 'Result is a list of list')
            self.assertEqual(8, len(_sublist[0]), 'Test bins length')
            self.assertEqual(8 + 1, len(_sublist[1]), 'Test edges of the bins length')
            self.assertEqual(self.nitems, sum(_sublist[0]), 'Test the sum of the histogram bins')
            self.assertGreaterEqual(self.maxValue, max(_sublist[1]), 'Test the edges of the bins')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
