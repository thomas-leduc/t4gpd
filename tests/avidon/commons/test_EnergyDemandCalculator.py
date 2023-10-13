'''
Created on 16 feb. 2022

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from datetime import datetime
from numpy import array
from t4gpd.avidon.commons.EnergyDemandCalculator import EnergyDemandCalculator


class EnergyDemandCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.dt = datetime(2022, 2, 16, 9, 21)
        self.C = array([10, 30, 15, 15, 10, 10, 8, 4])

    def tearDown(self):
        pass

    def testRunWithArgs(self):
        result = EnergyDemandCalculator().energyDemandOfITEquipment(self.C, self.dt)
        self.assertEqual(2263.152, result, 'Test energy demand')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
