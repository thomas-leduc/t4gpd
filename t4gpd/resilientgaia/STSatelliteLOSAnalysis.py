'''
Created on 19 nov. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
'''
from geopandas import GeoDataFrame
from pandas import concat
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class STSatelliteLOSAnalysis(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, lblsat):
        '''
        Constructor
        '''
        if not isinstance(lblsat, GeoDataFrame):
            raise IllegalArgumentTypeException(
                lblsat, "lblsat GeoDataFrame")

        self.lblsat = lblsat.query("label == 'LOS'", inplace=False)

    def __lin_reg(self, lblsat):
        from t4gpd.morph.geoProcesses.LinearRegressionIndices import LinearRegressionIndices

        op = LinearRegressionIndices(with_geom=True)
        linregsat = STGeoProcess(op, lblsat).run()
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

    def __mabeaxis(self, lblsat):
        from t4gpd.morph.geoProcesses.EllipticityAxisIndices import EllipticityAxisIndices

        op = EllipticityAxisIndices(
            threshold=None, debug=False, with_geom=True)
        mabeaxissat = STGeoProcess(op, lblsat).run()
        return mabeaxissat

    def __mabr(self, chull):
        from t4gpd.morph.geoProcesses.RectangularityIndices import RectangularityIndices

        op = RectangularityIndices(with_geom=True)
        mabrsat = STGeoProcess(op, chull).run()
        return mabrsat

    def run(self):
        # GROUP SATELLITES BY GID AND BY CONSTELLATION
        lblsat = self.lblsat.dissolve(
            by=["gid", "timeUTC", "constellation"],
            aggfunc={"satellite": list}, as_index=False)

        linreg = self.__lin_reg(lblsat)

        # LET'S CONVERT XPOINTS INTO THE CORRESPONDING CONVEX HULL
        chull = lblsat.assign(geometry=lambda geom: geom.convex_hull)
        mbc = self.__mbc(chull)
        mabr = self.__mabr(chull)
        mabe = self.__mabe(chull)
        mabeaxis = self.__mabeaxis(lblsat)

        # CONCAT ALL LAYERS USING INDEX
        lblsat = concat([
            lblsat,
            linreg[["slope", "intercept", "score", "mae", "mse"]],
            mabe[["flattening", "a_elli_def", "p_elli_def"]],
            mabeaxis[["ell_mae", "ell_mse"]],
            mabr[["stretching", "a_rect_def", "p_rect_def"]],
            mbc[["gravelius", "jaggedness", "miller", "morton", "a_circ_def"]]
        ], axis=1)

        return lblsat, chull, linreg, mabe, mabeaxis, mabr, mbc

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from datetime import timezone
        from geopandas import read_file
        from matplotlib.colors import ListedColormap
        from t4gpd.resilientgaia.STECEF2AERSatelliteReader import STECEF2AERSatelliteReader
        from t4gpd.resilientgaia.STSatelliteLabelling import STSatelliteLabelling
        from t4gpd.resilientgaia.STSatelliteOnSiteProjection import STSatelliteOnSiteProjection
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        # LOAD DATASETS
        rootdir = "/home/tleduc/prj/anr_resilientgaia_2024-2028/dev/data"
        ifile = f"{rootdir}/20240917_ReSilientGAIA.gpkg"
        buildings = read_file(ifile, layer="buildings")

        ifile = f"{rootdir}/20240917_parcours_timestamp.csv"
        aersat = STECEF2AERSatelliteReader(
            ifile, timestampFieldName="timeUTC").run()
        aersat["gid"] = range(len(aersat))
        aersat = aersat.set_index("timeUTC").tz_convert(
            timezone.utc).reset_index()

        gids = [959, 1615, 1718]
        # gids = [959]

        aersat = aersat.query(f"gid in {gids}", inplace=False)

        # PROCESS DATASETS
        projectionName, size = "Stereographic", 4.0
        skymaps = STSkyMap25D(buildings, aersat, nRays=64, rayLength=100.0,
                              elevationFieldname="HAUTEUR", h0=0.0, size=size, epsilon=1e-2,
                              projectionName=projectionName, withIndices=True, withAngles=False,
                              encode=True, threshold=1e-6).run()
        prjsat = STSatelliteOnSiteProjection(aersat, gid="gid", timestamp="timeUTC",
                                             proj=projectionName, size=size).run()
        prjsat2 = STSatelliteLabelling(skymaps, prjsat, "gid").run()

        lblsat, chull, linreg, mabe, mabeaxis, mabr, mbc = STSatelliteLOSAnalysis(
            prjsat2).run()

        # MAPPING
        my_cmap = ListedColormap(["green", "red"])

        for gid in gids:
            minx, miny, maxx, maxy = skymaps.query(
                f"gid == {gid}").buffer(1.0).total_bounds
            fig, axes = plt.subplots(
                figsize=(1.75 * 8.26, 1.35 * 8.26), nrows=2, ncols=3, squeeze=False)

            _skymaps = skymaps.query(f"gid == {gid}", inplace=False)
            svf = _skymaps.svf.squeeze()
            w_mean = _skymaps.w_mean.squeeze()
            h_over_w = _skymaps.h_over_w.squeeze()

            title = f"Position {gid}\n(svf={svf:.2f}, w_mean={w_mean:.1f} m, h/w={h_over_w:.3f})"
            fig.suptitle(title, fontsize=20)
            for nc, constellation in enumerate(["Galileo", "GLONASS", "GPS"]):
                querystring = f"(constellation == '{constellation}') and (gid == {gid})"
                _prjsat2 = prjsat2.query(querystring, inplace=False)
                _chull = chull.query(querystring, inplace=False)
                _mabe = mabe.query(querystring, inplace=False)
                _mabeaxis = mabeaxis.query(querystring, inplace=False)
                _mabr = mabr.query(querystring, inplace=False)
                _mbc = mbc.query(querystring, inplace=False)
                _linreg = linreg.query(querystring, inplace=False)

                # =====
                ax = axes[0, nc]
                ax.set_title(constellation, fontsize=16)
                skymaps.plot(ax=ax, color="lightgrey")
                aersat.plot(ax=ax, color="black", marker="P")
                _prjsat2.plot(ax=ax, column="label", cmap=my_cmap, marker="o")

                _chull.boundary.plot(ax=ax, color="brown",
                                     linestyle="dashed", linewidth=1)
                _mabe.boundary.plot(ax=ax, color="blue",
                                    linestyle="dashed", linewidth=1)
                _mabeaxis.plot(ax=ax, color="blue",
                               linestyle="dashed", linewidth=1)
                _mabeaxis.apply(lambda x: ax.annotate(
                    text=f"flattening={x.flattening:.2f}\nMAE={x.ell_mae:.2f}\nMSE={x.ell_mse:.2f}",
                    xy=[minx, miny], color="black", size=12, ha="left", va="bottom"), axis=1)
                ax.axis("off")
                ax.axis([minx, maxx, miny, maxy])

                # =====
                ax = axes[1, nc]

                skymaps.plot(ax=ax, color="lightgrey")
                aersat.plot(ax=ax, color="black", marker="P")
                _prjsat2.plot(ax=ax, column="label", cmap=my_cmap, marker="o")

                _mbc.boundary.plot(ax=ax, color="brown",
                                   linestyle="dashed", linewidth=1)
                _mabr.boundary.plot(ax=ax, color="blue",
                                    linestyle="dashed", linewidth=1)
                _linreg.plot(ax=ax, color="blue",
                             linestyle="dashed", linewidth=1)
                _linreg.apply(lambda x: ax.annotate(
                    text=f"score={x.score:.2f}\nMAE={x.mae:.2f}\nMSE={x.mse:.2f}",
                    xy=[minx, miny], color="black", size=12, ha="left", va="bottom"), axis=1)
                _mabr.apply(lambda x: ax.annotate(
                    text=f"stretching={x.stretching:.2f}\na_rect_def={x.a_rect_def:.2f}\np_rect_def={x.p_rect_def:.2f}",
                    xy=[maxx, miny], color="black", size=12, ha="right", va="bottom"), axis=1)
                _mbc.apply(lambda x: ax.annotate(
                    text=f"jaggedness={x.jaggedness:.2f}\nmiller={x.miller:.2f}\na_circ_def={x.a_circ_def:.2f}",
                    xy=[maxx, maxy], color="black", size=12, ha="right", va="top"), axis=1)
                ax.axis("off")
                ax.axis([minx, maxx, miny, maxy])

            plt.savefig(f"satmap_{gid}.pdf", bbox_inches="tight")
            # plt.show()
            plt.close(fig)

        return lblsat, chull, linreg, mabe, mabeaxis, mabr, mbc


# lblsat, chull, linreg, mabe, mabeaxis, mabr, mbc = STSatelliteLOSAnalysis.test()

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

lblsat, chull, linreg, mabe, mabeaxis, mabr, mbc = STSatelliteLOSAnalysis(prjsat2).run()
"""
