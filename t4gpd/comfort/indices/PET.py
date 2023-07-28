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
from pandas import DataFrame, Interval, IntervalIndex
from t4gpd.comfort.algo.PETLib import PETLib
from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PET(AbstractThermalComfortIndice):
    '''
    classdocs
    '''
    RANGES = DataFrame(
        data=[("Extreme cold stress", "#003075"),
              ("Strong cold stress", "#00c2f7"),
              ("Moderate cold stress", "#91c1e1"),
              ("Slight cold stress", "#dbebf5"),
              ("No thermal stress", "#ffffff"),
              ("Slight heat stress", "#ffdabd"),
              ("Moderate heat stress", "#fffa00"),
              ("Strong heat stress", "#ff7900"),
              ("Extreme heat stress", "#ff0000")],
        columns=["label", "color"],
        index=IntervalIndex([
            Interval(left=-float("inf"), right=4, closed="right"),
            Interval(left=4, right=8, closed="right"),
            Interval(left=8, right=13, closed="right"),
            Interval(left=13, right=18, closed="right"),
            Interval(left=18, right=23, closed="right"),
            Interval(left=23, right=29, closed="right"),
            Interval(left=29, right=35, closed="right"),
            Interval(left=35, right=41, closed="right"),
            Interval(left=41, right=float("inf"), closed="right"),
            ])
        )

    def __init__(self, sensorsGdf, AirTC="AirTC_Avg", RH="RH_Avg", WS_ms="WS_ms_Avg",
                 T_mrt="T_mrt"):
        '''
        Constructor

        AirTC: air temperature [C]
        RH: relative humidity [%]
        Ws_ms: wind speed recorded at pedestrian level (at height 1.1 m) [m.s-1]
        T_mrt: Mean radiant temperature [C]
        
        PET: Physiologically Equivalent Temperature
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, "DataFrame")

        for fieldname in (AirTC, RH, WS_ms, T_mrt):
            if fieldname not in sensorsGdf:
                raise Exception("%s is not a relevant field name!" % fieldname)

        self.AirTC = AirTC
        self.RH = RH
        self.WS_ms = WS_ms
        self.T_mrt = T_mrt

    @staticmethod
    def thermalPerceptionRange(tp):
        return PET.RANGES.iloc[PET.RANGES.index.get_loc(tp)].label

    @staticmethod
    def thermalPerceptionRanges():
        # Excerpt from https://doi.org/10.1016/j.wace.2018.01.004
        return {
            row.label: {"min": idx.left, "max": idx.right, "color": row.color} for idx, row in PET.RANGES.iterrows()
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

        return { "PET": PET }
