"""
Created on 26 aug. 2020

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

import warnings
from datetime import timezone
from geopandas import GeoDataFrame
from numpy import isnan
from shapely import MultiPolygon, Polygon
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.commons.sun.ShadowLib import ShadowLib
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.sun.AbstractHardShadow import AbstractHardShadow


class STHardShadow(AbstractHardShadow):
    """
    classdocs
    """

    def __init__(
        self,
        occludersGdf,
        datetimes,
        occludersElevationFieldname="HAUTEUR",
        altitudeOfShadowPlane=0,
        aggregate=False,
        tz=timezone.utc,
        model="pysolar",
    ):
        """
        Constructor
        """
        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn("Deprecated class: Use STBuildingShadow instead")

        if not isinstance(occludersGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(occludersGdf, "GeoDataFrame")
        self.gdf = occludersGdf
        self.crs = occludersGdf.crs

        if occludersElevationFieldname not in occludersGdf:
            raise Exception(
                "%s is not a relevant field name!" % (occludersElevationFieldname)
            )
        self.occludersElevationFieldname = occludersElevationFieldname

        self.altitudeOfShadowPlane = altitudeOfShadowPlane
        self.aggregate = aggregate
        sunModel = SunLib(gdf=occludersGdf, model=model)

        self.sunPositions = DatetimeLib.fromDatetimesDictToListOfSunPositions(
            datetimes, sunModel, tz
        )

    def _auxiliary(self, row, radDir, solarAlti, solarAzim):
        occluderGeom = row.geometry
        occluderElevation = row[self.occludersElevationFieldname]

        if (occluderElevation is None) or (isnan(occluderElevation)):
            return occluderGeom

        if isinstance(occluderGeom, Polygon):
            _shadow = ShadowLib.projectBuildingOntoShadowPlane(
                occluderGeom, occluderElevation, radDir, self.altitudeOfShadowPlane
            )
            if _shadow is not None:
                return _shadow

        elif isinstance(occluderGeom, MultiPolygon):
            _shadows = []
            for g in occluderGeom.geoms:
                _shadow = ShadowLib.projectBuildingOntoShadowPlane(
                    g, occluderElevation, radDir, self.altitudeOfShadowPlane
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
        shadows = STHardShadow(
            buildings,
            dts,
            occludersElevationFieldname="HAUTEUR",
            altitudeOfShadowPlane=0,
            aggregate=False,
            model="pysolar",
        ).run()

        # PLOTTING
        my_cmap = ListedColormap(["red", "green", "blue"])

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        shadows.plot(ax=ax, column="datetime", cmap=my_cmap, alpha=0.25, legend=True)
        buildings.boundary.plot(ax=ax, color="red")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return buildings, shadows, dts


# buildings, shadows, dts = STHardShadow.test()
# buildings.to_file("/tmp/DEBUG.gpkg", layer="buildings1")
# shadows.to_file("/tmp/DEBUG.gpkg", layer="shadows1")
