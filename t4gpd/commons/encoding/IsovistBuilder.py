"""
Created on 16 Oct. 2025

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

from geopandas import GeoDataFrame
from numpy import cos, linspace, pi, sin, stack
from shapely import polygons
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class IsovistBuilder(object):
    """
    classdocs
    """

    @staticmethod
    def build(sensors, raylen, copy=True):
        def __build(vp, raylens, arr_cos, arr_sin):
            vp = vp.centroid
            x, y = vp.x + raylens * arr_cos, vp.y + raylens * arr_sin
            return polygons(stack([x, y], axis=1))

        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if raylen not in sensors:
            raise Exception(f"{raylen} is a not a valid column name!")

        n = sensors[raylen].apply(lambda t: len(t)).unique()
        if 1 == len(n):
            n = n[0]
        else:
            raise Exception(f"{raylen} is a not a valid column (incoherent sizes)!")

        angles = linspace(0, 2.0 * pi, n, endpoint=False)
        arr_cos, arr_sin = cos(angles), sin(angles)

        isovists = sensors.copy(deep=True) if copy else sensors
        isovists.geometry = isovists.apply(
            lambda row: __build(row.geometry, row[raylen], arr_cos, arr_sin), axis=1
        )
        return isovists

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.isovist.STIsovistField2D import STIsovistField2D

        dx, rayLength, nRays = 100, 45, 64

        buildings = GeoDataFrameDemos.ensaNantesBuildings()

        sensors = FastGridLib.grid(buildings, dx, intoPoint=True, withRowsCols=False)
        sensors = PointsInPolygonsLib.outdoors(sensors, buildings)

        osensors = SensorBasedEncodingLib.encode2D(sensors, buildings, rayLength, nRays)
        isov = IsovistBuilder.build(osensors, raylen="raylen2D", copy=True)

        _, ref = STIsovistField2D(buildings, sensors, nRays, rayLength).run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(10, 10))

        buildings.plot(ax=ax, color="lightgrey")
        sensors.plot(ax=ax, color="black", marker="P")
        ref.boundary.plot(ax=ax, color="red", linewidth=1.0)
        isov.plot(ax=ax, color="yellow", alpha=0.5)
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)


# IsovistBuilder.test()
