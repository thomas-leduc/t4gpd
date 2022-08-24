'''
Created on 20 avr. 2021

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
from numpy import sqrt
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PointsDensifierLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def __densifyByCount(line, npts, blockid, contourid, distToTheSubstrate=None):
        distance = line.length / (npts - 1)
        return PointsDensifierLib.__densifyByDistance(line, distance, blockid,
                                                      contourid, distToTheSubstrate)

    @staticmethod
    def __densifyByDistance(line, distance, blockid, contourid, adjustableDist=True,
                            distToTheSubstrate=None):
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
                normalv = [speedv[1], -speedv[0], 0]

                k = remainingDist
                while (k <= norm):
                    samplePoint = Point([ a[0] + k * speedv[0], a[1] + k * speedv[1] ])

                    if not distToTheSubstrate is None:
                        samplePoint = Point([
                            samplePoint.x + distToTheSubstrate * normalv[0],
                            samplePoint.y + distToTheSubstrate * normalv[1]
                            ])

                    result.append({'node_id': ArrayCoding.encode([blockid, contourid, nodeid]),
                                   'motion_dir': ArrayCoding.encode(speedv),
                                   'normal_vec': ArrayCoding.encode(normalv),
                                   'geometry': samplePoint})
                    k += distance
                    nodeid += 1

                remainingDist = k - norm
        return result

    @staticmethod
    def __densifyByCurvilinearAbscissa(line, curvAbsc, blockid, contourid, distToTheSubstrate=None):
        if not isinstance(line, LineString):
            raise IllegalArgumentTypeException(line, 'LineString')

        listOfCoords = line.coords
        result, nodeid = list(), 0
        for i in range(1, len(listOfCoords)):
            a, b = listOfCoords[i - 1], listOfCoords[i]
            speedv = [ b[0] - a[0], b[1] - a[1] ]
            norm = sqrt(speedv[0] * speedv[0] + speedv[1] * speedv[1])
            if (0.0 < norm):
                speedv = [ speedv[0] / norm, speedv[1] / norm ]
                normalv = [speedv[1], -speedv[0], 0]

                ls = LineString([a, b])
                for _curvAbsc in curvAbsc:
                    samplePoint = ls.interpolate(_curvAbsc, normalized=True)

                    if not distToTheSubstrate is None:
                        samplePoint = Point([
                            samplePoint.x + distToTheSubstrate * normalv[0],
                            samplePoint.y + distToTheSubstrate * normalv[1]
                            ])

                    result.append({'node_id': ArrayCoding.encode([blockid, contourid, nodeid]),
                                   'motion_dir': ArrayCoding.encode(speedv),
                                   'normal_vec': ArrayCoding.encode(normalv),
                                   'geometry': samplePoint})
                    nodeid += 1

        return result

    @staticmethod
    def densifyByCount(geom, npts, blockid, contourid=0, distToTheSubstrate=None):
        if isinstance(geom, LineString):
            result = PointsDensifierLib.__densifyByCount(geom, npts, blockid, contourid,
                                                         distToTheSubstrate)

        elif isinstance(geom, Polygon):
            result = PointsDensifierLib.__densifyByCount(geom.exterior, npts, blockid, contourid,
                                                         distToTheSubstrate)
            for g in geom.interiors:
                contourid += 1
                result += PointsDensifierLib.__densifyByCount(g, npts, blockid, contourid,
                                                              distToTheSubstrate)

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                result += PointsDensifierLib.__densifyByCount(g, npts, blockid, contourid,
                                                              distToTheSubstrate)
                contourid += 1

        else:
            result = []

        return result

    @staticmethod
    def densifyByDistance(geom, distance, blockid, contourid=0, adjustableDist=True,
                          distToTheSubstrate=None):
        if isinstance(geom, LineString):
            result = PointsDensifierLib.__densifyByDistance(
                geom, distance, blockid, contourid, adjustableDist, distToTheSubstrate)

        elif isinstance(geom, Polygon):
            result = PointsDensifierLib.__densifyByDistance(
                geom.exterior, distance, blockid, contourid, adjustableDist, distToTheSubstrate)
            for g in geom.interiors:
                contourid += 1
                result += PointsDensifierLib.__densifyByDistance(
                    g, distance, blockid, contourid, adjustableDist, distToTheSubstrate)

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                result += PointsDensifierLib.densifyByDistance(
                    g, distance, blockid, contourid, adjustableDist, distToTheSubstrate)
                contourid += 1

        else:
            result = []

        return result

    @staticmethod
    def densifyByCurvilinearAbscissa(geom, curvAbsc, blockid, contourid=0, distToTheSubstrate=None):
        if isinstance(geom, LineString):
            result = PointsDensifierLib.__densifyByCurvilinearAbscissa(
                geom, curvAbsc, blockid, contourid, distToTheSubstrate)

        elif isinstance(geom, Polygon):
            result = PointsDensifierLib.__densifyByCurvilinearAbscissa(
                geom.exterior, curvAbsc, blockid, contourid, distToTheSubstrate)
            for g in geom.interiors:
                contourid += 1
                result += PointsDensifierLib.__densifyByCurvilinearAbscissa(
                    g, curvAbsc, blockid, contourid, distToTheSubstrate)

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                result += PointsDensifierLib.densifyByCurvilinearAbscissa(
                    g, curvAbsc, blockid, contourid, distToTheSubstrate)
                contourid += 1

        else:
            result = []

        return result
