'''
Created on 11 mai 2021

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
from pandas.core.frame import DataFrame
from t4gpd.comfort.algo.ConstantsLib import ConstantsLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice


class TmrtRadiometer(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, SRUp='SR01Up_1_Avg', SRDn='SR01Dn_1_Avg',
                 SRright='SR01Up_2_Avg', SRleft='SR01Dn_2_Avg',
                 SRfront='SR01Up_3_Avg', SRback='SR01Dn_3_Avg',
                 IRUp='IR01UpCo_1_Avg', IRDn='IR01DnCo_1_Avg',
                 IRright='IR01UpCo_2_Avg', IRleft='IR01DnCo_2_Avg',
                 IRfront='IR01UpCo_3_Avg', IRback='IR01DnCo_3_Avg'):
        '''
        Constructor
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (SRUp, SRDn, SRright, SRleft, SRfront, SRback,
                          IRUp, IRDn, IRright, IRleft, IRfront, IRback):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.SRUp, self.SRDn = SRUp, SRDn
        self.SRright, self.SRleft = SRright, SRleft
        self.SRfront, self.SRback = SRfront, SRback

        self.IRUp, self.IRDn = IRUp, IRDn
        self.IRright, self.IRleft = IRright, IRleft
        self.IRfront, self.IRback = IRfront, IRback

    def runWithArgs(self, row):
        SRUp, SRDn = row[self.SRUp], row[self.SRDn]
        SRright, SRleft = row[self.SRright], row[self.SRleft]
        SRfront, SRback = row[self.SRfront], row[self.SRback]

        IRUp, IRDn = row[self.IRUp], row[self.IRDn] 
        IRright, IRleft = row[self.IRright], row[self.IRleft]
        IRfront, IRback = row[self.IRfront], row[self.IRback]

        # calculation of the mean flux density of radiation
        S_rad = (ConstantsLib.alpha_k * (
            ConstantsLib.F_vert * (SRUp + SRDn) + 
            ConstantsLib.F_lat * (SRright + SRleft + SRfront + SRback)) + 
            ConstantsLib.alpha_l * (
                ConstantsLib.F_vert * (IRUp + IRDn) + 
                ConstantsLib.F_lat * (IRright + IRleft + IRfront + IRback)))

        # 14.04.2021
        # Mean flux densities splitted in 6 directions according Kantor et al. (2016)
        _SRUp = (ConstantsLib.alpha_k * ConstantsLib.F_vert * SRUp)
        _SRDn = (ConstantsLib.alpha_k * ConstantsLib.F_vert * SRDn)
        _IRUp = (ConstantsLib.alpha_l * ConstantsLib.F_vert * IRUp)
        _IRDn = (ConstantsLib.alpha_l * ConstantsLib.F_vert * IRDn)
        _SRright = (ConstantsLib.alpha_k * ConstantsLib.F_lat * SRright)
        _SRleft = (ConstantsLib.alpha_k * ConstantsLib.F_lat * SRleft)
        _SRfront = (ConstantsLib.alpha_k * ConstantsLib.F_lat * SRfront)
        _SRback = (ConstantsLib.alpha_k * ConstantsLib.F_lat * SRback)
        _IRright = (ConstantsLib.alpha_l * ConstantsLib.F_lat * IRright)
        _IRleft = (ConstantsLib.alpha_l * ConstantsLib.F_lat * IRleft)
        _IRfront = (ConstantsLib.alpha_l * ConstantsLib.F_lat * IRfront)
        _IRback = (ConstantsLib.alpha_l * ConstantsLib.F_lat * IRback)
        _SRlat = (ConstantsLib.alpha_k * ConstantsLib.F_lat * (SRright + SRleft + SRfront + SRback))
        _IRlat = (ConstantsLib.alpha_l * ConstantsLib.F_lat * (IRright + IRleft + IRfront + IRback))

        # calculation of the mean radiant temperature [C]
        T_mrt = ((S_rad / (ConstantsLib.epsi_p * ConstantsLib.sigma_B)) ** (0.25) - ConstantsLib.T_kel)

        # T_mrt splitted in up, down and lateral IR and SR according to Middel and Krayenhoff (2019) and Kantor et al. (2016)
        _ratio = T_mrt / S_rad

        T_mrt_SRUp = _ratio * _SRUp
        T_mrt_SRDn = _ratio * _SRDn
        T_mrt_IRUp = _ratio * _IRUp
        T_mrt_IRDn = _ratio * _IRDn
        T_mrt_SRright = _ratio * _SRright
        T_mrt_SRleft = _ratio * _SRleft
        T_mrt_SRfront = _ratio * _SRfront
        T_mrt_SRback = _ratio * _SRback
        T_mrt_IRright = _ratio * _IRright
        T_mrt_IRleft = _ratio * _IRleft
        T_mrt_IRfront = _ratio * _IRfront
        T_mrt_IRback = _ratio * _IRback
        T_mrt_SRlat = _ratio * _SRlat
        T_mrt_IRlat = _ratio * _IRlat

        return { 
            'T_mrt': T_mrt,
            #
            'T_mrt_SRUp': T_mrt_SRUp,
            'T_mrt_SRDn': T_mrt_SRDn,
            'T_mrt_IRUp': T_mrt_IRUp,
            'T_mrt_IRDn': T_mrt_IRDn,
            #
            'T_mrt_SRright': T_mrt_SRright,
            'T_mrt_SRleft': T_mrt_SRleft,
            'T_mrt_SRfront': T_mrt_SRfront,
            'T_mrt_SRback': T_mrt_SRback,
            #
            'T_mrt_IRright': T_mrt_IRright,
            'T_mrt_IRleft': T_mrt_IRleft,
            'T_mrt_IRfront': T_mrt_IRfront,
            'T_mrt_IRback': T_mrt_IRback,
            #
            'T_mrt_SRlat': T_mrt_SRlat,
            'T_mrt_IRlat': T_mrt_IRlat
            }
