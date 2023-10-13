'''
Created on 22 sep. 2023

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
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from geopandas import GeoDataFrame
from locale import LC_ALL, setlocale
from numpy import sqrt
from shapely import intersection_all, Point, union_all
from shapely.affinity import rotate, translate
from shapely.geometry import CAP_STYLE
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.sun.STHardShadow import STHardShadow


class WilliamAtkinson(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, rotation=0, position=LatLonLib.NANTES,
                 model="pysolar"):
        '''
        Constructor
        '''
        if ("epsg:4326" != position.crs):
            raise IllegalArgumentTypeException(
                position, "Must be a WGS84 GeoDataFrame")
        self.lat, _ = LatLonLib.fromGeoDataFrameToLatLon(position)
        self.sunModel = SunLib(position, model=model)
        # gdf = position.to_crs(position.estimate_utm_crs(datum_name="WGS 84")) # metric CRS
        # self.x, self.y = gdf.geometry.squeeze().x, gdf.geometry.squeeze().y
        self.rotation = rotation

    def mockup(self, angle):
        geom = Point((0, 0)).buffer(0.5, cap_style=CAP_STYLE.square)
        geom = rotate(geom, angle=angle, origin="center", use_radians=False)
        # geom = translate(geom, xoff=self.x, yoff=self.y)
        return GeoDataFrame([{"geometry": geom, "HAUTEUR": 1.0}])

    def shadows(self, days, angles, delta=30, ofile=None):
        nrows, ncols = len(days), len(angles)
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(
            ncols * 8.26, 8.26), squeeze=False)

        for nr, day in enumerate(days):
            sunrise = self.sunModel.getSunrise(day)
            sunrise += timedelta(minutes=delta)
            sunset = self.sunModel.getSunset(day)
            sunset -= timedelta(minutes=delta)
            # dts = arange(sunrise, sunset, timedelta(minutes=10))
            dts = [(sunrise, sunset, timedelta(minutes=10))]

            for nc, angle in enumerate(angles):
                ax = axes[nr, nc]
                building = self.mockup(angle)
                setlocale(LC_ALL, "en_US.utf8")
                shadows = STHardShadow(building, dts,
                                       occludersElevationFieldname="HAUTEUR",
                                       altitudeOfShadowPlane=0, aggregate=True).run()
                area1 = intersection_all(shadows.geometry).area
                area2 = union_all(shadows.geometry).area

                ax.set_title(
                    f"{sunrise.strftime('%b %d: %H:%M')} - {sunset.strftime('%H:%M')}, {self.lat:+.1f}°N, {area1:.1f} m$^2$, {area2:.1f} m$^2$")
                shadows.boundary.plot(ax=ax, color="grey", linewidth=0.5)
                building.plot(ax=ax, color="black")

        if ofile is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)


"""
WilliamAtkinson().shadows(days=[datetime(2023, 12, 21), datetime(
    2023, 3, 21), datetime(2023, 6, 21)], angles=[0, 45])
"""
