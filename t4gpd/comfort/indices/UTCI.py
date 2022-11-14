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
from numpy import isnan
from pandas.core.frame import DataFrame
from t4gpd.comfort.algo.UTCILib import UTCILib
from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class UTCI(AbstractThermalComfortIndice):
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

    @staticmethod
    def thermalPerceptionRanges():
        # Excerpt from https://doi.org/10.1016/j.wace.2018.01.004
        return {
            'Extreme cold': { 'min':-float('inf'), 'max':-40, 'color': '#003075' },
            'Very cold': { 'min':-40, 'max':-27, 'color': '#0088cf' },
            'Strong cold': { 'min':-27, 'max':-13, 'color': '#00c2f7' },
            'Moderate cold': { 'min':-13, 'max': 0, 'color': '#91c1e1' },
            'Slight cold': { 'min': 0, 'max': 9, 'color': '#dbebf5' },
            'Comfortable': { 'min': 9, 'max': 26, 'color': '#ffffff' },
            'Moderate heat': { 'min': 26, 'max': 32, 'color': '#fffa00' },
            'Strong heat': { 'min': 32, 'max': 38, 'color': '#ff7900' },
            'Very strong heat': { 'min': 38, 'max': 46, 'color': '#f40000' },
            'Extreme heat': { 'min': 46, 'max': float('inf'), 'color': '#ff0000' }
            }

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        RH = row[self.RH]
        WS_ms = row[self.WS_ms]
        T_mrt = row[self.T_mrt]

        UTCI = None
        if not (isnan(AirTC) or isnan(RH) or isnan(WS_ms) or isnan(T_mrt)):
            # Universal Thermal Climate Index (UTCI)
            UTCI = UTCILib.assess_utci(AirTC, RH, WS_ms, T_mrt)

        return { 'UTCI': UTCI }
