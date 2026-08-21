"""
Created on 13 Feb. 2026

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
from shapely import points
from tempfile import TemporaryDirectory
from t4gpd.commons import IllegalArgumentTypeException
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.PDALLib import PDALLib


class LASReader(GeoProcess):
    """
    classdocs
    """

    def __init__(
        self,
        ifiles,
        bbox=None,
        cfilter=None,
        columns=[
            "X",
            "Y",
            "Z",
            "Classification",
            "GpsTime",
            "HeightAboveGround",
            "Intensity",
        ],
    ):
        """
        Constructor
        """
        if not isinstance(bbox, GeoDataFrame):
            raise IllegalArgumentTypeException(bbox, "GeoDataFrame")
        self.ifiles = [ifiles] if isinstance(ifiles, str) else ifiles
        self.bbox = bbox
        self.cfilter = cfilter
        self.crs = PDALLib.get_copc_crs(self.ifiles[0])
        self.columns = columns

    def run(self):
        with TemporaryDirectory() as tmpdir:
            ofile = f"{tmpdir}/123.laz"
            PDALLib.merge_and_height_above_ground(
                self.ifiles, ofile, mask=self.bbox, cfilter=self.cfilter
            )
            df = PDALLib.merge_to_frame(ofile, columns=self.columns, mask=self.bbox)
            df["geometry"] = points(list(zip(df.X, df.Y, df.Z)))
            gdf = GeoDataFrame(df, crs=self.crs)
            return gdf

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
        gdf = LASReader(ifiles, roi).run()
        return gdf


# gdf = LASReader.test()
