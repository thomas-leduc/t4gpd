'''
Created on 1 avr. 2021

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
from numpy import ceil, floor
from shapely.affinity import translate
from shapely.geometry import MultiPoint, MultiPolygon, Point, Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class GridFace(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, dx, dy=None, intoPoint=True):
        '''
        Constructor
        '''
        self.dx = dx
        self.dy = dx if dy is None else dy
        self.intoPoint = intoPoint

    @staticmethod
    def __findLongestEdge(geom):
        biggestLen, biggestEdge = 0, None
        for currEdge in GeomLib.toListOfBipointsAsLineStrings(geom):
            currLen = currEdge.length
            if (biggestLen < currLen):
                biggestLen, biggestEdge = currLen, currEdge
        return biggestEdge

    @staticmethod
    def __greatestEnclosingInt(value):
        return int(ceil(value) if (0 < value) else floor(value))

    @staticmethod
    def __preprocess(geom, du, dv):
        minx, miny, maxx, maxy = geom.bounds
        ll, lr, ur, ul = [minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]

        longestEdge = GridFace.__findLongestEdge(geom)
        u = GeomLib.unitVector(*longestEdge.coords)
        v = [-u[1], u[0]]

        anchor = geom.exterior.coords[0]
        nuMin, nuMax, nvMin, nvMax = 0, 0, 0, 0

        for _p in (ll, lr, ur, ul):
            tmp = GeomLib.vector_to(anchor, _p)
            nu = GridFace.__greatestEnclosingInt(GeomLib.dotProduct(u, tmp) / du)
            nv = GridFace.__greatestEnclosingInt(GeomLib.dotProduct(v, tmp) / dv)
            if (nuMax < nu):
                nuMax = nu
            elif (nuMin > nu):
                nuMin = nu

            if (nvMax < nv):
                nvMax = nv
            elif (nvMin > nv):
                nvMin = nv

        return Point(anchor), u, v, nuMin, nuMax, nvMin, nvMax

    @staticmethod
    def __gridIntoFaces(geom, du, dv):
        if isinstance(geom, MultiPolygon):
            _mps = []
            for _geom in geom.geoms:
                _mp = GridFace.__gridIntoFaces(_geom, du, dv)
                _mps += _mp.geoms
            return MultiPolygon(_mps)

        else:
            anchor, u, v, nuMin, nuMax, nvMin, nvMax = GridFace.__preprocess(geom, du, dv)

            _geoms = []
            for nv in range(nvMin, nvMax + 1):
                for nu in range(nuMin, nuMax + 1):
                    p1 = translate(anchor,
                                   xoff=(nu - 0.5) * du * u[0] + (nv - 0.5) * dv * v[0],
                                   yoff=(nu - 0.5) * du * u[1] + (nv - 0.5) * dv * v[1])
                    p2 = translate(anchor,
                                   xoff=(nu + 0.5) * du * u[0] + (nv - 0.5) * dv * v[0],
                                   yoff=(nu + 0.5) * du * u[1] + (nv - 0.5) * dv * v[1])
                    p3 = translate(anchor,
                                   xoff=(nu + 0.5) * du * u[0] + (nv + 0.5) * dv * v[0],
                                   yoff=(nu + 0.5) * du * u[1] + (nv + 0.5) * dv * v[1])
                    p4 = translate(anchor,
                                   xoff=(nu - 0.5) * du * u[0] + (nv + 0.5) * dv * v[0],
                                   yoff=(nu - 0.5) * du * u[1] + (nv + 0.5) * dv * v[1])

                    _cell = Polygon([p1, p2, p3, p4])
                    if geom.contains(_cell):
                        _geoms.append(_cell)

            return MultiPolygon(_geoms)

    def runWithArgs(self, row):
        geom = row.geometry
        if not GeomLib.isPolygonal(geom):
            return { 'geometry': MultiPolygon() }

        geom = GeomLib.normalizeRingOrientation(geom)

        geom = GridFace.__gridIntoFaces(geom, self.dx, self.dy)
        if self.intoPoint:
            geom = MultiPoint([_p.centroid for _p in geom.geoms])

        return { 'geometry': geom, 'n_cells': len(geom.geoms) }
