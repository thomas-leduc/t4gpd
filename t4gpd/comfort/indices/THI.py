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
from pandas.core.frame import DataFrame
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice


class THI(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg'):
        '''
        Constructor

        AirTC: air temperature [C]
        RH: relative humidity [%]

        THI: Temperature-Humidity Index (THI) stated in Grosdemouge (2020) 
        after (Emmanuel et al., 2016) in humid and hot environment
        *** 21-24: 100% des personnes en situation de confort
        *** 24-26: 50% des personnes en situation de confort
        *** > 26: 100% des personnes en situation d'inconfort lie a la chaleur
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (AirTC, RH):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.AirTC = AirTC
        self.RH = RH

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        RH = row[self.RH]

        # THI: Temperature-Humidity Index
        THI = 0.8 * AirTC + (AirTC * RH) / 500

        return { 'THI': THI }
