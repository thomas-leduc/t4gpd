"""
Created on 5 Jan. 2026

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

from geopandas import GeoDataFrame
from numpy import (
    asarray,
    cos,
    exp,
    linspace,
    max,
    mean,
    median,
    min,
    pi,
    quantile,
    r_,
    sin,
    stack,
    std,
)
from pandas import DataFrame, concat
from scipy.stats import kurtosis, skew
from shapely import Point, polygons
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.AzimuthOfTravelLib import AzimuthOfTravelLib
from t4gpd.commons.DataFrameLib import DataFrameLib
from t4gpd.commons.Entropy import Entropy
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.SVFLib import SVFLib
from t4gpd.commons.morph.CircularityLib import CircularityLib
from t4gpd.commons.morph.ConvexityLib import ConvexityLib
from t4gpd.commons.morph.EllipticityLib import EllipticityLib
from t4gpd.commons.morph.LinearRegressionLib import LinearRegressionLib
from t4gpd.commons.morph.RectangularityLib import RectangularityLib
from t4gpd.commons.sat.PANLib import PANLib


class EncodingIndices(object):
    """
    classdocs
    """

    @staticmethod
    def __generic_indices(meth, sensors, raylen, suffix, copy):
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if raylen not in sensors.columns:
            raise IllegalArgumentTypeException(raylen, "sensors' column name")

        geoms = EncodingIndices.__raylens_to_polygon(sensors, raylen)
        df = DataFrame(
            geoms.apply(
                lambda geom: meth(geom, with_geom=False, suffix=suffix)
            ).to_list(),
            index=sensors.index,
        )
        return concat([sensors, df], axis=1, copy=copy)

    @staticmethod
    def __raylens_to_polygon(sensors, raylen):
        n = sensors[raylen].apply(lambda t: len(t)).unique()
        if 1 == len(n):
            n = n[0]
        else:
            raise Exception(f"{raylen} is a not a valid column (incoherent sizes)!")
        angles = linspace(0, 2.0 * pi, n, endpoint=False)
        arr_cos, arr_sin = cos(angles), sin(angles)

        return sensors[raylen].apply(
            lambda raylens: polygons(
                stack([raylens * arr_cos, raylens * arr_sin], axis=1)
            )
        )

    @staticmethod
    def circularity_indices(sensors, raylen, suffix="", copy=True):
        return EncodingIndices.__generic_indices(
            CircularityLib.get_indices, sensors, raylen, suffix, copy
        )

    @staticmethod
    def convexity_indices(sensors, raylen, suffix="", copy=True):
        return EncodingIndices.__generic_indices(
            ConvexityLib.get_indices, sensors, raylen, suffix, copy
        )

    @staticmethod
    def ellipticity_indices(sensors, raylen, suffix="", copy=True):
        return EncodingIndices.__generic_indices(
            EllipticityLib.get_indices, sensors, raylen, suffix, copy
        )

    @staticmethod
    def linear_regression_indices(sensors, raylen, suffix="", copy=True):
        return EncodingIndices.__generic_indices(
            LinearRegressionLib.get_indices, sensors, raylen, suffix, copy
        )

    @staticmethod
    def raylen_indices(
        sensors, raylen="raylen2D", copy=True, precision=1.0, base=exp(1)
    ):
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if raylen not in sensors.columns:
            raise IllegalArgumentTypeException(raylen, "sensors' column name")

        mapping = {
            f"min_{raylen}": min,
            f"avg_{raylen}": mean,
            f"std_{raylen}": std,
            f"max_{raylen}": max,
            f"q1_{raylen}": lambda v: quantile(v, 0.25),
            f"med_{raylen}": median,
            f"q3_{raylen}": lambda v: quantile(v, 0.75),
            f"skew_{raylen}": skew,
            f"kurt_{raylen}": lambda v: kurtosis(v, fisher=True, bias=True),
            f"H_{raylen}": lambda v: Entropy.createFromDoubleValuesArray(
                v, precision
            ).h(base),
            f"drift_{raylen}": lambda _: None,
        }

        df = DataFrame(columns=mapping.keys(), index=sensors.index)
        for k, v in mapping.items():
            df[k] = sensors[raylen].apply(v)

        origin = Point([0, 0])
        df[f"drift_{raylen}"] = EncodingIndices.__raylens_to_polygon(sensors, raylen)
        df[f"drift_{raylen}"] = df[f"drift_{raylen}"].apply(
            lambda g: origin.distance(g.centroid)
        )
        return concat([sensors, df], axis=1, copy=copy)

    @staticmethod
    def rectangularity_indices(sensors, raylen="raylen2D", suffix="", copy=True):
        return EncodingIndices.__generic_indices(
            RectangularityLib.get_indices, sensors, raylen, suffix, copy
        )

    @staticmethod
    def svf_indices(sensors, angles, copy=True):
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if angles not in sensors.columns:
            raise IllegalArgumentTypeException(angles, "sensors' column name")

        mapping = {"svf_rad": SVFLib.svfAngles2026, "svf_geom": SVFLib.svfAngles2018}

        df = DataFrame(columns=mapping.keys(), index=sensors.index)
        for k, v in mapping.items():
            df[k] = sensors[angles].apply(v)

        return concat([sensors, df], axis=1, copy=copy)

    @staticmethod
    def svf_oriented_indices(sensors, angles, oriented="quadrants", copy=True):
        OFFSETS = {"quadrants": 8, "octants": 16, "duodecants": 24}
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if angles not in sensors.columns:
            raise IllegalArgumentTypeException(angles, "sensors' column name")
        if oriented not in ["quadrants", "octants", "duodecants"]:
            raise IllegalArgumentTypeException(
                oriented,
                "oriented as 'quadrants', 'octants', or 'duodecants'",
            )

        # PREPARE ORIENTED SVF
        N = sensors[angles].apply(lambda t: len(t)).unique()
        if 1 == len(N):
            N = N[0]
        else:
            raise Exception(f"{angles} is a not a valid column (incoherent sizes)!")

        offset = OFFSETS[oriented]
        if 0 < N % offset:
            raise IllegalArgumentTypeException(N, f"multiple of {offset}")
        n = N // offset

        match oriented:
            case "quadrants":
                slices = {
                    "svf4_east": r_[slice(7 * n, 8 * n), slice(0, n)],
                    "svf4_north": slice(n, 3 * n),
                    "svf4_west": slice(3 * n, 5 * n),
                    "svf4_south": slice(5 * n, 7 * n),
                }
            case "octants":
                slices = {
                    "svf8_east": r_[slice(15 * n, 16 * n), slice(0, n)],
                    "svf8_northeast": slice(n, 3 * n),
                    "svf8_north": slice(3 * n, 5 * n),
                    "svf8_northwest": slice(5 * n, 7 * n),
                    "svf8_west": slice(7 * n, 9 * n),
                    "svf8_southwest": slice(9 * n, 11 * n),
                    "svf8_south": slice(11 * n, 13 * n),
                    "svf8_southeast": slice(13 * n, 15 * n),
                }
            case "duodecants":
                slices = {
                    "svf12_e": r_[slice(23 * n, 24 * n), slice(0, n)],
                    "svf12_ene": slice(n, 3 * n),
                    "svf12_nne": slice(3 * n, 5 * n),
                    "svf12_n": slice(5 * n, 7 * n),
                    "svf12_nnw": slice(7 * n, 9 * n),
                    "svf12_wnw": slice(9 * n, 11 * n),
                    "svf12_w": slice(11 * n, 13 * n),
                    "svf12_wsw": slice(13 * n, 15 * n),
                    "svf12_ssw": slice(15 * n, 17 * n),
                    "svf12_s": slice(17 * n, 19 * n),
                    "svf12_sse": slice(19 * n, 21 * n),
                    "svf12_ese": slice(21 * n, 23 * n),
                }

        mapping = {}
        for k, v in slices.items():
            mapping[f"{k}_rad"] = lambda a, idx=v: SVFLib.svfAngles2026(asarray(a)[idx])
            mapping[f"{k}_geom"] = lambda a, idx=v: SVFLib.svfAngles2018(
                asarray(a)[idx]
            )

        df = DataFrame(columns=mapping.keys(), index=sensors.index)
        for k, v in mapping.items():
            df[k] = sensors[angles].apply(v)

        return concat([sensors, df], axis=1, copy=copy)

    @staticmethod
    def svf_pan_indices(sensors, angles, copy=True):
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if angles not in sensors.columns:
            raise IllegalArgumentTypeException(angles, "sensors' column name")

        df = DataFrame(columns=["svf_pan"], index=sensors.index)
        df["svf_pan"] = PANLib.svf_with_pan(sensors, angles)
        return concat([sensors, df], axis=1, copy=copy)

    @staticmethod
    def svf_path_oriented_indices(
        sensors, angles, azimuth, oriented="quadrants", copy=True
    ):
        def __slices(angles, offset, slices):
            def __get_angles(angles, slc, offset):
                n = len(angles)
                return [angles[(i + offset) % n] for i in r_[slc]]

            mapping = {}
            for k, v in slices.items():
                _angles = __get_angles(angles, v, offset)
                mapping[f"{k}_rad"] = SVFLib.svfAngles2026(_angles)
                mapping[f"{k}_geom"] = SVFLib.svfAngles2018(_angles)
            return mapping

        OFFSETS = {"bissants": 8, "quadrants": 8, "octants": 16, "duodecants": 24}
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if angles not in sensors.columns:
            raise IllegalArgumentTypeException(angles, "sensors' column name")
        if azimuth not in sensors.columns:
            raise IllegalArgumentTypeException(azimuth, "sensors' column name")
        if oriented not in ["bissants", "quadrants", "octants", "duodecants"]:
            raise IllegalArgumentTypeException(
                oriented,
                "oriented as 'quadrants', 'octants', or 'duodecants'",
            )

        # PREPARE PATH-ORIENTED SVF
        N = sensors[angles].apply(lambda t: len(t)).unique()
        if 1 == len(N):
            N = N[0]
        else:
            raise Exception(f"{angles} is a not a valid column (incoherent sizes)!")

        offset = OFFSETS[oriented]
        if 0 < N % offset:
            raise IllegalArgumentTypeException(N, f"multiple of {offset}")
        n = N // offset

        match oriented:
            case "bissants":
                slices = {
                    "svf4_front_back": r_[
                        slice(3 * n, 5 * n), slice(7 * n, 8 * n), slice(0, n)
                    ],
                    "svf4_left_right": r_[slice(n, 3 * n), slice(5 * n, 7 * n)],
                }
            case "quadrants":
                slices = {
                    "svf4_front": r_[slice(7 * n, 8 * n), slice(0, n)],
                    "svf4_left": slice(n, 3 * n),
                    "svf4_back": slice(3 * n, 5 * n),
                    "svf4_right": slice(5 * n, 7 * n),
                }
            case "octants":
                slices = {
                    "svf8_front": r_[slice(15 * n, 16 * n), slice(0, n)],
                    "svf8_frontleft": slice(n, 3 * n),
                    "svf8_left": slice(3 * n, 5 * n),
                    "svf8_backleft": slice(5 * n, 7 * n),
                    "svf8_back": slice(7 * n, 9 * n),
                    "svf8_backright": slice(9 * n, 11 * n),
                    "svf8_right": slice(11 * n, 13 * n),
                    "svf8_frontright": slice(13 * n, 15 * n),
                }
            case "duodecants":
                slices = {
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

        _offset = DataFrameLib.getNewColumnName(sensors)
        sensors[_offset] = sensors[azimuth].apply(
            lambda azim: AngleLib.fromEastCCWAzimuthToSliceId(azim, N, degree=False)
        )

        df = DataFrame(
            sensors.apply(
                lambda row: __slices(row[angles], row[_offset], slices),
                axis=1,
            ).to_list(),
            index=sensors.index,
        )
        sensors = concat([sensors, df], axis=1, copy=copy)
        sensors.drop(columns=[_offset], inplace=True)
        return sensors

    @staticmethod
    def test():
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        dx, h0, rayLength, nRays = 100, 1.1, 45, 64

        buildings = GeoDataFrameDemos.ensaNantesBuildings()

        sensors = FastGridLib.grid(buildings, dx, intoPoint=True, withRowsCols=False)
        sensors = PointsInPolygonsLib.outdoors(sensors, buildings)

        # osensors = SensorBasedEncodingLib.encode2D(sensors, buildings, rayLength, nRays)
        osensors = SensorBasedEncodingLib.encode2D25D(
            sensors,
            buildings,
            elevationFieldname="HAUTEUR",
            h0=h0,
            rayLength=rayLength,
            nRays=nRays,
        )
        osensors = AzimuthOfTravelLib.add_ccw_azimuth_of_travel(osensors, degree=False)

        # osensors = EncodingIndices.raylen_indices(osensors, raylen="raylen2D")
        # osensors = EncodingIndices.raylen_indices(osensors, raylen="raylen25D")
        # osensors = EncodingIndices.raylen_indices(osensors, raylen="h_over_w")
        # osensors = EncodingIndices.svf_indices(osensors, angles="angles")
        # osensors = EncodingIndices.svf_oriented_indices(
        #     osensors, angles="angles", oriented="quadrants"
        # )
        # osensors = EncodingIndices.svf_oriented_indices(
        #     osensors, angles="angles", oriented="octants"
        # )
        # osensors = EncodingIndices.svf_oriented_indices(
        #     osensors, angles="angles", oriented="duodecants"
        # )
        # osensors = EncodingIndices.svf_path_oriented_indices(
        #     osensors, angles="angles", azimuth="azimuth", oriented="bissants"
        # )
        # osensors = EncodingIndices.circularity_indices(
        #     osensors, raylen="raylen2D", suffix="_2D"
        # )
        # osensors = EncodingIndices.convexity_indices(
        #     osensors, raylen="raylen2D", suffix="_2D"
        # )
        osensors = EncodingIndices.linear_regression_indices(
            osensors, raylen="raylen2D", suffix="_2D"
        )
        # osensors = EncodingIndices.rectangularity_indices(
        #     osensors, raylen="raylen2D", suffix="_2D"
        # )
        osensors.drop(
            columns=["raylen2D", "HAUTEUR", "raylen25D", "h_over_w", "angles"],
            inplace=True,
        )
        return osensors

    @staticmethod
    def test2():
        from matplotlib import pyplot as plt
        from t4gpd.demos.NantesBDT import NantesBDT
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
        from t4gpd.morph.STBBox import STBBox

        buffDist, nRays = 200.0, 360
        sensors = GeoDataFrame(
            [
                {
                    "gid": 1,
                    "geometry": Point(355146.27863477013, 6689127.271813846),
                    "label": "Place de la Bourse",
                },
                {
                    "gid": 2,
                    "geometry": Point(354915.263, 6689943.223),
                    "label": "Place Viarme",
                },
                {
                    "gid": 3,
                    "geometry": Point(355148.996, 6689435.408),
                    "label": "Place du Bon Pasteur",
                },
                {
                    "gid": 4,
                    "geometry": Point(354893.574, 6689176.943),
                    "label": "Place Graslin",
                },
            ],
            crs="EPSG:2154",
        )
        bb = STBBox(sensors, buffDist=2 * buffDist).run()
        buildings = NantesBDT.buildings(roi=bb)

        h0 = 0
        osensors = SensorBasedEncodingLib.encode25D(
            sensors,
            buildings,
            elevationFieldname="HAUTEUR",
            h0=h0,
            rayLength=buffDist,
            nRays=nRays,
        )
        osensors = EncodingIndices.svf_pan_indices(osensors, angles="angles", copy=True)
        smaps = PANLib.skymap_with_pan(
            osensors, "angles", proj="Isoaire", size=100, epsilon=1e-1, copy=True
        )

        fig, ax = plt.subplots(figsize=(1.3 * 8.26, 8.26))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="grey")
        sensors.plot(ax=ax, color="red", marker="+", markersize=50)
        smaps.plot(ax=ax, color="green", edgecolor="green", alpha=0.85)
        smaps.apply(
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

        return osensors


# sensors = EncodingIndices.test()
# sensors = EncodingIndices.test2()
