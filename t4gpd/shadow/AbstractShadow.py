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
from numpy import deg2rad
from pandas import merge
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeoProcess import GeoProcess


class AbstractShadow(GeoProcess):
    """
    classdocs
    """

    def run(self):
        self.gdf["__PK__"] = range(len(self.gdf))
        masks = self.gdf.copy()

        # Hypothesis: the shadow cast by a 1m high mask is at most 10m long
        # rad2deg(arctan2(1,10)) > 5.71
        sunPos = (
            self.sunPositions.query(f"apparent_elevation > 5.71")
            .reset_index()
            .loc[:, ["index", "sun_beam_direction", "apparent_elevation", "azimuth"]]
            .rename(columns={"index": "datetime", "apparent_elevation": "elevation"})
        )
        sunPos["elevation_rad"] = deg2rad(sunPos.elevation)
        sunPos["azimuth_rad"] = deg2rad(
            AngleLib.northCW2eastCCW(sunPos.azimuth, degree=True)
        )

        # CARTESIAN PRODUCT
        shadows = merge(masks, sunPos, how="cross")
        shadows.geometry = shadows.apply(
            lambda row: self._auxiliary(
                row, row.sun_beam_direction, row.elevation_rad, row.azimuth_rad
            ),
            axis=1,
        )

        if self.aggregate:
            shadows = shadows[["datetime", "geometry"]].dissolve(by="datetime")
            # Use a buffer to avoid slivers
            shadows.geometry = shadows.buffer(1e-3, -1)
            shadows.reset_index(inplace=True)
        else:
            # ATTRIBUTE JOIN USING __PK__
            shadows = merge(
                self.gdf.drop(columns="geometry"),
                shadows[["__PK__", "datetime", "geometry"]],
                how="inner",
                on="__PK__",
            )
            shadows.drop(columns=["__PK__"], inplace=True)

        self.gdf.drop(columns="__PK__", inplace=True)
        shadows = GeoDataFrame(shadows, crs=self.gdf.crs)
        return shadows
