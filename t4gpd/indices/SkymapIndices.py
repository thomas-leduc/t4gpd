"""
Created on 11 mar. 2025

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
from pandas import concat
from shapely import MultiLineString, get_coordinates
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.SVFLib import SVFLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.morph.CircularityLib import CircularityLib
from t4gpd.commons.morph.ConvexityLib import ConvexityLib
from t4gpd.commons.morph.LinearRegressionLib import LinearRegressionLib
from t4gpd.commons.morph.OrientedSVFLib import OrientedSVFLib
from t4gpd.commons.morph.RectangularityLib import RectangularityLib
from t4gpd.commons.morph.StarShapedLib import StarShapedLib


class SkymapIndices(object):
    """
    classdocs
    """

    @staticmethod
    def indices(skymaps, prefix=None, merge_by_index=False):
        if not isinstance(skymaps, GeoDataFrame):
            raise IllegalArgumentTypeException(skymaps, "GeoDataFrame")
        # if DataFrameLib.hasAMultiIndex(skymaps):
        #     raise IllegalArgumentTypeException(
        #         skymaps, "GeoDataFrame without MultiIndex"
        #     )
        skymaps.set_index("gid", inplace=True, verify_integrity=True)
        skymaps.index.name = None

        neg_skymaps = skymaps.copy(deep=True)
        neg_skymaps.geometry = neg_skymaps.geometry.apply(
            lambda geom: GeomLib.getUniqueHoleAsPolygon(geom)
        )

        rays_neg_skymaps = neg_skymaps.copy(deep=True)
        rays_neg_skymaps.geometry = rays_neg_skymaps.apply(
            lambda row: MultiLineString(
                [
                    [row.viewpoint.coords[0][:2], rc]
                    for rc in get_coordinates(row.geometry)
                ]
            ),
            axis=1,
        )

        df1 = StarShapedLib.indices(
            rays_neg_skymaps, with_geom=False, prefix=prefix, merge_by_index=False
        )

        df2 = CircularityLib.indices(
            neg_skymaps[["geometry"]],
            with_geom=False,
            prefix=prefix,
            merge_by_index=True,
        )
        df2 = ConvexityLib.indices(
            df2, with_geom=False, prefix=prefix, merge_by_index=True
        )
        df2 = LinearRegressionLib.indices(
            df2, with_geom=False, prefix=prefix, merge_by_index=True
        )
        df2 = RectangularityLib.indices(
            df2, with_geom=False, prefix=prefix, merge_by_index=True
        )
        df2.drop(columns=["geometry"], inplace=True)

        df3 = skymaps[["angles"]].copy(deep=True)
        df3["svf"] = df3.angles.apply(lambda a: SVFLib.svfAngles2018(deg2rad(a)))
        df3.drop(columns=["angles"], inplace=True)

        df4, df5, df6, df3456 = None, None, None, None
        nb_angles = skymaps.angles.apply(lambda v: len(v)).unique()
        if 1 == len(nb_angles):
            if 0 == nb_angles[0] % 8:
                df4 = OrientedSVFLib(skymaps, "angles", method="quadrants").indices2()
            if 0 == nb_angles[0] % 16:
                df5 = OrientedSVFLib(skymaps, "angles", method="octants").indices2()
            if 0 == nb_angles[0] % 24:
                df6 = OrientedSVFLib(skymaps, "angles", method="duodecants").indices2()
        df3456 = concat([df3, df4, df5, df6], axis=1)

        df123456 = concat([df1, df2, df3456], axis=1)

        if merge_by_index:
            df123456 = concat([skymaps, df123456], axis=1)
            df123456["geometry"] = df123456.viewpoint
            df123456.drop(columns=["viewpoint"], inplace=True)
            df123456.set_geometry("geometry", inplace=True)
        return df123456


"""
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.skymap.STSkyMap25D import STSkyMap25D

buildings = GeoDataFrameDemos.ensaNantesBuildings()
sensors = STGrid(buildings, dx=80, indoor=False, intoPoint=True).run()
sensors.set_index("gid", drop=False, inplace=True)
sensors.index.name = None

skymaps = STSkyMap25D(
    buildings,
    sensors,
    nRays=64,
    rayLength=100.0,
    elevationFieldname="HAUTEUR",
    h0=1.1,
    size=1.0,
    epsilon=1e-2,
    projectionName="Stereographic",
    withIndices=False,
    withAngles=True,
    encode=False,
    threshold=1e-6,
).run()

df = SkymapIndices.indices(skymaps, prefix="smap", merge_by_index=True)
"""
