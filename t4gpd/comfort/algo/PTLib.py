'''
Created on 12 mai 2021

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
from t4gpd.comfort.algo.ConstantsLib import ConstantsLib
from t4gpd.comfort.algo.PMVLib import PMVLib


class PTLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def assess_pt(AirTC, RH, WS_ms, T_mrt):
        PMV = PMVLib.assess_pmv(AirTC, RH, WS_ms, T_mrt)

        # PT: Perceived Temperature
        # PT calculation based on clothing level, after (Coccolo et al., 2016)
        # The computation is based on the PMV for a standard pedestrian, called 
        # "Clima Michel", walking (135 W.m-2) and changing clothing according to 
        # the season:winter clothing (Icl equal to 1.75 clo) and summer clothing 
        # (Icl equal to 0.5 clo).
        PT = None

        if ((0 > PMV) and (ConstantsLib.Clo == 1.75)):
            PT = 5.805 + 12.6784 * PMV
        elif ((0 == PMV) and (0.5 < ConstantsLib.Clo < 1.75)):
            PT = 21.258 - 9.558 * ConstantsLib.Clo
        elif ((0 < PMV) and (0.5 == ConstantsLib.Clo)):
            PT = 16.826 + 6.183 * PMV

        return PT
