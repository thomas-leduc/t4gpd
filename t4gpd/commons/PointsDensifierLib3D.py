'''
Created on 20 sep. 2022

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
from numpy import sqrt, asarray
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PointsDensifierLib3D(object):
    '''
    classdocs
    '''

    @staticmethod
    def __densifyByCurvilinearAbscissa(line, curvAbsc, blockid, contourid):
        if not isinstance(line, LineString):
            raise IllegalArgumentTypeException(line, 'LineString')

        listOfCoords = line.coords
        result, nodeid = list(), 0
        for i in range(1, len(listOfCoords)):
            a, b = listOfCoords[i - 1], listOfCoords[i]
            speedv = asarray([ b[0] - a[0], b[1] - a[1], b[2] - a[2] ])
            norm = sqrt(speedv[0] ** 2 + speedv[1] ** 2 + speedv[2] ** 2)
            if (0.0 < norm):
                speedv = speedv / norm

                for _curvAbsc in curvAbsc:
                    samplePoint = Point(a + _curvAbsc * norm * speedv)

                    result.append({'node_id': ArrayCoding.encode([blockid, contourid, nodeid]),
                                   'motion_dir': ArrayCoding.encode(speedv),
                                   'geometry': samplePoint})
                    nodeid += 1

        return result

    @staticmethod
    def densifyByCurvilinearAbscissa(geom, curvAbsc, blockid, contourid=0):
        assert GeomLib.is3D(geom), 'geom is expected to be 3D!'

        if isinstance(geom, LineString):
            result = PointsDensifierLib3D.__densifyByCurvilinearAbscissa(
                geom, curvAbsc, blockid, contourid)

        elif isinstance(geom, Polygon):
            result = PointsDensifierLib3D.__densifyByCurvilinearAbscissa(
                geom.exterior, curvAbsc, blockid, contourid)
            for g in geom.interiors:
                contourid += 1
                result += PointsDensifierLib3D.__densifyByCurvilinearAbscissa(
                    g, curvAbsc, blockid, contourid)

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                result += PointsDensifierLib3D.densifyByCurvilinearAbscissa(
                    g, curvAbsc, blockid, contourid)
                contourid += 1

        else:
            result = []

        return result
