'''
Created on 9 janv. 2023

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
from geopandas.geodataframe import GeoDataFrame
from numpy import arcsin, asarray, cos, pi, round, sin, sqrt, vstack, where
from numpy.random import default_rng, uniform
from shapely.geometry import Point, Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D


class RandomPointPicking(object):
    '''
    classdocs
    '''

    @staticmethod
    def _simpleTriangulation(ngon):
        coords = ngon.exterior.coords[:-1]
        n = len(coords)
        resultat = []
        for i, ipp in zip(range(1, n - 1), range(2, n)):
            resultat.append(Polygon([coords[0], coords[i], coords[ipp]]))
        return resultat
    
    @staticmethod
    def convexPolygonPointPicking(ngon, npts):
        rng = default_rng()
        # INSPIRED BY:
        # https://blogs.sas.com/content/iml/2020/10/21/random-points-in-polygon.html
        assert isinstance(ngon, Polygon), 'ngon is expected to be a Shapely Polygon!'
        assert GeomLib.isConvex(ngon), 'ngon is expected to be convex!'
        tris = RandomPointPicking._simpleTriangulation(ngon)
        # areas = [tri.area for tri in tris]
        areas = asarray([GeomLib3D.getArea(tri) for tri in tris])
        ratios = areas / areas.sum() 
        listOfNpts = round(npts * ratios).astype(int)

        choices = [0] * len(tris) + [1] * npts
        listOfNpts[listOfNpts == 0] = rng.choice(choices, size=len(listOfNpts[listOfNpts == 0]))

        resultat = []
        for tri, _npts in zip(tris, listOfNpts):
            resultat.append(RandomPointPicking.trianglePointPicking(tri, _npts))
        return vstack(resultat)

    @staticmethod
    def trianglePointPicking(tri, npts):
        # INSPIRED BY:
        # https://blogs.sas.com/content/iml/2020/10/19/random-points-in-triangle.html
        assert isinstance(tri, Polygon), 'tri is expected to be a Shapely Polygon!'
        assert tri.is_valid, 'tri is expected to be a VALID Shapely Polygon!'
        assert (4 == len(tri.exterior.coords)), 'tri is expected to be a triangle!'
        a, b, c = list(tri.exterior.coords[:-1])
        a = [a[0], a[1], 0 if (2 == len(a)) else a[2]]
        b = [b[0], b[1], 0 if (2 == len(b)) else b[2]]
        c = [c[0], c[1], 0 if (2 == len(c)) else c[2]]
        ab = asarray([b[0] - a[0], b[1] - a[1], b[2] - a[2]])
        ac = asarray([c[0] - a[0], c[1] - a[1], c[2] - a[2]])

        # GENERATE RANDOM UNIFORM VARIABLES
        u1, u2 = uniform(low=0, high=1, size=[2, npts])
        idx = where(u1 + u2 > 1)
        u1[idx], u2[idx] = 1 - u1[idx], 1 - u2[idx]

        # GENERATE XYZ
        x = a[0] + u1 * ab[0] + u2 * ac[0]
        y = a[1] + u1 * ab[1] + u2 * ac[1]
        z = a[2] + u1 * ab[2] + u2 * ac[2]
        return vstack([x, y, z]).T 

    @staticmethod
    def unitDiskPointPicking(npts):
        # INSPIRED BY:
        # https://mathworld.wolfram.com/DiskPointPicking.html
        r, theta = uniform(low=0, high=1, size=[2, npts])
        r, theta = sqrt(r), 2 * pi * theta
        x, y = r * cos(theta), r * sin(theta)
        return vstack([x, y]).T 

    @staticmethod
    def unitSpherePointPicking(npts):
        # INSPIRED BY:
        # https://mathworld.wolfram.com/SpherePointPicking.html
        u, v = uniform(low=0, high=1, size=[2, npts])
        # LONGITUDE, LATITUDE
        lon, lat = 2 * pi * u, arcsin(2 * v - 1)
        # FROM LONGITUDE AND LATITUDE TO CARTESIAN COORDINATES
        cosLat = cos(lat)
        x, y, z = cos(lon) * cosLat, sin(lon) * cosLat, sin(lat)
        return vstack([x, y, z]).T 

    @staticmethod
    def toGeoDataFrame(XYZ):
        rows = []
        for gid, xyz in enumerate(XYZ, start=1):
            rows.append({ 'gid': gid, 'geometry': Point(xyz) })
        return GeoDataFrame(rows)
