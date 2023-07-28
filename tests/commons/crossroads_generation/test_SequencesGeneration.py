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
from t4gpd.commons.crossroads_generation.SequencesGeneration import SequencesGeneration


class SequencesGenerationTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun(self):
        quadruples = [
            (False, True, False, 5),
            (False, False, True, 8),
            (False, True, True, 13),
            #
            (True, True, False, 5),
            (True, False, True, 7),
            (True, True, True, 12),
            ]
        for m, wB, wS, nitems in quadruples:
            result = SequencesGeneration(nbranchs=4, mirror=m, withBranchs=wB, withSectors=wS).run()
            self.assertIsInstance(result, dict, 'Test the type of result')
            self.assertEqual(nitems, len(result), 'Test the length of result')
            self.assertTrue(all([isinstance(v, Sequence) for v in result.values()]),
                            'The result is a dictionary where the values are Sequence')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
