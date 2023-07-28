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

from t4gpd.comfort.algo.PETLib import PETLib


class PETLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAssess_pet(self):
        '''
        Davtalab, Jamshid et al. 2020. "The Impact of Green Space Structure on Physiological 
        Equivalent Temperature Index in Open Space." Urban Climate 31 (October 2019): 100574. 
        https://doi.org/10.1016/j.uclim.2019.100574.

        see Table 3, location A1
        '''
        AirTC, RH, WS_ms, T_mrt = 39.53, 10.83, 0.99, 42.42
        # _, _, _, PET = PETLib.assess_pet(AirTC, RH, WS_ms, T_mrt)
        Tsk_PET, Tc_PET, Tcl_PET, PET = PETLib.assess_pet(AirTC, RH, WS_ms, T_mrt)
        print('Tsk_PET = %.2f, Tc_PET = %.2f, Tcl_PET = %.2f, PET = %.2f' % (Tsk_PET, Tc_PET, Tcl_PET, PET))
        self.assertAlmostEqual(41.35, PET, None, 'Test PET', 1.22)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
