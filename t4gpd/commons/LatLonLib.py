"""
Created on 20 janv. 2021

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

from warnings import warn

from geopandas import GeoDataFrame
from numpy import abs
from shapely import box, Point
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class LatLonLib(object):
    """
    classdocs
    """

    ALGER = GeoDataFrame([{"geometry": Point((3.042048, 36.752887))}], crs="epsg:4326")
    AVIGNON = GeoDataFrame([{"geometry": Point((4.80892, 43.94834))}], crs="epsg:4326")
    CAP_TOWN = GeoDataFrame(
        [{"geometry": Point((18.42322, -33.92584))}], crs="epsg:4326"
    )
    DAKAR = GeoDataFrame([{"geometry": Point((-17.444061, 14.6937))}], crs="epsg:4326")
    EDINBURGH = GeoDataFrame(
        [{"geometry": Point((-3.188267, 55.953252))}], crs="epsg:4326"
    )
    GREENWICH = GeoDataFrame(
        [{"geometry": Point((-0.001545, 51.477928))}], crs="epsg:4326"
    )
    LAGOS = GeoDataFrame([{"geometry": Point((3.379206, 6.524379))}], crs="epsg:4326")
    LILLE = GeoDataFrame(
        [{"geometry": Point((3.0585800, 50.6329700))}], crs="epsg:4326"
    )
    # outside the polar circles ; latitude must be between -66.56 and +66.56
    # LONGYEARBYEN = GeoDataFrame([{"geometry": Point((-15.6258907, 78.2253594))}], crs="epsg:4326")
    MONTPELLIER = GeoDataFrame(
        [{"geometry": Point((3.87723, 43.61092))}], crs="epsg:4326"
    )
    NANTES = GeoDataFrame([{"geometry": Point((-1.55, 47.2))}], crs="epsg:4326")
    NIAMEY = GeoDataFrame([{"geometry": Point((2.1098, 13.51366))}], crs="epsg:4326")
    QUITO = GeoDataFrame([{"geometry": Point((-78.52495, -0.22985))}], crs="epsg:4326")
    REYKJAVIK = GeoDataFrame(
        [{"geometry": Point((-21.89541, 64.13548))}], crs="epsg:4326"
    )

    @staticmethod
    def fromGeoDataFrameToLatLon(gdf=NANTES):
        """
        Extract latitude and longitude from a GeoDataFrame.
        :param gdf: GeoDataFrame containing the geometry.
        :return: A tuple (latitude, longitude) representing the centroid of the geometries in the GeoDataFrame.
        If the input parameter is not set, it defaults to NANTES.
        """
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        if gdf.crs is None:
            warn("Crs is not set!")
            gdf = LatLonLib.NANTES

        _gdf = gdf if ("epsg:4326" == gdf.crs) else gdf.to_crs("epsg:4326")
        _centroid = box(*_gdf.total_bounds).centroid
        _latitude, _longitude = _centroid.y, _centroid.x
        return _latitude, _longitude

    @staticmethod
    def decimalDegree2sexagesimalDegree(angle, ndigits=1):
        """
        Convert a decimal degree angle to a sexagesimal degree angle.
        :param angle: Decimal degree angle to convert.
        :param ndigits: Number of digits after the decimal point for seconds.
        :return: A tuple (degrees, minutes, seconds) representing the sexagesimal degree angle.
        0 <= seconds < 60
        0 <= minutes < 60
        0 <= degrees < 360
        The sign of the angle is preserved, with negative angles indicating southern or western hemispheres.
        """
        _angle = abs(angle)
        d = int(_angle)
        m = int((_angle - d) * 60)
        s = round(((_angle - d) * 60 - m) * 60, ndigits)
        d = -d if (angle < 0) else d
        return d, m, s

    @staticmethod
    def latlon_to_str(gdf):
        """
        Convert a GeoDataFrame to a string representation of latitude and longitude in sexagesimal format.
        :param gdf: GeoDataFrame containing the geometry.
        :return: A string formatted as "latitude, longitude".
        """
        lat, lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        lat = LatLonLib.sexagesimalDegreePrettyPrinter(
            LatLonLib.decimalDegree2sexagesimalDegree(lat), opt="latitude"
        )
        lon = LatLonLib.sexagesimalDegreePrettyPrinter(
            LatLonLib.decimalDegree2sexagesimalDegree(lon), opt="longitude"
        )
        return f"{lat}, {lon}"

    @staticmethod
    def sexagesimalDegreePrettyPrinter(angle, opt=None):
        """
        Pretty print a sexagesimal degree angle.
        :param angle: A tuple (degrees, minutes, seconds) representing the angle.
        :param opt: Optional parameter to specify if the angle is latitude or longitude.
        :return: A formatted string representation of the angle.
        """
        d, m, s = angle

        if "latitude" == opt:
            orient = "N" if (0 < d) else "S"
        elif "longitude" == opt:
            orient = "E" if (0 < d) else "W"
        else:
            return f"{d:.0f}° {m:.0f}′ {s}″"

        return f"{abs(d):.0f}° {m:.0f}′ {s}″ {orient}"
