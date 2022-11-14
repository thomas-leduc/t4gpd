'''
Created on 19 sept. 2022

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
from numpy import apply_along_axis, asarray, linspace
from shapely.coords import CoordinateSequence
from shapely.geometry import LinearRing, LineString, Point, Polygon
from sklearn.preprocessing import normalize
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.PointsDensifierLib3D import PointsDensifierLib3D


class SphericalProjectionLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def __projectionOnTheUnitSphere(vpCoord, coords):
        assert isinstance(vpCoord, CoordinateSequence), 'vpCoord is expected to be a CoordinateSequence!'
        assert 1 == len(vpCoord), 'vpCoord is expected to be a CoordinateSequence of a single Point!'
        assert 3 == len(vpCoord[0]), 'vpCoord is expected to be a 3D CoordinateSequence!'
        assert isinstance(coords, CoordinateSequence), 'coords is expected to be a CoordinateSequence!'

        vp = asarray(vpCoord)
        c = asarray(coords)
        nrows, ncols = c.shape
        assert 3 == ncols, 'coords is expected to be a 3D CoordinateSequence!'

        vp = vp.repeat(nrows, axis=0)
        prj = c - vp

        __filter = lambda row: (row[0], row[1], max(vpCoord[0][2], row[2]))
        return apply_along_axis(__filter, 1, vp + normalize(prj, axis=1, norm='l2'))

    @staticmethod
    def __stereographicProjectionOnTheUnitDisc(vpCoord, coords):
        prjCoords = SphericalProjectionLib.__projectionOnTheUnitSphere(vpCoord, coords)

        vp = asarray(vpCoord)
        c = asarray(prjCoords)
        nrows, _ = c.shape

        vp = vp.repeat(nrows, axis=0)
        prj = c - vp
        __stereo = lambda row: (row[0] / (1 + row[2]), row[1] / (1 + row[2]), 0)
        return vp + apply_along_axis(__stereo, 1, prj)

    @staticmethod
    def __orthogonalProjectionOnTheUnitDisc(vpCoord, coords):
        prjCoords = SphericalProjectionLib.__projectionOnTheUnitSphere(vpCoord, coords)

        vp = asarray(vpCoord)
        c = asarray(prjCoords)
        nrows, _ = c.shape

        vp = vp.repeat(nrows, axis=0)
        prj = c - vp
        __ortho = lambda row: (row[0], row[1], 0)
        return vp + apply_along_axis(__ortho, 1, prj)

    @staticmethod
    def __project(vp, geom, prjOp, npts):
        assert isinstance(vp, Point), 'vp is expected to be a Shapely Point!'
        assert GeomLib.isAShapelyGeometry(geom), 'geom is expected to be a Shapely geometry!'
        assert not GeomLib.isMultipart(geom), 'geom must be a single Shapely Point, LineString or Polygon!'

        vpCoord = vp.coords
        if isinstance(geom, Point):
            return Point(prjOp(vpCoord, geom.coords))

        _densifier = PointsDensifierLib3D.densifyByCurvilinearAbscissa
        _curvAbsc = linspace(0, 1, npts)

        if isinstance(geom, LinearRing):
            _tmp = _densifier(geom, curvAbsc=_curvAbsc, blockid=0)
            geom = LinearRing([x['geometry'] for x in _tmp])
            return LinearRing(prjOp(vpCoord, geom.coords))

        if isinstance(geom, LineString):
            _tmp = _densifier(geom, curvAbsc=_curvAbsc, blockid=0)
            geom = LineString([x['geometry'] for x in _tmp])
            return LineString(prjOp(vpCoord, geom.coords))

        if isinstance(geom, Polygon):
            _tmp1 = _densifier(geom.exterior, curvAbsc=_curvAbsc, blockid=0)
            _tmp1 = LinearRing([x['geometry'] for x in _tmp1])

            _tmp2 = [_densifier(hole, curvAbsc=_curvAbsc, blockid=0) for hole in geom.interiors]
            _tmp2 = [LinearRing([x['geometry'] for x in _tmp1]) for _tmp1 in _tmp2]
            geom = Polygon(_tmp1, _tmp2)

            prjExterior = prjOp(vpCoord, geom.exterior.coords)
            prjHoles = [prjOp(vpCoord, hole.coords) for hole in geom.interiors]
            return Polygon(prjExterior, prjHoles)

        raise Exception('Unreachable instruction!')

    @staticmethod
    def orthogonal(vp, geom, npts=51):
        prjOp = SphericalProjectionLib.__orthogonalProjectionOnTheUnitDisc
        return SphericalProjectionLib.__project(vp, geom, prjOp, npts)

    @staticmethod
    def stereographic(vp, geom, npts=51):
        prjOp = SphericalProjectionLib.__stereographicProjectionOnTheUnitDisc
        return SphericalProjectionLib.__project(vp, geom, prjOp, npts)
