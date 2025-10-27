"""
Created on 15 mars 2022

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
from matplotlib.colors import ListedColormap
from numpy import ndarray
from shapely.affinity import translate, scale
from shapely.geometry import Point, Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STBBox import STBBox


class STCompass(GeoProcess):
    """
    classdocs
    """

    LOCATIONS = ["lower left", "lower right", "upper left", "upper right"]

    def __init__(
        self, basemap, bounds, crs, magnitude=0.015, bgcolor=None, location="upper left"
    ):
        """
        Constructor
        """
        self.basemap = basemap
        self.crs = crs
        self.magnitude = magnitude
        self.bgcolor = bgcolor

        if isinstance(bounds, (list, tuple, ndarray)) and (4 == len(bounds)):
            self.bounds = bounds
        else:
            raise IllegalArgumentTypeException(bounds, "box (minx, miny, maxx, maxy)")

        if location.lower() in STCompass.LOCATIONS:
            self.location = location.lower()
        else:
            raise IllegalArgumentTypeException(location, STCompass.LOCATIONS)

    @staticmethod
    def __letter():
        h, w = 1.45, 0.45
        return Polygon(
            [
                (-0.5 - w, 3),
                (-0.5, 3),
                (-0.5, 3 + h - w),
                (0.5, 3),
                (0.5 + w, 3),
                (0.5 + w, 3 + h),
                (0.5, 3 + h),
                (0.5, 3 + w),
                (-0.5, 3 + h),
                (-0.5 - w, 3 + h),
            ]
        )

    @staticmethod
    def __left_arrow():
        return Polygon([(0, 0), (0, 2), (-2, -1.5)])

    @staticmethod
    def __right_arrow():
        return Polygon([(0, 0), (2, -1.5), (0, 2)])

    def __translation_and_dilation(self, arrow):
        minx, miny, maxx, maxy = self.bounds

        deltax, deltay = maxx - minx, maxy - miny
        delta = min(deltax, deltay)

        arrow = scale(
            arrow,
            xfact=self.magnitude * delta,
            yfact=self.magnitude * delta,
            origin=Point([0, 0]),
        )
        match self.location:
            case "lower left":
                xoff = minx + 2 * self.magnitude * delta
                yoff = miny + 4.5 * self.magnitude * delta
            case "lower right":
                xoff = maxx - 2 * self.magnitude * delta
                yoff = miny + 4.5 * self.magnitude * delta
            case "upper left":
                xoff = minx + 2 * self.magnitude * delta
                yoff = maxy - 4.5 * self.magnitude * delta
            case "upper right":
                xoff = maxx - 2 * self.magnitude * delta
                yoff = maxy - 4.5 * self.magnitude * delta

        arrow = translate(
            arrow,
            xoff=xoff,
            yoff=yoff,
        )
        return arrow

    def run(self):
        _left_arrow = self.__translation_and_dilation(self.__left_arrow())
        _right_arrow = self.__translation_and_dilation(self.__right_arrow())
        _letter = self.__translation_and_dilation(self.__letter())

        my_rgb_cmap = ListedColormap(["white", "black", "black"])

        gdf = GeoDataFrame(
            [
                {"gid": 0, "geometry": _left_arrow},
                {"gid": 1, "geometry": _right_arrow},
                {"gid": 2, "geometry": _letter},
            ],
            crs=self.crs,
        )

        if self.bgcolor is not None:
            bb = STBBox(gdf, buffDist=3).run()
            bb.plot(ax=self.basemap, color=self.bgcolor, alpha=0.35)

        gdf.plot(ax=self.basemap, edgecolor="black", column="gid", cmap=my_rgb_cmap)

        return gdf


"""
import matplotlib.pyplot as plt
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

buildings = GeoDataFrameDemos.ensaNantesBuildings()

fig, ax = plt.subplots()
buildings.plot(ax=ax)
STCompass(
    ax, buildings.total_bounds, buildings.crs, magnitude=0.015, location="lower left"
).run()
plt.show()
"""
