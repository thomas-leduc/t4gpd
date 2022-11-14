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
from pandas import DataFrame
from t4gpd.comfort.algo.PETLib import PETLib
from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PET(AbstractThermalComfortIndice):
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
        
        PET: Physiologically Equivalent Temperature
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
            'Extreme cold': { 'min':-float('inf'), 'max':4, 'color': '#003075' },
            'Strong cold': { 'min':4, 'max':8, 'color': '#00c2f7' },
            'Moderate cold': { 'min':8, 'max': 13, 'color': '#91c1e1' },
            'Slight cold': { 'min': 13, 'max': 18, 'color': '#dbebf5' },
            'Comfortable': { 'min': 18, 'max': 23, 'color': '#ffffff' },
            'Slight heat': { 'min': 23, 'max': 29, 'color': '#ffdabd' },
            'Moderate heat': { 'min': 29, 'max': 35, 'color': '#fffa00' },
            'Strong heat': { 'min': 35, 'max': 41, 'color': '#ff7900' },
            'Extreme heat': { 'min': 41, 'max': float('inf'), 'color': '#ff0000' }
            }

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        RH = row[self.RH]
        WS_ms = row[self.WS_ms]
        T_mrt = row[self.T_mrt]

        PET = None
        if not (isnan(AirTC) or isnan(RH) or isnan(WS_ms) or isnan(T_mrt)):
            # PET: Physiologically Equivalent Temperature
            _, _, _, PET = PETLib.assess_pet(AirTC, RH, WS_ms, T_mrt) 

        return { 'PET': PET }
