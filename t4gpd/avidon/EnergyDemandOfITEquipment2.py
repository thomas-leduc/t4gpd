'''
Created on 16 feb. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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

from numpy import float64, ndarray
from t4gpd.avidon.commons.EnergyDemandCalculator import EnergyDemandCalculator
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class EnergyDemandOfITEquipment2(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, columns, dt, tz=timezone.utc, D=None, S=None, E=None, encode=False):
        '''
        Constructor
        '''
        self.calc = EnergyDemandCalculator(D, S, E)
        self.columns = columns

        if isinstance(dt, datetime):
            self.dt = [dt.replace(tzinfo=tz)] if dt.tzinfo is None else [dt]
        elif isinstance(dt, (list, ndarray, tuple)):
            self.dt = []
            for _dt in dt:
                if not isinstance(_dt, datetime):
                    raise IllegalArgumentTypeException(dt, 'datetime or list of datetimes')
                self.dt.append(_dt.replace(tzinfo=tz) if _dt.tzinfo is None else _dt)
        else:
            raise IllegalArgumentTypeException(dt, 'datetime or list of datetimes')

        self.encode = encode

    def runWithArgs(self, row):
        _C = row[self.columns].to_numpy(dtype=float64)

        whs, dts = [], []
        for _dt in self.dt:
            _wh = self.calc.energyDemandOfITEquipment(_C, _dt)
            dts.append(_dt)
            whs.append(_wh)

        if (1 == len(self.dt)):
            return { 'IT_in_Wh': whs[0], 'datetime': dts[0] }

        if self.encode:
            return { 'IT_in_Wh': ArrayCoding.encode(whs), 'datetime': ArrayCoding.encode(dts) }

        return { 'IT_in_Wh': whs, 'datetime': dts }
