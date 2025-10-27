"""
Created on 13 Sep. 2025

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
from numpy import deg2rad, ndarray, r_, rad2deg
from pandas import DataFrame, concat
from shapely import LineString, Point
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.SVFLib import SVFLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class STPathOrientedSVF(AbstractGeoprocess):
    """
    classdocs
    """

    __slots__ = (
        "skymaps",
        "viewpointFieldname",
        "anglesFieldname",
        "commons",
        "svf",
        "slices",
    )

    def __init__(
        self,
        skymaps,
        viewpointFieldname="viewpoint",
        anglesFieldname="angles",
        method="quadrants",
        svf=2018,
    ):
        """
        Constructor
        """
        if not isinstance(skymaps, GeoDataFrame):
            raise IllegalArgumentTypeException(skymaps, "GeoDataFrame")
        self.skymaps = skymaps

        if viewpointFieldname not in skymaps:
            raise Exception(f"{anglesFieldname} is not a relevant field name!")
        self.viewpointFieldname = viewpointFieldname

        if anglesFieldname not in skymaps:
            raise Exception(f"{anglesFieldname} is not a relevant field name!")
        self.anglesFieldname = anglesFieldname

        method = method.lower()
        if "quadrants" == method:
            offset = 8
        elif "octants" == method:
            offset = 16
        elif "duodecants" == method:
            offset = 24
        else:
            raise IllegalArgumentTypeException(
                method, "'quadrants', 'octants', or 'duodecants'"
            )

        for angles in self.skymaps[self.anglesFieldname]:
            if isinstance(angles, (list, ndarray, tuple)) and (
                0 == len(angles) % offset
            ):
                n = len(angles) // offset
            else:
                raise Exception(
                    f"\n{angles}\n\nmust be a collection of angles whose length is a multiple of {offset}."
                )

        if 1981 == svf:
            print(f"SVF calculation method: Oke (1981)")
            self.svf = SVFLib.svfAngles1981
        else:
            print(f"SVF calculation method: Bernard et al. (2018)")
            self.svf = SVFLib.svfAngles2018

        if 8 == offset:
            self.slices = {
                "svf4_front": r_[slice(7 * n, 8 * n), slice(0, n)],
                "svf4_left": slice(n, 3 * n),
                "svf4_back": slice(3 * n, 5 * n),
                "svf4_right": slice(5 * n, 7 * n),
            }
        elif 16 == offset:
            self.slices = {
                "svf8_front": r_[slice(15 * n, 16 * n), slice(0, n)],
                "svf8_frontleft": slice(n, 3 * n),
                "svf8_left": slice(3 * n, 5 * n),
                "svf8_backleft": slice(5 * n, 7 * n),
                "svf8_back": slice(7 * n, 9 * n),
                "svf8_backright": slice(9 * n, 11 * n),
                "svf8_right": slice(11 * n, 13 * n),
                "svf8_frontright": slice(13 * n, 15 * n),
            }
        elif 24 == offset:
            self.slices = {
                "svf12_front": r_[slice(23 * n, 24 * n), slice(0, n)],
                "svf12_ffl": slice(n, 3 * n),
                "svf12_lfl": slice(3 * n, 5 * n),
                "svf12_left": slice(5 * n, 7 * n),
                "svf12_lbl": slice(7 * n, 9 * n),
                "svf12_bbl": slice(9 * n, 11 * n),
                "svf12_back": slice(11 * n, 13 * n),
                "svf12_bbr": slice(13 * n, 15 * n),
                "svf12_rbr": slice(15 * n, 17 * n),
                "svf12_right": slice(17 * n, 19 * n),
                "svf12_rfr": slice(19 * n, 21 * n),
                "svf12_ffr": slice(21 * n, 23 * n),
            }
        else:
            raise Exception("Unreachable instruction!")

        self.commons = ["__prev", "__next", "__offset"]

    def __slices(self, angles, offset):
        def __get_angles(angles, slc, offset):
            n = len(angles)
            return [angles[(i + offset) % n] for i in r_[slc]]

        return {
            k: self.svf(deg2rad(__get_angles(angles, v, offset)))
            for k, v in self.slices.items()
        }

    def __to_linestring(self, row):
        _prev, _curr, _next = row["__prev"], row[self.viewpointFieldname], row["__next"]
        _prev = _curr if _prev is None else _prev
        _next = _curr if _next is None else _next
        _dist = 0.2 * _prev.distance(_next)
        _rp = Point(
            [
                _curr.x + (_next.x - _prev.x) / _dist,
                _curr.y + (_next.y - _prev.y) / _dist,
            ]
        )
        return LineString([GeomLib.removeZCoordinate(_curr), _rp])

    def __to_offset(self, row):
        _prev, _curr, _next = row["__prev"], row[self.viewpointFieldname], row["__next"]
        _prev = _curr if _prev is None else _prev
        _next = _curr if _next is None else _next
        _dist = _prev.distance(_next)
        _curr_dx = [_curr.x + 1, _curr.y]
        _rp = [
            _curr.x + (_next.x - _prev.x) / _dist,
            _curr.y + (_next.y - _prev.y) / _dist,
        ]
        _curr = [_curr.x, _curr.y]
        azim = AngleLib.angleBetweenNodes(_curr_dx, _curr, _rp)
        nslices = len(row[self.anglesFieldname])
        offset = AngleLib.fromEastCCWAzimuthToSliceId(azim, nslices, degree=False)
        # return f"{rad2deg(azim)} -> {offset}"
        return offset

    def run(self):

        gdf = GeoDataFrame(
            concat([self.skymaps, DataFrame(columns=self.commons)]),
            crs=self.skymaps.crs,
        )
        gdf["__prev"] = gdf[self.viewpointFieldname].shift(1)
        gdf["__next"] = gdf[self.viewpointFieldname].shift(-1)
        # gdf.geometry = gdf.apply(  ### DEBUG
        #     lambda row: self.__to_linestring(row), axis=1
        # )
        gdf["__offset"] = gdf.apply(lambda row: self.__to_offset(row), axis=1)

        df = DataFrame(
            gdf.apply(
                lambda row: self.__slices(row[self.anglesFieldname], row["__offset"]),
                axis=1,
            ).to_list(),
            index=gdf.index,
        )
        gdf = GeoDataFrame(concat([gdf, df], axis=1), crs=self.skymaps.crs)

        gdf.drop(columns=self.commons, inplace=True)
        return gdf

    @staticmethod
    def test(method="octants"):
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STPointsDensifier import STPointsDensifier
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        paths = GeoDataFrameDemos.districtRoyaleInNantesPaths()
        paths = paths.loc[paths[paths.gid == 2].index]
        sensors = STPointsDensifier(paths, distance=30.0, pathidFieldname="gid").run()

        from shapely import box

        buildings = GeoDataFrame(
            [
                {"ID": 1, "HAUTEUR": 10, "geometry": box(5, -50, 15, 50)},
                {"ID": 2, "HAUTEUR": 10, "geometry": box(-15, -50, -6, 50)},
            ],
            crs="epsg:2154",
        )
        paths = GeoDataFrame(
            [
                {"gid": 1, "geometry": LineString([(0, -100), (0, 100)])},
            ],
            crs="epsg:2154",
        )

        sensors = STPointsDensifier(paths, distance=10.0, pathidFieldname="gid").run()
        sensors.gid = range(len(sensors))
        nRays = 96  # 48
        skymaps = STSkyMap25D(
            buildings,
            sensors,
            nRays=nRays,
            rayLength=100,
            elevationFieldname="HAUTEUR",
            h0=0,
            size=4,
            withIndices=True,
            withAngles=True,
            encode=False,
        ).run()

        indics = STPathOrientedSVF(skymaps, "viewpoint", "angles", method=method).run()
        # print(indics["__offset"])

        # PLOTTING
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.15 * 8.26))
        buildings.plot(ax=ax, color="grey")
        paths.plot(ax=ax, color="lightgrey", linestyle=":")
        skymaps.plot(ax=ax, color="yellow")
        indics.plot(ax=ax, color="blue", linewidth=4)
        sensors.plot(ax=ax, color="red", marker="P")
        sensors.apply(
            lambda x: ax.annotate(
                text=x.gid,
                xy=x.geometry.coords[0][:2],
                color="red",
                size=10,
                ha="left",
                va="top",
            ),
            axis=1,
        )

        if "svf4_front" in indics:
            f, r, b, l = "svf4_front", "svf4_right", "svf4_back", "svf4_left"
        elif "svf8_front" in indics:
            f, r, b, l = "svf8_front", "svf8_right", "svf8_back", "svf8_left"
        elif "svf12_front" in indics:
            f, r, b, l = "svf12_front", "svf12_right", "svf12_back", "svf12_left"
        indics.apply(
            lambda x: ax.annotate(
                text=f"f={100*x[f]:.1f} r={100*x[r]:.1f} b={100*x[b]:.1f} l={100*x[l]:.1f}",
                xy=x.geometry.centroid.coords[0][:2],
                color="black",
                size=12,
                ha="left",
                va="top",
            ),
            axis=1,
        )
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return skymaps, indics


# skymaps, indics = STPathOrientedSVF.test(method="quadrants")
# skymaps, indics = STPathOrientedSVF.test(method="octants")
# skymaps, indics = STPathOrientedSVF.test(method="duodecants")
# print(indics[[c for c in indics.columns if c.startswith("svf")]])

# if "svf4_front" in indics:
#     cols = [c for c in indics.columns if c.startswith("svf4")]
# elif "svf8_front" in indics:
#     cols = [c for c in indics.columns if c.startswith("svf8")]
# elif "svf12_front" in indics:
#     cols = [c for c in indics.columns if c.startswith("svf12")]
# assert all(((indics.svf - indics[cols].mean(axis=1)).abs() < 1e-9))
