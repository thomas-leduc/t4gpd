'''
Created on 25 juin 2021

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
from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.graph.UrbanGraphLibOld import UrbanGraphLibOld
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class CrossroadsAngularity(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, roads, sampleDist=None, threshold=10):
        '''
        Constructor
        '''
        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, 'GeoDataFrame')
        self.roads = roads

        self.graph = UrbanGraphLibOld()
        self.graph.add([_geom for _geom in roads.geometry])
        self.rs = self.graph.getUniqueRoadsSections()
        self.assocTbl = dict()
        for rs in self.graph.getUniqueRoadsSections():
            _start = UrbanGraphLibOld.hashCoord(rs['geometry'].coords[0])
            if (_start in self.assocTbl):
                self.assocTbl[_start].append(rs['geometry'].coords)
            else:
                self.assocTbl[_start] = [rs['geometry'].coords]

            _stop = UrbanGraphLibOld.hashCoord(rs['geometry'].coords[-1])
            if (_stop in self.assocTbl):
                self.assocTbl[_stop].append(list(reversed(rs['geometry'].coords)))
            else:
                self.assocTbl[_stop] = [list(reversed(rs['geometry'].coords))]

        self.sampleDist = sampleDist
        self.threshold = threshold

    def __isAMultipleOf(self, a, b):
        if (self.threshold >= (a % b)) or (self.threshold >= (b - (a % b))):
            return True
        return False

    def __aux1(self, currCoords):
        _currHash = UrbanGraphLibOld.hashCoord(currCoords)

        _azims = []
        for _branch in self.assocTbl[_currHash]:
            _remoteCoords = _branch[-1]
            _currDir = [_remoteCoords[0] - currCoords[0], _remoteCoords[1] - currCoords[1]]
            _currAzim = round(AngleLib.toDegrees(AngleLib.normAzimuth(_currDir)), 1)
            _azims.append(_currAzim)

        _azims = sorted(_azims)
        _angles = [round((_azims[i] - _azims[i - 1] + 360) % 360, 1) for i in range(len(_azims))]
        _mode = 4
        for _angle in _angles:
            if (not self.__isAMultipleOf(_angle, 90)):
                if (not self.__isAMultipleOf(_angle, 45)):
                    _mode = 16
                elif (4 == _mode):
                    _mode = 8

        return {
            'cross_azim': ArrayCoding.encode(_azims),
            'cross_std1': None,
            'cross_angl': ArrayCoding.encode(_angles),
            'cross_std2': None,
            'cross_mode': _mode
            }

    def runWithArgs(self, row):
        geom = row.geometry

        if ('Point' == geom.geom_type):
            _currCoords = geom.coords[0]

            if ((self.sampleDist is None) or (0 >= self.sampleDist)):
                return self.__aux1(_currCoords)
            else:
                raise NotImplementedError('Must be implemented!')

        return {
            'cross_azim': None,
            'cross_std1': None,
            'cross_angl': None,
            'cross_std2': None,
            'cross_mode': None
            }
