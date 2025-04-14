"""
Created on 22 sep. 2023

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

import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from pandas import Timestamp, concat, date_range
from shapely import box, intersection_all, union_all
from shapely.affinity import rotate, translate
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunModel import SunModel
from t4gpd.shadow.STBuildingShadow import STBuildingShadow


class WilliamAtkinson(GeoProcess):
    """
    classdocs
    """

    def __init__(self, gdf, angles, dts, freq="10min", model="pvlib"):
        """
        Constructor
        """
        if not gdf.crs.is_projected:
            raise IllegalArgumentTypeException(gdf, "Must be a projected GeoDataFrame")

        self.gdf = gdf
        self.angles = angles
        self.dts = dts
        self.freq = freq
        self.model = model

        sunModel = SunModel(gdf, altitude=0, model=model)
        self.sun_rise_sets = sunModel.sun_rise_set(self.dts)
        self.shadows = None

    def build_a_unit_volume(self, angle):
        dx, dy, _, _ = self.gdf.total_bounds
        geom = box(-0.5, -0.5, 0.5, 0.5)
        geom = rotate(geom, angle=angle, origin="center", use_radians=False)
        geom = translate(geom, xoff=dx, yoff=dy)
        return GeoDataFrame([{"geometry": geom, "HAUTEUR": 1.0}], crs=self.gdf.crs)

    def plot(self, ofile=None):
        if self.shadows is None:
            self.shadows = self.run()

        days, angles = self.shadows.day.unique(), self.shadows.angle.unique()
        nrows, ncols = len(days), len(angles)

        lat, _ = LatLonLib.fromGeoDataFrameToLatLon(self.shadows)

        fig, axes = plt.subplots(
            nrows=nrows, ncols=ncols, figsize=(ncols * 8.26, 8.26), squeeze=False
        )

        shadows = self.shadows.copy(deep=True)
        shadows.day = shadows.day.astype(str)

        for nc, angle in enumerate(angles):
            building = self.build_a_unit_volume(angle)

            for nr, day in enumerate(days):
                sunrise = self.sun_rise_sets.loc[day, "sunrise"]
                sunset = self.sun_rise_sets.loc[day, "sunset"]

                ax = axes[nr, nc]
                _shadows = shadows.query(
                    f"(day == '{str(day)}') and (angle == {angle})"
                )
                area1 = intersection_all(_shadows.geometry).area
                area2 = union_all(_shadows.geometry).area

                ax.set_title(
                    f"{sunrise.strftime('%b %d: %H:%M')} - {sunset.strftime('%H:%M')}, {lat:+.1f}°N, {area1:.1f} m$^2$, {area2:.1f} m$^2$"
                )
                _shadows.boundary.plot(ax=ax, color="grey", linewidth=0.5)
                building.plot(ax=ax, color="black")
                ax.axis("off")
        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    def run(self):
        shadows = []
        for angle in self.angles:
            building = self.build_a_unit_volume(angle)

            for day, row in self.sun_rise_sets.iterrows():
                sunrise, sunset = row["sunrise"], row["sunset"]
                dts = date_range(start=sunrise, end=sunset, freq=self.freq)
                _shadows = STBuildingShadow(
                    building,
                    dts,
                    elevationFieldName="HAUTEUR",
                    altitudeOfShadowPlane=0,
                    aggregate=True,
                    model=self.model,
                ).run()
                _shadows["day"] = day
                _shadows["angle"] = angle
                shadows.append(_shadows)

        shadows = GeoDataFrame(concat(shadows), crs=self.gdf.crs)
        return shadows


"""
dts = [Timestamp(f"2025-{m}-21", tz="UTC") for m in [12, 3, 6]]
wa = WilliamAtkinson(
    LatLonLib.NANTES.to_crs("epsg:2154"), angles=[0, 45], dts=dts, model="pvlib"
)
shadows = wa.run()
wa.plot()
wa.build_a_unit_volume(0).to_file("/tmp/1.gpkg", layer="building")
shadows.to_file("/tmp/1.gpkg", layer="shadows")
"""
