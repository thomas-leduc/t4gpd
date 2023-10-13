'''
Created on 27 mai 2021

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
from datetime import datetime, timezone

from t4gpd.avidon.scenarios.AbstractScenario import AbstractScenario
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess

class EnergyDemandOfITEquipment(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, scenario, dt, tz=timezone.utc):
        '''
        Constructor
        '''
        if not isinstance(scenario, AbstractScenario):
            raise IllegalArgumentTypeException(scenario, 'AbstractScenario')
        self.scenario = scenario

        if not isinstance(dt, datetime):
            raise IllegalArgumentTypeException(dt, 'datetime')
        self.dt = dt.replace(tzinfo=tz) if dt.tzinfo is None else dt

    def runWithArgs(self, row):
        return {
            'IT_in_Wh': self.scenario.energyDemandOfITEquipment(row, self.dt),
            'datetime': self.dt
            }
