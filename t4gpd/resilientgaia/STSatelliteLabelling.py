"""
Created on 21 oct. 2024

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
from numpy import isnan
from pandas import DataFrame, concat
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class STSatelliteLabelling(GeoProcess):
    """
    classdocs
    """

    def __init__(self, skymaps, prjsat, gid="gid"):
        """
        Constructor
        """
        if not isinstance(skymaps, GeoDataFrame):
            raise IllegalArgumentTypeException(skymaps, "skymaps GeoDataFrame")
        if not gid in skymaps:
            raise Exception(f"{gid} is not a relevant field name for skymaps!")
        if not isinstance(prjsat, GeoDataFrame):
            raise IllegalArgumentTypeException(prjsat, "prjsat GeoDataFrame")
        if not "gid" in prjsat:
            raise Exception(f"{gid} is not a relevant field name for prjsat!")

        if not GeoDataFrameLib.shareTheSameCrs(skymaps, prjsat):
            raise Exception(
                "Illegal argument: skymaps and prjsat are expected to share the same crs!"
            )

        self.skymaps = skymaps
        self.prjsat = prjsat
        self.gid = gid
        self.gids = self.skymaps[self.gid]

    def __merge(self):
        prjsat = []
        for gid in self.gids:
            _skymap = self.skymaps.loc[
                self.skymaps[self.skymaps[self.gid] == gid].index, ["geometry"]
            ]
            _prjsat = self.prjsat.loc[self.prjsat[self.prjsat[self.gid] == gid].index]
            _prjsat = _prjsat.sjoin(_skymap, how="left")
            prjsat.append(_prjsat)

        prjsat = concat(prjsat)
        prjsat["label"] = prjsat.index_right.apply(
            lambda v: "LOS" if isnan(v) else "NLOS"
        )
        prjsat.drop(columns=["index_right"], inplace=True)
        return prjsat

    @staticmethod
    def transpose(
        df,
        gid="gid",
        satellite="satellite",
        label="label",
        others=["timeUTC", "viewpoint"],
    ):
        """
        0: NO SIGNAL
        1: NLOS
        2: LOS
        """
        satnames = SatelliteLib.get_satellite_names(2)
        columns = [f"{s}_BDT" for s in satnames]

        others = {other: "first" for other in others}
        others.update({satellite: list, label: list})

        result = df.groupby(by=gid).agg(others).reset_index()
        empty = DataFrame([], columns=columns)
        result = concat([result, empty], axis=1)

        def foo(satname, satellites, labels):
            if not satname in satellites:
                return 0
            index = satellites.index(satname)
            if "NLOS" == labels[index]:
                return 1
            if "LOS" == labels[index]:
                return 2
            raise Exception("Unreachable instruction!")

        for satname, column in zip(satnames, columns):
            result[column] = result.apply(
                lambda row: foo(satname, row[satellite], row[label]),
                axis=1,
            )
        return result

    def run(self):
        prjsat = self.__merge()
        return prjsat

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from datetime import timezone
        from geopandas import read_file
        from matplotlib.colors import ListedColormap
        from t4gpd.resilientgaia.STECEF2AERSatelliteReader import (
            STECEF2AERSatelliteReader,
        )
        from t4gpd.resilientgaia.STSatelliteOnSiteProjection import (
            STSatelliteOnSiteProjection,
        )
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        # LOAD DATASETS
        rootdir = "/home/tleduc/prj/anr_resilientgaia_2024-2028/dev/data"
        ifile = f"{rootdir}/20240917_ReSilientGAIA.gpkg"
        buildings = read_file(ifile, layer="buildings")

        ifile = f"{rootdir}/20240917_parcours_timestamp.csv"
        aersat = STECEF2AERSatelliteReader(ifile, timestampFieldName="timeUTC").run()
        aersat["gid"] = range(len(aersat))
        aersat = aersat.set_index("timeUTC").tz_convert(timezone.utc).reset_index()

        # gids = [959, 1615, 1718]
        gids = [959]
        aersat = aersat.query(f"gid in {gids}", inplace=False)

        # PROCESS DATASETS
        projectionName, size = "Stereographic", 4.0
        skymaps = STSkyMap25D(
            buildings,
            aersat,
            nRays=64,
            rayLength=100.0,
            elevationFieldname="HAUTEUR",
            h0=0.0,
            size=size,
            epsilon=1e-2,
            projectionName=projectionName,
            withIndices=True,
            withAngles=False,
            encode=True,
            threshold=1e-6,
        ).run()
        prjsat = STSatelliteOnSiteProjection(
            aersat, gid="gid", timestamp="timeUTC", proj=projectionName, size=size
        ).run()

        prjsat2 = STSatelliteLabelling(skymaps, prjsat, "gid").run()

        # MAPPING
        my_cmap = ListedColormap(["green", "red"])

        for gid in gids:
            _prjsat2 = prjsat2.query(f"gid == {gid}", inplace=False)
            ht = (
                _prjsat2.groupby(by="label")
                .agg({"constellation": "count"})
                .to_dict()["constellation"]
            )

            minx, miny, maxx, maxy = (
                skymaps.query(f"gid == {gid}").buffer(1.0).total_bounds
            )

            fig, ax = plt.subplots(figsize=(1.15 * 8.26, 1.15 * 8.26))
            ax.set_title(
                f"Position {gid} ({ht['LOS']} LOS + {ht['NLOS']} NLOS)", fontsize=20
            )
            skymaps.plot(ax=ax, color="lightgrey")
            aersat.plot(ax=ax, color="black", marker="P")
            _prjsat2.plot(ax=ax, column="label", cmap=my_cmap, marker="o")

            ax.axis("off")
            ax.axis([minx, maxx, miny, maxy])
            # plt.savefig(f"satmap_{gid}.pdf", bbox_inches="tight")
            fig.tight_layout()
            plt.show()
            plt.close(fig)

        return prjsat2


# prjsat2 = STSatelliteLabelling.test()

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
"""

"""
from geopandas import read_file
from t4gpd.resilientgaia.STSatelliteOnSiteProjection import STSatelliteOnSiteProjection

def __los_nlos(sat, skymaps, projectionName, size=1.0):
    prjsat = STSatelliteOnSiteProjection(
        sat, gid="gid", timestamp="timeUTC", proj=projectionName, size=size
    ).run()
    lblsat = STSatelliteLabelling(skymaps, prjsat, "gid").run()
    return lblsat

DATASET = "/home/tleduc/prj/anr_resilientgaia_2024-2028/dev/data/20241219_datasets_full/dataset.gpkg"
terrain, mobility = "vincent_gache_segment_1", "car"
projectionName = "Stereographic"

uliss = read_file(DATASET, layer=f"{terrain}_{mobility}_uliss")
skymaps = read_file(DATASET, layer=f"{terrain}_{mobility}_skymaps")
lblsat = __los_nlos(uliss, skymaps, projectionName)
lblsat = lblsat.assign(segment=terrain, mobility_type=mobility)

lblsat2 = STSatelliteLabelling.transpose(
    lblsat,
    gid="gid",
    satellite="satellite",
    label="label",
    others=["timeUTC", "viewpoint", "segment", "mobility_type"],
    )
"""
