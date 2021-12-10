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


class TmrtOutLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def assess_tmrt_out(N, SR01Up_1, SR01Dn_1, IR01UpCo_1, IR01DnCo_1):
        SDIF, Idn = CommonsLib.SDIF_Idn(N, SR01Up_1)

        #=======================================================
        # Calculation of OUT_SET based on Watanabe et al. (2014)
 
        # net direct solar radiation to the body [W.m-2]
        dir_body = ConstantsLib.ah * ConstantsLib.fp * Idn
        # net diffuse solar radiation to the body [W.m-2]
        diff_body = (ConstantsLib.ah * ConstantsLib.alpha_eff 
                     * ((SDIF + SR01Dn_1) / 2))
        # net longwave to the body [W.m-2]
        longw_body = (ConstantsLib.alpha_l * ConstantsLib.alpha_eff
                      * ((IR01UpCo_1 + IR01DnCo_1) / 2))

        # OUT_MRT after Watanabe etal. (2014)
        Tmrt_OUT = ((dir_body + diff_body + longw_body)
                    / (ConstantsLib.alpha_l * ConstantsLib.alpha_eff
                       * ConstantsLib.sigma_B)) ** 0.25 - ConstantsLib.T_kel

        return Tmrt_OUT
