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
from numpy import exp
from pandas.core.frame import DataFrame
from t4gpd.comfort.algo.ConstantsLib import ConstantsLib
from t4gpd.comfort.algo.SET_mist import set_mist_optimized
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice


class SETmist(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg', WS_ms='WS_ms_Avg',
                 T_mrt='T_mrt'):
        '''
        Constructor

        AirTC: air temperature [C]
        RH: relative humidity [%]
        Ws_ms: wind speed recorded at pedestrian level (at height 1.1 m) [m.s-1]
        T_mrt: Mean radiant temperature [C]

        SETmist: Standard Effective Temperature, SET** for misting environment
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (AirTC, RH, WS_ms, T_mrt):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.AirTC = AirTC
        self.RH = RH
        self.WS_ms = WS_ms
        self.T_mrt = T_mrt

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        RH = row[self.RH]
        WS_ms = row[self.WS_ms]
        T_mrt = row[self.T_mrt]

        # saturated water pressure
        P_s = exp(16.6536 - (4030.183 / (AirTC + 235)))  # 1 torr = 101 325/760 Pascal
        vapor_pressure = RH * P_s / 100  # Pa

        # SETmist: Standard Effective Temperature, SET** for misting environment
        SETmist = set_mist_optimized(AirTC, T_mrt, WS_ms, RH, ConstantsLib.M_met,
                                     ConstantsLib.Clo, vapor_pressure,
                                     ConstantsLib.W_met,
                                     ConstantsLib.body_surface_area,
                                     ConstantsLib.patm,
                                     ConstantsLib.fa_eff,
                                     ConstantsLib.p_mist)

        return { 'SETmist': SETmist }
