'''
Created on 23 nov. 2020

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
from geopandas.geodataframe import GeoDataFrame
from numpy import arctan, cos, pi, sin
from shapely.geometry import Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCastingLib import RayCastingLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class SkyMap2D(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, buildingsGdf, nRays=180, size=4.0, maxRayLen=100.0, elevationFieldname='HAUTEUR',
                 projectionName='Stereographic'):
        '''
        Constructor
        '''
        if not isinstance(buildingsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(buildingsGdf, 'GeoDataFrame')
        self.buildingsGdf = buildingsGdf
        self.spatialIndex = buildingsGdf.sindex

        self.nRays = nRays
        self.shootingDirs = RayCastingLib.preparePanopticRays(nRays)
        self.size = size
        self.maxRayLen = maxRayLen

        if elevationFieldname not in buildingsGdf:
            raise Exception('%s is not a relevant field name!' % elevationFieldname)
        self.elevationFieldname = elevationFieldname

        if not projectionName in ['Stereographic']:
            raise IllegalArgumentTypeException(projectionName, 'spherical projection as "Stereographic"')
        self.proj = SkyMap2D.__stereographic

    @staticmethod
    def __stereographic(lat, lon, size=1.0):
        radius = (size * cos(lat)) / (1.0 + sin(lat))
        return (radius * cos(lon), radius * sin(lon))

    def runWithArgs(self, row):
        viewPoint = row.geometry.centroid

        if GeomLib.isAnIndoorPoint(viewPoint, self.buildingsGdf, self.spatialIndex):
            return Polygon()

        _, _, _, _, hws = RayCastingLib.multipleRayCast25D(self.buildingsGdf, self.spatialIndex, viewPoint,
                                                           self.shootingDirs, self.maxRayLen, self.elevationFieldname, True)
        lats = [arctan(hw) for hw in hws]
        angularOffset = (2.0 * pi) / self.nRays
        lons = [i * angularOffset for i in list(range(self.nRays)) + [0]]

        pnodes = [self.proj(lats[i], lons[i], self.size) for i in list(range(self.nRays)) + [0]]
        nodes = [(viewPoint.x + pnode[0], viewPoint.y + pnode[1]) for pnode in pnodes]

        return { 'geometry': Polygon(viewPoint.buffer(self.size).exterior.coords, [nodes]) }
