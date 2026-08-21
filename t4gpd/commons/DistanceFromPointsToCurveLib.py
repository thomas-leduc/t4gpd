"""
Created on 9 Feb. 2026

@author: tleduc

Copyright 2020-2026 Thomas Leduc

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

from numpy import asarray, sqrt
from shapely import MultiPoint, get_coordinates, get_num_geometries, points
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class DistanceFromPointsToCurveLib(object):
    """
    classdocs
    """

    @staticmethod
    def __distances(pts, curve):
        if not GeomLib.isAShapelyGeometry(pts):
            raise IllegalArgumentTypeException(pts, "shapely geometry")
        if not GeomLib.isLineal(curve):
            raise IllegalArgumentTypeException(curve, "LineString or MultiLineString")
        if 1 != get_num_geometries(curve):
            raise IllegalArgumentTypeException(
                curve, "LineString single MultiLineString"
            )
        return asarray(
            [
                pt.distance(curve.interpolate(curve.project(pt)))
                for pt in points(get_coordinates(pts))
            ]
        )

    @staticmethod
    def mae(pts, curve):
        distances = DistanceFromPointsToCurveLib.__distances(pts, curve)
        return distances.mean()

    @staticmethod
    def mse(pts, curve):
        distances = DistanceFromPointsToCurveLib.__distances(pts, curve)
        return (distances**2).mean()

    @staticmethod
    def rmse(pts, curve):
        distances = DistanceFromPointsToCurveLib.__distances(pts, curve)
        return sqrt((distances**2).mean())

    @staticmethod
    def test():
        from shapely import LineString

        curve = LineString([(0, 0), (100, 0)])
        points = MultiPoint([(5, 5), (10, -10), (15, 15)])
        mae = DistanceFromPointsToCurveLib.mae(points, curve)
        mse = DistanceFromPointsToCurveLib.mse(points, curve)
        rmse = DistanceFromPointsToCurveLib.rmse(points, curve)
        assert 10.0 == mae
        assert 350 / 3 == mse
        assert sqrt(350 / 3) == rmse
        print(mae, mse, rmse)


# DistanceFromPointsToCurveLib.test()
