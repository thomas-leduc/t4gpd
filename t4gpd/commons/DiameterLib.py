"""
Created on 19 juin 2020

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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
"""

from shapely.geometry import LineString, Point

from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class DiameterLib(object):
    """
    classdocs
    """

    @staticmethod
    def diameter(obj):
        if not GeomLib.isAShapelyGeometry(obj):
            raise IllegalArgumentTypeException(obj, "Shapely geometry")
        chull = obj.convex_hull
        chull = chull if GeomLib.isLineal(chull) else chull.exterior
        vertices = [Point(c) for c in chull.coords]
        nVertices = len(vertices)

        maxDist, pairOfVertices = -1.0, None
        for i in range(nVertices):
            v1 = vertices[i]
            for j in range(i + 1, nVertices):
                v2 = vertices[j]
                currDist = v1.distance(v2)
                if maxDist < currDist:
                    maxDist = currDist
                    pairOfVertices = [v1, v2]

        if pairOfVertices is None:
            return [None, None, None]

        segment = LineString(pairOfVertices)
        return [segment, maxDist, GeomLib.getLineStringOrientation(segment)]
