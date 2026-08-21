"""
Created on 6 March 2026

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

import json
import laspy
import pdal
from datetime import datetime
from geopandas import GeoDataFrame
from numpy import concatenate, unique
from os import access, R_OK
from os.path import isfile
from pandas import DataFrame, to_datetime
from shapely import union_all
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PDALLib(object):
    """
    classdocs

    PDAL - Point Data Abstraction Library
    """

    @staticmethod
    def asprs_colors(lang="en"):
        """
        ASPRS: American Society for Photogrammetry and Remote Sensing
        """
        if "fr" == lang:
            return {
                1: ("#AAAAAA", "Non classé"),
                2: ("#AA5500", "Sol"),
                3: ("#00AAAA", "Végétation faible"),
                4: ("#55FF55", "Végétation moyenne"),
                5: ("#00AA00", "Végétation forte"),
                6: ("#FF5555", "Bâtiment"),
                9: ("#0000FF", "Eau"),
                17: ("#5555FF", "Tablier du pont"),
                64: ("#91522D", "64"),
                66: ("#E15989", "66"),
                67: ("#BECF50", "67"),
            }
        return {
            1: ("#AAAAAA", "Unclassified"),
            2: ("#AA5500", "Ground"),
            3: ("#00AAAA", "Low Vegetation"),
            4: ("#55FF55", "Medium Vegetation"),
            5: ("#00AA00", "High Vegetation"),
            6: ("#FF5555", "Building"),
            9: ("#0000FF", "Water"),
            17: ("#5555FF", "Bridge"),
            64: ("#91522D", "64"),
            66: ("#E15989", "66"),
            67: ("#BECF50", "67"),
        }

    @staticmethod
    def get_copc_crs(ifile):
        """Reads the COPC CRS via laspy"""
        with laspy.open(ifile) as f:
            crs = f.header.parse_crs()
        return crs

    @staticmethod
    def __merge_pipeline_steps(ifiles, mask, cfilter):
        if isinstance(ifiles, str):
            ifiles = [ifiles]

        crs = PDALLib.get_copc_crs(ifiles[0])
        pipeline_steps = []
        for ifile in ifiles:
            if not (isfile(ifile) and access(ifile, R_OK)):
                raise IllegalArgumentTypeException(ifile, "readable filename")
            if not crs.equals(PDALLib.get_copc_crs(ifile)):
                raise Exception(
                    f"Illegal argument: {ifile} crs is expected to be '{crs}'!"
                )

            reader = (
                "readers.copc" if ifile.lower().endswith(".copc.laz") else "readers.las"
            )
            pipeline_steps.append({"type": reader, "filename": ifile})

        if mask is not None:
            if not isinstance(mask, GeoDataFrame):
                raise IllegalArgumentTypeException(mask, "GeoDataFrame")
            if not crs.equals(mask.crs):
                raise Exception(
                    f"Illegal argument: {mask} crs is expected to be '{crs}'!"
                )
            mask = union_all(mask.geometry)
            minx, miny, maxx, maxy = mask.bounds
            bounds = f"([{minx},{maxx}],[{miny},{maxy}])"

            pipeline_steps.extend(
                [
                    {"type": "filters.crop", "bounds": bounds},
                    {"type": "filters.crop", "polygon": mask.wkt},
                ]
            )

        if cfilter is not None:
            expression = " || ".join([f"Classification == {c}" for c in cfilter])
            # expression = f"Classification in {tuple(cfilter)}"
            pipeline_steps.append(
                {"type": "filters.expression", "expression": expression}
            )

        return pipeline_steps

    @staticmethod
    def merge(ifiles, ofile, mask=None, cfilter=None):
        pipeline_steps = PDALLib.__merge_pipeline_steps(ifiles, mask, cfilter)
        pipeline_steps.append(
            {"type": "writers.las", "filename": ofile, "compression": "laszip"}
        )
        pipeline = {"pipeline": pipeline_steps}
        pipeline = pdal.Pipeline(json.dumps(pipeline))
        pipeline.execute()
        return ofile

    @staticmethod
    def merge_and_count_classes(ifiles, mask=None, cfilter=None):
        pipeline_steps = PDALLib.__merge_pipeline_steps(ifiles, mask, cfilter)
        pipeline = {"pipeline": pipeline_steps}
        pipeline = pdal.Pipeline(json.dumps(pipeline))
        pipeline.execute()

        arrays = pipeline.arrays
        pts = concatenate(arrays)
        if "Classification" not in pts.dtype.names:
            raise ValueError("Le nuage n'a pas de champ 'Classification'")
        # Counting by classes
        classes, counts = unique(pts["Classification"], return_counts=True)
        df = DataFrame({"Classification": classes, "Count": counts})
        df["Ratio"] = df.Count / df.Count.sum()
        return df

    @staticmethod
    def merge_and_height_above_ground(ifiles, ofile, mask=None, cfilter=None):
        # Note: we keep all ground points for the HAG calculation.
        pipeline_steps = PDALLib.__merge_pipeline_steps(ifiles, mask, cfilter=None)
        pipeline_steps.append({"type": "filters.hag_nn"})

        if cfilter is not None:
            expression = " || ".join([f"Classification == {c}" for c in cfilter])
            # expression = f"Classification in {tuple(cfilter)}"
            pipeline_steps.append(
                {"type": "filters.expression", "expression": expression}
            )

        pipeline_steps.append(
            {
                "type": "writers.las",
                "filename": ofile,
                "compression": "laszip",
                "extra_dims": "HeightAboveGround=float32",
            },
        )
        pipeline = {"pipeline": pipeline_steps}
        pipeline = pdal.Pipeline(json.dumps(pipeline))
        pipeline.execute()
        return ofile

    @staticmethod
    def merge_to_dsm(ifiles, ofile, resolution, otype="idw", window=0, mask=None, cfilter=None):
        """
        resolution: DSM pixel size (0.5 m, 1 m, etc.)
        output_type: max, min, mean, idw (= Inverse Distance Weighting)
        radius: Search radius of points around the pixel (empirical rule = 1.5 x resolution)
        """
        pipeline_steps = PDALLib.__merge_pipeline_steps(ifiles, mask, cfilter)
        pipeline_steps.append(
            {
                "type": "writers.gdal",
                "filename": ofile,
                "output_type": otype,
                "resolution": resolution,
                "radius": 1.5 * resolution,
                "gdaldriver": "GTiff",
                "window_size": window,  # window=0: this avoids unnecessary buffering
                "data_type": "float32",
            }
        )
        pipeline = {"pipeline": pipeline_steps}
        pipeline = pdal.Pipeline(json.dumps(pipeline))
        pipeline.execute()
        return ofile

    @staticmethod
    def merge_to_frame(
        ifiles,
        columns=["X", "Y", "Z", "Classification", "GpsTime"],
        mask=None,
        cfilter=None,
    ):
        """
        columns=["X", "Y", "Z", "Classification", "GpsTime", "HeightAboveGround", "Intensity"]
        """
        # gps_epoch = datetime(1980, 1, 6)
        lidar_epoch = datetime(2011, 9, 14, 0, 0, 0)

        pipeline_steps = PDALLib.__merge_pipeline_steps(ifiles, mask, cfilter)
        pipeline = {"pipeline": pipeline_steps}
        pipeline = pdal.Pipeline(json.dumps(pipeline))
        pipeline.execute()

        arrays = pipeline.arrays
        pts = concatenate(arrays)
        for k in columns:
            if k not in pts.dtype.names:
                raise ValueError(f"The cloud does not have a '{k}' field.")

        # print(pts.dtype.names)
        df = DataFrame({column: pts[column] for column in columns})
        if "GpsTime" in df.columns:
            df.GpsTime = to_datetime(df.GpsTime, unit="s", origin=lidar_epoch)

        return df

    @staticmethod
    def test():
        from t4gpd.demos.GeoDataFrameDemosB import GeoDataFrameDemosB
        from t4gpd.commons.grid.IGNTilingLib import IGNTilingLib

        roi = GeoDataFrameDemosB.zonesEmblematiques()
        roi = roi.query("TOPONYME == 'Champ de Mars'").reset_index(drop=True)

        rootdir = "/home/tleduc/data/lidarhd/paris"
        grid = IGNTilingLib.grid(
            roi,
            prefix=f"{rootdir}/LHD_FXX_",
            suffix="_PTS_LAMB93_IGN69.copc.laz",
            step=1000,
        )
        ifiles = grid.label.values

        df = PDALLib.merge_and_count_classes(ifiles, roi)
        print(df)

        # ofile = "/home/tleduc/sDrive_cnrs/crenau/4_depots_projets/d_anr_mavel_2025-2026/dev/champ_de_mars.laz"
        # PDALLib.merge(ifiles, ofile, roi)

        columns = ["X", "Y", "Z", "Classification", "GpsTime", "Intensity"]
        df = PDALLib.merge_to_frame(ifiles, columns, mask=roi)
        return df

    @staticmethod
    def test2():
        from t4gpd.demos.GeoDataFrameDemosB import GeoDataFrameDemosB
        from t4gpd.commons.grid.IGNTilingLib import IGNTilingLib

        roi = GeoDataFrameDemosB.zonesEmblematiques()
        roi = roi.query("TOPONYME == 'Champ de Mars'").reset_index(drop=True)

        rootdir = "/home/tleduc/data/lidarhd/paris"
        grid = IGNTilingLib.grid(
            roi,
            prefix=f"{rootdir}/LHD_FXX_",
            suffix="_PTS_LAMB93_IGN69.copc.laz",
            step=1000,
        )
        ifiles = grid.label.values

        ofile = "/home/tleduc/sDrive_cnrs/crenau/4_depots_projets/d_anr_mavel_2025-2026/dev/champ_de_mars.laz"
        PDALLib.merge_and_height_above_ground(
            ifiles, ofile, roi, cfilter=[2, 3, 4, 5, 6]
        )

        columns = [
            "X",
            "Y",
            "Z",
            "Classification",
            "GpsTime",
            "HeightAboveGround",
            "Intensity",
        ]
        df = PDALLib.merge_to_frame(ofile, columns, mask=None)
        return df

    @staticmethod
    def test3():
        from t4gpd.demos.GeoDataFrameDemosB import GeoDataFrameDemosB
        from t4gpd.commons.grid.IGNTilingLib import IGNTilingLib

        roi = GeoDataFrameDemosB.zonesEmblematiques()
        roi = roi.query("TOPONYME == 'Champ de Mars'").reset_index(drop=True)

        rootdir = "/home/tleduc/data/lidarhd/paris"
        grid = IGNTilingLib.grid(
            roi,
            prefix=f"{rootdir}/LHD_FXX_",
            suffix="_PTS_LAMB93_IGN69.copc.laz",
            step=1000,
        )
        ifiles = grid.label.values

        ofile = "/home/tleduc/sDrive_cnrs/crenau/4_depots_projets/d_anr_mavel_2025-2026/dev/champ_de_mars.tif"
        PDALLib.merge_to_dsm(
            ifiles, ofile, resolution=1, mask=roi, cfilter=[2, 3, 4, 5]
        )


# df = PDALLib.test()
# df = PDALLib.test2()
# PDALLib.test3()
