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
from t4gpd.comfort.algo.TmrtGlobeTemperatureLib import TmrtGlobeTemperatureLib


class TmrtGlobeTemperatureLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAssess_tmrt(self):
        '''
        Davtalab, Jamshid et al. 2020. "The Impact of Green Space Structure on Physiological 
        Equivalent Temperature Index in Open Space." Urban Climate 31 (October 2019): 100574. 
        https://doi.org/10.1016/j.uclim.2019.100574.

        see Table 3, location A1      
        '''
        AirTC, GlobeTC, WS_ms = 39.53, 42.04, 0.99
        T_mrt = TmrtGlobeTemperatureLib.assess_tmrt(
            AirTC, GlobeTC, WS_ms, GlobeEmissivity=0.95, GlobeDiameter=0.75)
        print('T_mrt = %.2f' % T_mrt)
        self.assertAlmostEqual(42.42, T_mrt, None, 'Test T_mrt', 2.18)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
