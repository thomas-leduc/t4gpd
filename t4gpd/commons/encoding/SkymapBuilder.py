"""
Created on 17 Oct. 2025

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
from shapely import linearrings, polygons
from shapely.affinity import translate
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.proj.AEProjectionLib import AEProjectionLib


class SkymapBuilder(object):
    """
    classdocs
    """

    @staticmethod
    def build(sensors, angles, proj, size=1, epsilon=1e-1, copy=True):
        def __build(exterior_ring, vp, azim, elev, prj, size):
            pp = [prj(vp, _azim, _elev, size) for _azim, _elev in zip(azim, elev)]
            _exterior_ring = translate(linearrings(exterior_ring), xoff=vp.x, yoff=vp.y)
            return polygons(_exterior_ring, holes=[pp])

        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if angles not in sensors:
            raise Exception(f"{angles} is a not a valid column name!")

        prj = AEProjectionLib.projection_switch(proj)

        n = sensors[angles].apply(lambda t: len(t)).unique()
        if 1 == len(n):
            n = n[0]
        else:
            raise Exception(f"{angles} is a not a valid column (incoherent sizes)!")

        azim = linspace(0, 2.0 * pi, n, endpoint=False)
        cos_azim, sin_azim = cos(azim), sin(azim)
        exterior_ring = (size + epsilon) * stack([cos_azim, sin_azim], axis=1)

        skymaps = sensors.copy(deep=True) if copy else sensors
        skymaps.geometry = skymaps.apply(
            lambda row: __build(
                exterior_ring, row.geometry, azim, row[angles], prj, size
            ),
            axis=1,
        )
        return skymaps

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        dx, rayLength, nRays = 100, 100, 64
        projectionName, size = "Stereographic", 10
        elevationFieldname, h0 = "HAUTEUR", 0.0

        buildings = GeoDataFrameDemos.ensaNantesBuildings()

        sensors = FastGridLib.grid(buildings, dx, intoPoint=True, withRowsCols=False)
        sensors = PointsInPolygonsLib.outdoors(sensors, buildings)

        osensors = SensorBasedEncodingLib.encode25D(
            sensors, buildings, elevationFieldname, h0, rayLength, nRays
        )
        smaps = SkymapBuilder.build(
            osensors, "angles", proj=projectionName, size=size, copy=True
        )

        ref = STSkyMap25D(
            buildings,
            sensors,
            nRays,
            rayLength,
            elevationFieldname,
            h0,
            size,
            epsilon=1e-1,
            projectionName=projectionName,
            withIndices=False,
            withAngles=True,
        ).run()
        ref.index = sensors.index

        # MAPPING
        fig, ax = plt.subplots(figsize=(10, 10))

        buildings.plot(ax=ax, color="lightgrey")
        sensors.plot(ax=ax, color="black", marker="P")
        ref.boundary.plot(ax=ax, color="red", linewidth=1.0)
        smaps.plot(ax=ax, color="yellow", edgecolor="green", alpha=0.5)
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)


# SkymapBuilder.test()
