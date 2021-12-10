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
from numpy import isnan
from pandas.core.frame import DataFrame
from t4gpd.comfort.algo.SETLib import SETLib
from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class OUTSET(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg', WS_ms='WS_ms_Avg',
                 Tmrt_OUT='Tmrt_OUT'):
        '''
        Constructor

        AirTC: air temperature [C]
        RH: relative humidity [%]
        Ws_ms: wind speed recorded at pedestrian level (at height 1.1 m) [m.s-1]
        Tmrt_OUT: Outdoor Mean radiant temperature [C]

        SET: Standard Effective Temperature
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (AirTC, RH, WS_ms, Tmrt_OUT):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.AirTC = AirTC
        self.RH = RH
        self.WS_ms = WS_ms
        self.Tmrt_OUT = Tmrt_OUT

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        RH = row[self.RH]
        WS_ms = row[self.WS_ms]
        Tmrt_OUT = row[self.Tmrt_OUT]

        if Tmrt_OUT is None:
            return { 'OUT_SET': None }

        # OUT_SET: Outdoor Standard Effective Temperature 
        OUT_SET = SETLib.assess_set(AirTC, RH, WS_ms, Tmrt_OUT)

        return { 'OUT_SET': OUT_SET }
