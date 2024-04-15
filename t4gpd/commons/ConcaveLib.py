'''
Created on 30 oct 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from shapely import MultiPolygon, Polygon, union_all
from shapely.prepared import prep
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class ConcaveLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def fillInTheConcavities(polygon, obstacles):
        if not GeomLib.isPolygonal(polygon):
            raise IllegalArgumentTypeException(
                polygon, "Polygon or MultiPolygon")

        chull = polygon.convex_hull
        concavities = chull.difference(polygon)
        if isinstance(concavities, Polygon):
            concavities = MultiPolygon([concavities])

        pobstacles = prep(obstacles)
        result = [polygon] + \
            list(filter(pobstacles.disjoint, concavities.geoms))

        return union_all(result)
