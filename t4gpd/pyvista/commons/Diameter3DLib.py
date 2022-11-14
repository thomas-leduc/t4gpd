'''
Created on 5 sept. 2022

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
from shapely.geometry import LineString, Polygon
from t4gpd.commons.DiameterLib import DiameterLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D


class Diameter3DLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def diameter3D(geom):
        assert isinstance(geom, Polygon), 'geom is expected to be a Shapely Polygon!'

        if not GeomLib.is3D(geom):
            diam, dist, _ = DiameterLib.diameter(geom)
            return [diam, dist]

        vertices = list(geom.exterior.coords)
        nVertices = len(vertices)

        maxDist, pairOfVertices = -1.0, None
        for i in range(nVertices):
            v1 = vertices[i]
            for j in range(i + 1, nVertices):
                v2 = vertices[j]
                currDist = GeomLib3D.distFromTo(v1, v2)
                if maxDist < currDist:
                    maxDist = currDist
                    pairOfVertices = [v1, v2]

        if pairOfVertices is None:
            return [None, None]

        segment = LineString(pairOfVertices)
        return [segment, maxDist]
