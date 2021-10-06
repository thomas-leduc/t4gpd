'''
Created on 15 dec. 2020

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
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess
from t4gpd.commons.ChrystalAlgorithm import ChrystalAlgorithm


class MBC(AbstractGeoprocess):
    '''
    classdocs
    '''

    @staticmethod
    def runWithArgs(row):
        circle, center, radius = ChrystalAlgorithm(row.geometry).run()
        return { 'geometry': circle, 'radius': radius, 'center': center.wkt }
