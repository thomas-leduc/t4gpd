'''
Created on 31 janv. 2021

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
from shapely.affinity import translate
from shapely.geometry import MultiPolygon, Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class FootprintExtruder(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, buildingsGdf, elevationFieldname='HAUTEUR', forceZCoordToZero=True):
        '''
        Constructor
        '''
        if not isinstance(buildingsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(buildingsGdf, 'GeoDataFrame')

        if not (elevationFieldname in buildingsGdf):
            raise Exception('%s is not a relevant field name!' % (elevationFieldname))
        self.elevationFieldname = elevationFieldname
        self.forceZCoordToZero = forceZCoordToZero

    def __wallsPerRing(self, groundRing, roofRing):
        _down, _up = groundRing.coords, roofRing.coords
        _nNodes, result = len(_down), []
        for i in range(1, _nNodes):
            result.append(Polygon([_down[i - 1], _down[i], _up[i], _up[i - 1], _down[i - 1]]))
        return result

    def __walls(self, ground, roof):
        result = self.__wallsPerRing(ground.exterior, roof.exterior) 

        _nHoles = len(ground.interiors)
        for i in range(_nHoles):
            result += self.__wallsPerRing(ground.interiors[i], roof.interiors[i])

        return result

    def runWithArgs(self, row):
        _geom, _deltaZ = row.geometry, row[self.elevationFieldname]
        if not (isinstance(_geom, Polygon) or (isinstance(_geom, MultiPolygon) and (1 == len(_geom.geoms)))):
            raise IllegalArgumentTypeException(_geom, 'Polygon or MultiPolygon (with a single Polygon)')

        if isinstance(_geom, MultiPolygon):
            _geom = _geom.geoms[0]

        _geom = GeomLib.normalizeRingOrientation(_geom)

        if (self.forceZCoordToZero) or (not _geom.has_z):
            _ground = GeomLib.forceZCoordinateToZ0(_geom)
            _roof = translate(_ground, zoff=_deltaZ)
        else:
            _roof = _geom
            _ground = translate(_roof, zoff=-_deltaZ)

        _ground, _roof = (_ground, _roof) if (0 < _deltaZ) else (_roof, _ground)

        _walls = self.__walls(_ground, _roof)

        # TL. 10.03.2021
        _ground = GeomLib.normalizeRingOrientation(_ground, ccw=False)
        _roof = GeomLib.normalizeRingOrientation(_roof, ccw=True)

        return { 'geometry': MultiPolygon([_ground, _roof] + _walls) }
