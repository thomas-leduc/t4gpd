'''
Created on 2 feb. 2021

@author: tleduc

Copyright 2020 Thomas Leduc

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
from t4gpd.comfort.indices.ASV import ASV
from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice


class EmpiricalThermalIndices(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg', WS_ms='WS_ms_Avg',
                 SRUp='SR01Up_1_Avg'):
        '''
        Constructor

        AirTC: air temperature [C]
        RH: relative humidity [%]
        Ws_ms: wind speed [m.s-1]
        SRUp: incoming shortwave radiation [W.m-2]
        '''
        self.ops = [
            ASV(sensorsGdf, AirTC, RH, WS_ms, SRUp)
            ]

    def runWithArgs(self, row):
        result = dict()
        for op in self.ops:
            result.update(op.runWithArgs(row))
        return result
