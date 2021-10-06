'''
Created on 16 juin 2020

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
from numpy import round, sqrt
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon

from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class DensifierLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def __densifyByCount(line, npts, gid, pathid):
        distance = line.length / (npts - 1)
        return DensifierLib.__densifyByDistance(line, distance, gid, pathid)

    @staticmethod
    def __densifyByDistance(line, distance, gid, pathid, adjustableDist=True):
        if not isinstance(line, LineString):
            raise IllegalArgumentTypeException(line, 'LineString')
        
        if adjustableDist:
            _d = line.length
            if (_d > distance):
                distance = _d / round(_d / distance)
        
        listOfCoords = line.coords

        result, nodeid, remainingDist = list(), 0, 0.0
        for i in range(1, len(listOfCoords)):
            a, b = listOfCoords[i - 1], listOfCoords[i]
            speedv = [ b[0] - a[0], b[1] - a[1] ]
            norm = sqrt(speedv[0] * speedv[0] + speedv[1] * speedv[1])
            if (0.0 < norm):
                speedv = [ speedv[0] / norm, speedv[1] / norm ]

                k = remainingDist
                while (k <= norm):
                    samplePoint = Point([ a[0] + k * speedv[0], a[1] + k * speedv[1] ])
                    result.append({'gid':gid, 'pathid': pathid, 'nodeid': nodeid,
                                   'motion_dir':ArrayCoding.encode(speedv), 'geometry':samplePoint})
                    k += distance
                    gid += 1
                    nodeid += 1

                remainingDist = k - norm
        return gid, pathid + 1, result

    @staticmethod
    def densifyByCount(geom, npts, gid=0, pathid=0):
        if isinstance(geom, LineString):
            gid, pathid, result = DensifierLib.__densifyByCount(geom, npts, gid, pathid)

        elif isinstance(geom, Polygon):
            gid, pathid, result = DensifierLib.densifyByCount(geom.exterior, npts, gid, pathid)
            for g in geom.interiors:
                gid, pathid, _result = DensifierLib.densifyByCount(g, npts, gid, pathid)
                result += _result

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                gid, pathid, _result = DensifierLib.densifyByCount(g, npts, gid, pathid)
                result += _result

        return gid, pathid, result

    @staticmethod
    def densifyByDistance(geom, distance, gid=0, pathid=0, adjustableDist=True):
        if isinstance(geom, LineString):
            gid, pathid, result = DensifierLib.__densifyByDistance(geom, distance, gid, pathid, adjustableDist)

        elif isinstance(geom, Polygon):
            gid, pathid, result = DensifierLib.densifyByDistance(geom.exterior, distance, gid, pathid, adjustableDist)
            for g in geom.interiors:
                gid, pathid, _result = DensifierLib.densifyByDistance(g, distance, gid, pathid, adjustableDist)
                result += _result

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                gid, pathid, _result = DensifierLib.densifyByDistance(g, distance, gid, pathid, adjustableDist)
                result += _result

        return gid, pathid, result
