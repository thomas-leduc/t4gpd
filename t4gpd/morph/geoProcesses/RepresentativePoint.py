'''
Created on 24 juin 2022

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
from shapely.geometry import JOIN_STYLE
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class RepresentativePoint(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, buffdist=4, join_style=JOIN_STYLE.mitre):
        '''
        Constructor
        '''
        self.buffdist = buffdist
        self.join_style = join_style

    def representativePoint(self, geom, buffdist):
        _geom = geom.buffer(-buffdist, join_style=self.join_style)
        if _geom.is_empty:
            return None
        return _geom.representative_point()

    def runWithArgs(self, row):
        geom = row.geometry
        buffdist = self.buffdist
        for _ in range(10):
            p = self.representativePoint(geom, buffdist)
            if p is not None:
                return { 'geometry': p }
            buffdist /= 2
        return { 'geometry': geom.representative_point() }
