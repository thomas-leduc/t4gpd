'''
Created on 17 mai 2021

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
import unittest

from t4gpd.comfort.algo.PMVLib import PMVLib


class PMVLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAssess_pmv(self):
        AirTC, RH, WS_ms, T_mrt = 29.53, 10.83, 0.99, 32.42
        PMV = PMVLib.assess_pmv(AirTC, RH, WS_ms, T_mrt)
        print('PMV = %.2f' % (PMV))
        # self.assertAlmostEqual(XXX, PMV, None, 'Test PMV', XXX)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
