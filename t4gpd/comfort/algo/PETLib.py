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
from t4gpd.comfort.algo.CommonsLib import CommonsLib
from t4gpd.comfort.algo.ConstantsLib import ConstantsLib
from t4gpd.comfort.algo.VDI_PET_corrected import pet, system


class PETLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def assess_pet(AirTC, RH, WS_ms, T_mrt):
        M_activity = ConstantsLib.M  # [W]
        icl = ConstantsLib.Clo  # [clo]

        # Air pressure in Pascal and mPa
        _, P_air = CommonsLib.airPressure(AirTC, RH)

        Tair, Tmrt, v_air, pvap = AirTC, T_mrt, WS_ms, 10.0 * P_air

        tc, tsk, tcl, esw_real = system(Tair, Tmrt, pvap, v_air, M_activity, icl)
        tsk, enbal, esw, ed, PET, tcl = pet(tc, tsk, tcl, Tair, esw_real)

        return tsk, tc , tcl, PET
