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

from t4gpd.comfort.algo.SETLib import SETLib


class SETLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        '''
        Parsons, Ken C. 2003. Journal of Chemical Information and Modeling Human Thermal Environments: 
        The Effects of Hot, Moderate and Cold Environments on Human Health, Comfort and Performance. 
        2nd ed. London and New-York: Taylor & Francis.
        See p. 214, Table 8.8
        '''
        AirTC, RH, WS_ms, T_mrt = 30.0, 30.0, 0.25, 40.0
        SET = SETLib.assess_set(AirTC, RH, WS_ms, T_mrt)
        print('SET = %.2f' % (SET))
        self.assertAlmostEqual(31.3, SET, None, 'Test SET', 1e-3)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
