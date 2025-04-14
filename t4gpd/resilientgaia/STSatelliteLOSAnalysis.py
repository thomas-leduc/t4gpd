"""
Created on 19 nov. 2024

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
from pandas import DataFrame, concat
from shapely.wkt import loads
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class STSatelliteLOSAnalysis(GeoProcess):
    """
    classdocs
    """

    def __init__(self, lblsat, linreg=True, mbc=True, mabr=True, mabe=True):
        """
        Constructor
        """
        if not isinstance(lblsat, GeoDataFrame):
            raise IllegalArgumentTypeException(lblsat, "lblsat GeoDataFrame")

        self.lblsat = lblsat
        self.lossat = lblsat.query("label == 'LOS'", inplace=False)
        self.nlossat = lblsat.query("label == 'NLOS'", inplace=False)
        self.linreg = linreg
        self.mbc = mbc
        self.mabr = mabr
        self.mabe = mabe

    @staticmethod
    def groupby(lblsat):
        df = lblsat.groupby(by=["gid", "constellation", "label"], as_index=False).agg(
            {"satellite": list}
        )
        # df = df.to_dict("records")
        ht = {}
        for _, row in df.iterrows():
            gid = row.gid
            if not gid in ht:
                ht[gid] = {
                    "gid": gid,
                    "LOS_GPS": 0,
                    "NLOS_GPS": 0,
                    "LOS_GLONASS": 0,
                    "NLOS_GLONASS": 0,
                    "LOS_Galileo": 0,
                    "NLOS_Galileo": 0,
                }
            ht[gid][f"{row.label}_{row.constellation}"] = len(row.satellite)
        df = DataFrame(ht.values())
        df["LOS"] = df["LOS_GPS"] + df["LOS_GLONASS"] + df["LOS_Galileo"]
        df["NLOS"] = df["NLOS_GPS"] + df["NLOS_GLONASS"] + df["NLOS_Galileo"]
        df["GPS"] = df["LOS_GPS"] + df["NLOS_GPS"]
        df["GLONASS"] = df["LOS_GLONASS"] + df["NLOS_GLONASS"]
        df["Galileo"] = df["LOS_Galileo"] + df["NLOS_Galileo"]
        return df

    def __lin_reg(self, lossat):
        from t4gpd.morph.geoProcesses.LinearRegressionIndices import (
            LinearRegressionIndices,
        )

        op = LinearRegressionIndices(with_geom=True)
        linregsat = STGeoProcess(op, lossat).run()
        return linregsat

    def __mbc(self, chull):
        from t4gpd.morph.geoProcesses.CircularityIndices import CircularityIndices

        op = CircularityIndices(with_geom=True)
        mbcsat = STGeoProcess(op, chull).run()
        return mbcsat

    def __mabe(self, chull):
        from t4gpd.morph.geoProcesses.EllipticityIndices import EllipticityIndices

        op = EllipticityIndices(threshold=None, debug=False, with_geom=True)
        mabesat = STGeoProcess(op, chull).run()
        return mabesat

    def __mabeaxis(self, lossat):
        from t4gpd.morph.geoProcesses.EllipticityAxisIndices import (
            EllipticityAxisIndices,
        )

        op = EllipticityAxisIndices(threshold=None, debug=False, with_geom=True)
        mabeaxissat = STGeoProcess(op, lossat).run()
        return mabeaxissat

    def __mabr(self, chull):
        from t4gpd.morph.geoProcesses.RectangularityIndices import RectangularityIndices

        op = RectangularityIndices(with_geom=True)
        mabrsat = STGeoProcess(op, chull).run()
        return mabrsat

    def __multi_indices(self, allsat, lossat, nlossat):
        allsat["drift"] = allsat.apply(
            lambda row: loads(row.viewpoint).distance(row.geometry.centroid), axis=1
        )
        lossat["drift_LOS"] = lossat.apply(
            lambda row: loads(row.viewpoint).distance(row.geometry.centroid), axis=1
        )
        nlossat["drift_NLOS"] = nlossat.apply(
            lambda row: loads(row.viewpoint).distance(row.geometry.centroid), axis=1
        )
        dfs = [allsat, lossat["drift_LOS"], nlossat["drift_NLOS"]]

        # LET'S CONVERT XPOINTS INTO THE CORRESPONDING CONVEX HULL
        chull = lossat.assign(geometry=lambda geom: geom.convex_hull)

        if self.linreg:
            linreg = self.__lin_reg(lossat)
            dfs.append(linreg[["slope", "intercept", "score", "mae", "mse"]])

        if self.mbc:
            mbc = self.__mbc(chull)
            dfs.append(
                mbc[["gravelius", "jaggedness", "miller", "morton", "a_circ_def"]]
            )

        if self.mabr:
            mabr = self.__mabr(chull)
            dfs.append(mabr[["stretching", "a_rect_def", "p_rect_def"]])

        if self.mabe:
            mabe = self.__mabe(chull)
            dfs.append(mabe[["flattening", "a_elli_def", "p_elli_def"]])
            mabeaxis = self.__mabeaxis(lossat)
            dfs.append(mabeaxis[["ell_mae", "ell_mse"]])

        # CONCAT ALL LAYERS USING INDEX
        lossat = concat(dfs, axis=1)
        lossat.drop(columns=["geometry", "viewpoint", "satellite"], inplace=True)

        return lossat

    def run(self):
        # GROUP SATELLITES BY GID
        allsat = self.lblsat.dissolve(
            by=["gid", "viewpoint"], aggfunc={"satellite": list}, as_index=False
        )
        allLOSsat = self.lossat.dissolve(
            by=["gid", "viewpoint"], aggfunc={"satellite": list}, as_index=False
        )
        allNLOSsat = self.nlossat.dissolve(
            by=["gid", "viewpoint"], aggfunc={"satellite": list}, as_index=False
        )
        allLOSsat = self.__multi_indices(allsat, allLOSsat, allNLOSsat)

        # GROUP SATELLITES BY GID AND BY CONSTELLATION
        cstALLsat = self.lblsat.dissolve(
            by=["gid", "viewpoint", "constellation"],
            aggfunc={"satellite": list},
            as_index=False,
        )
        cstLOSsat = self.lossat.dissolve(
            by=["gid", "viewpoint", "constellation"],
            aggfunc={"satellite": list},
            as_index=False,
        )
        cstNLOSsat = self.nlossat.dissolve(
            by=["gid", "viewpoint", "constellation"],
            aggfunc={"satellite": list},
            as_index=False,
        )
        cstLOSsat = self.__multi_indices(cstALLsat, cstLOSsat, cstNLOSsat)

        # MERGE
        df1 = cstLOSsat.query("constellation == 'GPS'").drop(columns=["constellation"])
        df2 = cstLOSsat.query("constellation == 'GLONASS'").drop(
            columns=["constellation"]
        )
        df3 = cstLOSsat.query("constellation == 'Galileo'").drop(
            columns=["constellation"]
        )

        lblpos = STSatelliteLOSAnalysis.groupby(self.lblsat)
        result = (
            lblpos.merge(allLOSsat, on="gid", how="left")
            .merge(df1, on="gid", how="left", suffixes=("", "_GPS"))
            .merge(df2, on="gid", how="left", suffixes=("", "_GLONASS"))
            .merge(df3, on="gid", how="left", suffixes=("", "_Galileo"))
        )
        return result


"""
import matplotlib.pyplot as plt
from datetime import timezone
from geopandas import read_file
from matplotlib.colors import ListedColormap
from t4gpd.resilientgaia.STECEF2AERSatelliteReader import STECEF2AERSatelliteReader
from t4gpd.resilientgaia.STSatelliteLabelling import STSatelliteLabelling
from t4gpd.resilientgaia.STSatelliteOnSiteProjection import STSatelliteOnSiteProjection
from t4gpd.skymap.STSkyMap25D import STSkyMap25D

# LOAD DATASETS
ifile = "/home/tleduc/prj/anr_resilientgaia_2024-2028/dev/data/20240917_ReSilientGAIA.gpkg"
buildings = read_file(ifile, layer="buildings")

ifile = "/home/tleduc/prj/anr_resilientgaia_2024-2028/dev/data/20240917_parcours_timestamp.csv"
aersat = STECEF2AERSatelliteReader(ifile, timestampFieldName="timeUTC").run()
aersat["gid"] = range(len(aersat))
aersat = aersat.set_index("timeUTC").tz_convert(timezone.utc).reset_index()
gids = [959, 1615, 1718]
# gids = [959]
aersat = aersat.loc[aersat[aersat.gid.isin(gids)].index]

# PROCESS DATASETS
projectionName, size = "Stereographic", 4.0
skymaps = STSkyMap25D(buildings, aersat, nRays=64, rayLength=100.0,
                      elevationFieldname="HAUTEUR", h0=0.0, size=size, epsilon=1e-2,
                      projectionName=projectionName, withIndices=True, withAngles=False,
                      encode=True, threshold=1e-6).run()
prjsat = STSatelliteOnSiteProjection(aersat, gid="gid", timestamp="timeUTC",
                                     proj=projectionName, size=size).run()
prjsat2 = STSatelliteLabelling(skymaps, prjsat, "gid").run()

df = STSatelliteLOSAnalysis(prjsat2).run()
"""

"""
from geopandas import read_file

ifile = "/home/tleduc/prj/anr_resilientgaia_2024-2028/dev/data/20241219_datasets/dataset.gpkg"
lblsat = read_file(ifile, layer=f"berlin_segment_1_lblsat")
df1 = STSatelliteLOSAnalysis(lblsat).run()
df2 = STSatelliteLOSAnalysis(lblsat, linreg=False, mbc=False, mabr=False, mabe=False).run()
"""
