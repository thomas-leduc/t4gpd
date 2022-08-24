'''
Created on 18 juil. 2022

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
from shapely.geometry import LineString
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class FromContourToNormalVector(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, magn=1.0):
        self.magn = magn

    def runWithArgs(self, row):
        geom = row.geometry
        assert GeomLib.isPolygonal(geom), 'The GeoDataFrame must be composed of (Multi)Polygon'
        c = GeomLib3D.centroid(geom).coords[0]
        n = GeomLib3D.getFaceNormalVector(geom)
        return { 'geometry': LineString([c, [c[i] + self.magn * n[i] for i in range(3)]]) }
