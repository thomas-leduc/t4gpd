"""
Created on 29 Apr. 2026

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

from numpy import deg2rad, linspace, pi
from pymap3d import geodetic2aer
from shapely import Point, Polygon
from shapely.affinity import translate
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
from t4gpd.commons.proj.AEProjectionLib import AEProjectionLib
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class PANLib(object):
    """
    classdocs
    """

    @staticmethod
    def orbital_inclination_and_altitude(constellation: str):
        """
        GLONASS orbital inclination = 64.8°, altitude = 19100 km
        GPS orbital inclination = 55°, altitude = 20200 km
        GALILEO orbital inclination = 56°, altitude = 23222 km
        """
        match constellation.lower():
            case "glonass":
                return 64.8, 19.1e6
            case "gps":
                return 55, 20.2e6
            case "galileo":
                return 56, 23.222e6
            case _:
                raise IllegalArgumentTypeException(
                    constellation,
                    "supported constellation names: glonass, gps, galileo",
                )

    @staticmethod
    def pot_au_noir(
        lat_observer: float,
        lon_observer: float,
        h_observer: float,
        prj: str,
        size: float,
        orbital_inclination: float = 64.8,
        h_sat: float = 19.1e6,
        npts: int = 36,
    ) -> Polygon:
        """
        GLONASS orbital inclination = 64.8°, altitude = 19100 km
        GPS orbital inclination = 55°, altitude = 20200 km
        GALILEO orbital inclination = 56°, altitude = 23222 km
        """

        def __double_prj(
            lat_observer,
            lon_observer,
            h_observer,
            lat_sat,
            lon_sat,
            h_sat,
            prj,
            size,
            ell=SatelliteLib.WGS84,
        ):
            vp = Point([0, 0])
            # https://geospace-code.github.io/pymap3d/aer.html#pymap3d.aer.geodetic2aer
            # AER: azimuth, elevation, slant range
            az, el, _ = geodetic2aer(
                lat_sat,
                lon_sat,
                h_sat,
                lat_observer,
                lon_observer,
                h_observer,
                ell,
                deg=True,
            )
            # TODO: prkoi 90 ?
            return prj(vp, azim=deg2rad(90 + az), elev=deg2rad(el), size=size)

        prj = AEProjectionLib.projection_switch(prj)
        lat_sat = orbital_inclination

        return Polygon(
            [
                __double_prj(
                    lat_observer,
                    lon_observer,
                    h_observer,
                    lat_sat,
                    lon_sat,
                    h_sat,
                    prj,
                    size,
                )
                for lon_sat in linspace(0, 360, npts, endpoint=False)
            ]
        )

    @staticmethod
    def svf_with_pan(sensors, angles):
        size, epsilon = 1.0, 1e-1
        fullarea = pi * (size + epsilon) ** 2

        smaps_with_pan = PANLib.skymap_with_pan(
            sensors, angles, proj="Isoaire", size=size, epsilon=epsilon, copy=True
        )
        return (fullarea - smaps_with_pan.geometry.area) / fullarea

    @staticmethod
    def skymap_with_pan(sensors, angles, proj, size=1, epsilon=1e-1, copy=True):
        smaps = SkymapBuilder.build(sensors, angles, proj, size, epsilon, copy)
        lat, lon = LatLonLib.fromGeoDataFrameToLatLon(sensors)
        pan = PANLib.pot_au_noir(
            lat_observer=lat,
            lon_observer=lon,
            h_observer=0,
            prj=proj,
            size=size,
        )
        pans = sensors.geometry.apply(lambda g: translate(pan, xoff=g.x, yoff=g.y))
        smaps.geometry = [smap.union(pan) for smap, pan in zip(smaps.geometry, pans)]

        return smaps

    @staticmethod
    def test():
        from matplotlib import pyplot as plt
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        sensors = GeoDataFrameDemos.ensaNantesTrees()
        sensors = sensors.sample(n=3, random_state=0)

        h0, rayLength, nRays = 0.0, 100, 64
        projectionName, size = "Isoaire", 30
        osensors = SensorBasedEncodingLib.encode25D(
            sensors, buildings, "HAUTEUR", h0, rayLength, nRays
        )

        smaps_with_pan = PANLib.skymap_with_pan(
            osensors, "angles", proj=projectionName, size=size, copy=True
        )
        smaps_with_pan["svf_pan"] = PANLib.svf_with_pan(osensors, "angles")

        fig, ax = plt.subplots(figsize=(1.3 * 8.26, 8.26))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="grey")
        sensors.plot(ax=ax, color="red", marker="+", markersize=50)
        smaps_with_pan.plot(ax=ax, color="green", edgecolor="green", alpha=0.85)
        smaps_with_pan.apply(
            lambda x: ax.annotate(
                text=f"{x.svf_pan:.1%}",
                xy=x.geometry.centroid.coords[0],
                color="black",
                size=16,
                ha="center",
                va="bottom",
            ),
            axis=1,
        )
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return smaps_with_pan


# gdf = PANLib.test()
