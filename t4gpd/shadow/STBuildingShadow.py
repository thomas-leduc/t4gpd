"""
Created on 9 Apr. 2025

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
from numpy import isnan
from shapely import MultiPolygon, Polygon
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.ShadowLib import ShadowLib
from t4gpd.commons.sun.SunModel import SunModel
from t4gpd.shadow.AbstractShadow import AbstractShadow


class STBuildingShadow(AbstractShadow):
    """
    classdocs
    """

    def __init__(
        self,
        buildings,
        dts,
        elevationFieldName="HAUTEUR",
        altitudeOfShadowPlane=0,
        aggregate=False,
        model="pvlib",
    ):
        """
        Constructor
        """
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, "GeoDataFrame")
        self.gdf = buildings

        if elevationFieldName not in buildings:
            raise Exception(f"{elevationFieldName} is not a relevant field name!")
        self.elevationFieldName = elevationFieldName

        self.altitudeOfShadowPlane = altitudeOfShadowPlane
        self.aggregate = aggregate

        sunModel = SunModel(buildings, altitude=altitudeOfShadowPlane, model=model)
        self.sunPositions = sunModel.positions_and_sun_beam_direction(dts)

    def _auxiliary(self, row, radDir, solarAlti, solarAzim):
        geom = row.geometry
        geomElevation = row[self.elevationFieldName]

        if (
            (geomElevation is None)
            or (isnan(geomElevation))
            or (geomElevation <= self.altitudeOfShadowPlane)
        ):
            return geom

        if isinstance(geom, Polygon):
            _shadow = ShadowLib.projectBuildingOntoShadowPlane(
                geom, geomElevation, radDir, self.altitudeOfShadowPlane
            )
            if _shadow is not None:
                return _shadow

        elif isinstance(geom, MultiPolygon):
            _shadows = []
            for g in geom.geoms:
                _shadow = ShadowLib.projectBuildingOntoShadowPlane(
                    g, geomElevation, radDir, self.altitudeOfShadowPlane
                )
                if _shadow is not None:
                    _shadows.append(_shadow)
            return None if (0 == len(_shadows)) else MultiPolygon(_shadows)

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        from pandas import Timestamp
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        buildings = buildings.tail(1)
        dts = [
            Timestamp(f"2025-07-21 {h}:00", tz="Europe/Paris").tz_convert("UTC")
            for h in [9, 12, 15]
        ]
        shadows = STBuildingShadow(
            buildings,
            dts,
            elevationFieldName="HAUTEUR",
            altitudeOfShadowPlane=0,
            aggregate=False,
            model="pvlib",
        ).run()

        # PLOTTING
        shadows.datetime = shadows.datetime.apply(lambda dt: dt.strftime("%H:%M"))
        my_cmap = ListedColormap(["red", "green", "blue"])

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        shadows.plot(ax=ax, column="datetime", cmap=my_cmap, alpha=0.25, legend=True)
        buildings.boundary.plot(ax=ax, color="red")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return buildings, shadows, dts


# buildings, shadows, dts = STBuildingShadow.test()
# buildings.to_file("/tmp/DEBUG.gpkg", layer="buildings2")
# shadows.to_file("/tmp/DEBUG.gpkg", layer="shadows2")
