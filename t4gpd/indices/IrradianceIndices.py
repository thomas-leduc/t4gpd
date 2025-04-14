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
from numpy import cos, deg2rad
from pandas import concat
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.DataFrameLib import DataFrameLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.SVFLib import SVFLib
from t4gpd.commons.energy.PvlibProxy import PvlibProxy


class IrradianceIndices(object):
    """
    classdocs
    """

    @staticmethod
    def __diffuse_wpm2(dhi, angles):
        _svf = SVFLib.svfAngles2018(deg2rad(angles))
        return _svf * dhi

    @staticmethod
    def __direct_wpm2(dni, azimuth, elevation, angles):
        _nslices = len(angles)
        _azimuth = AngleLib.northCW2eastCCW(azimuth, degree=True)
        _azimSliceId = AngleLib.fromEastCCWAzimuthToSliceId(_azimuth, _nslices)

        if angles[_azimSliceId] < elevation:
            # The position is in the sun on the given datetime
            return cos(deg2rad(90 - elevation)) * dni
        return 0

    @staticmethod
    def indices(
        gdf,
        dtFieldname,
        altitude=0,
        model="ineichen",
        skymaps=None,
        merge_by_index=False,
    ):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if DataFrameLib.hasAMultiIndex(gdf):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame without MultiIndex")

        clearsky = PvlibProxy.get_ghi_dni_dhi_positions(
            gdf, dtFieldname, altitude, model
        )

        _gdf = gdf.reset_index().loc[:, ["index", "timestamp"]]
        clearsky = _gdf.merge(clearsky, how="inner", on=dtFieldname)
        clearsky.set_index("index", inplace=True, verify_integrity=True)
        clearsky.index.name = None

        if not skymaps is None:
            if not isinstance(gdf, GeoDataFrame):
                raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
            if DataFrameLib.hasAMultiIndex(gdf):
                raise IllegalArgumentTypeException(
                    gdf, "GeoDataFrame without MultiIndex"
                )
            if not GeoDataFrameLib.shareTheSameCrs(gdf, skymaps):
                raise Exception(
                    "Illegal argument: gdf and skymaps are expected to share the same crs!"
                )
            if not gdf.index.equals(skymaps.index):
                raise Exception(
                    "Illegal argument: gdf and skymaps are expected to share the same index!"
                )
            clearsky = concat([clearsky, skymaps[["angles"]]], axis=1)
            clearsky["diffuse_wpm2"] = clearsky.apply(
                lambda row: IrradianceIndices.__diffuse_wpm2(row.dhi, row.angles),
                axis=1,
            )
            clearsky["direct_wpm2"] = clearsky.apply(
                lambda row: IrradianceIndices.__direct_wpm2(
                    row.dni, row.azimuth, row.apparent_elevation, row.angles
                ),
                axis=1,
            )
            clearsky.drop(columns=["angles"], inplace=True)

        if merge_by_index:
            clearsky = concat([gdf, clearsky], axis=1)
        return clearsky


"""
from t4gpd.demos.NantesBDT import NantesBDT
from t4gpd.morph.STBBox import STBBox
from t4gpd.picoclim.PicopattReader import PicopattReader
from t4gpd.skymap.STSkyMap25D import STSkyMap25D

ifile = "/home/tleduc/prj/anr_picopatt_2024-2027/docker/picopatt_nantes*centre*20250120*1427.csv"
measures = PicopattReader(ifile, lat="lat_ontrack", lon="lon_ontrack").run()
measures = measures.sample(5, random_state=0)  # DEBUG
df1 = IrradianceIndices.indices(measures, "timestamp", merge_by_index=True)

# =====
buffDist, nrays = 100, 96
buildings = NantesBDT.buildings(STBBox(measures, buffDist).run())
measures = measures.reset_index().rename(columns={"index": "gid"})
skymaps = STSkyMap25D(
    buildings,
    measures,
    nRays=nrays,
    rayLength=buffDist,
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
skymaps.set_index("gid", inplace=True, verify_integrity=True)
skymaps.index.name = None
measures = measures.set_index("gid", drop=True)
measures.index.name = None

df2 = IrradianceIndices.indices(
    measures, "timestamp", skymaps=skymaps, merge_by_index=True
)
"""
