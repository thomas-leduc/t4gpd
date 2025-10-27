"""
Created on 25 sep. 2023

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

import matplotlib.pyplot as plt
import unittest

from geopandas import GeoDataFrame
from numpy import ceil
from shapely import Point, Polygon
from shapely.affinity import translate
from shapely.geometry import CAP_STYLE
from shapely.wkt import loads
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.skymap.STSkyMap25D import STSkyMap25D


class STSkyMap25DTest(unittest.TestCase):
    def setUp(self):
        h = 10.0
        self.masks1 = GeoDataFrame(
            [
                {
                    "gid": 1,
                    "geometry": Polygon(
                        [(0, 0), (0, 10), (10, 10), (10, 9), (1, 9), (1, 0), (0, 0)]
                    ),
                    "HAUTEUR": h,
                }
            ]
        )
        self.masks2 = self.masks1.copy(deep=True)
        self.masks2.geometry = self.masks2.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(geom, z0=h)
        )
        self.masks3 = GeoDataFrame(
            [
                {
                    "gid": 1,
                    "geometry": loads(
                        "POLYGON ((353471.90000000002328306 6684814 33.5, 353463.5 6684812.09999999962747097 33.5, 353461.79999999998835847 6684819.79999999981373549 33.5, 353462.70000000001164153 6684820.20000000018626451 33.5, 353461.5 6684825.79999999981373549 33.5, 353468.59999999997671694 6684827.5 33.5, 353471.90000000002328306 6684814 33.5))"
                    ),
                    "HAUTEUR": 4.0,
                }
            ]
        )

        epsilon = 1e-6
        self.sensors1 = GeoDataFrame(
            [
                {
                    "gid": 1,
                    "row": 0,
                    "column": 0,
                    "geometry": Point([1 + epsilon, 9 - epsilon]),
                },
                {"gid": 2, "row": 0, "column": 1, "geometry": Point([5, 10 + epsilon])},
                {"gid": 3, "row": 0, "column": 2, "geometry": Point([10, 0])},
            ]
        )
        self.sensors2 = self.sensors1.copy(deep=True)
        self.sensors2.geometry = self.sensors2.geometry.apply(
            lambda geom: geom.buffer(0.5, cap_style=CAP_STYLE.square)
        )
        self.sensors3 = GeoDataFrame(
            [
                {
                    "gid": 1,
                    "row": 0,
                    "column": 0,
                    "geometry": loads("POINT (353469.15000000008149073 6684825.25)"),
                },
            ]
        )

    def tearDown(self):
        self.masks1 = None
        self.masks2 = None
        self.masks3 = None
        self.sensors1 = None
        self.sensors2 = None
        self.sensors3 = None

    def __plot(self, masks, sensors, result, indic=None, bbox=[-2, 12, -2, 12]):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        masks.plot(ax=ax, color="grey")
        sensors.plot(ax=ax, color="black", marker="+")
        result.plot(ax=ax, color="blue", alpha=0.35)
        if indic is not None:
            result.apply(
                lambda x: ax.annotate(
                    text=f"{x[indic]:.2f}",
                    xy=x.geometry.centroid.coords[0],
                    color="red",
                    size=12,
                    ha="center",
                ),
                axis=1,
            )
        else:
            sensors.apply(
                lambda x: ax.annotate(
                    text=x.gid,
                    xy=x.geometry.centroid.coords[0],
                    color="red",
                    size=12,
                    ha="center",
                ),
                axis=1,
            )
        ax.axis(bbox)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testPlotProjections(self):
        dw = 10
        buildings = GeoDataFrameDemos.regularGridOfPlots(2, 2, dw=dw)
        buildings["HAUTEUR"] = 10
        viewpoints = GeoDataFrame(
            [{"gid": 1, "geometry": Point(0, 0)}], crs=buildings.crs
        )

        PRJ = ["Orthogonal", "Isoaire", "Stereographic", "Polar"]
        ncols = 2
        nrows = int(ceil(len(PRJ) / ncols))
        fig, axes = plt.subplots(
            nrows=nrows, ncols=ncols, figsize=(24, 8), squeeze=False
        )
        for i, prj in enumerate(PRJ):
            smaps = STSkyMap25D(
                buildings,
                viewpoints,
                nRays=360,
                rayLength=100.0,
                elevationFieldname="HAUTEUR",
                h0=0.0,
                size=dw,
                epsilon=1e-1,
                projectionName=prj,
                withIndices=False,
                withAngles=False,
            ).run()

            ax = axes.flat[i]
            ax.set_title(
                f"{prj} (h=10m), area={smaps.area.sum():.1f} m$^2$", fontsize=18
            )
            viewpoints.plot(ax=ax, marker="P")
            buildings.plot(ax=ax, edgecolor="black", alpha=0.5)
            smaps.plot(ax=ax, color="black")
            ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        for sensors in [self.sensors1, self.sensors2]:
            for masks in [self.masks1, self.masks2]:
                result = STSkyMap25D(
                    masks,
                    sensors,
                    nRays=64,
                    rayLength=100.0,
                    elevationFieldname="HAUTEUR",
                    h0=0.0,
                    size=2.0,
                    epsilon=1e-2,
                    projectionName="Stereographic",
                    withIndices=False,
                    withAngles=False,
                ).run()
                self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
                self.assertEqual(len(sensors), len(result), "Count rows")
                self.assertEqual(
                    len(sensors.columns) + 1, len(result.columns), "Count columns"
                )
                # self.__plot(masks, sensors, result)

    def testRun2(self):
        for sensors in [self.sensors1, self.sensors2]:
            for masks in [self.masks1, self.masks2]:
                result = STSkyMap25D(
                    masks,
                    sensors,
                    nRays=64,
                    rayLength=100.0,
                    elevationFieldname="HAUTEUR",
                    h0=0.0,
                    size=2.0,
                    epsilon=1e-2,
                    projectionName="Stereographic",
                    withIndices=True,
                    withAngles=False,
                ).run()
                self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
                self.assertEqual(len(sensors), len(result), "Count rows")
                self.assertEqual(
                    len(sensors.columns) + 10, len(result.columns), "Count columns"
                )
                # print(result[['gid', 'w_mean', 'w_std', 'h_mean', 'h_over_w', 'svf']])
                self.assertTrue(
                    all(result.apply(lambda row: row.w_mean > row.gid * 25, axis=1)),
                    "Check w_mean values",
                )
                self.assertTrue(
                    all(result.apply(lambda row: row.gid * 0.25 < row.svf < 1, axis=1)),
                    "Check svf values",
                )

                epsilon = 1e-3
                self.assertAlmostEqual(
                    result.at[0, "svf"], 0.266, None, "Check svf value (0)", epsilon
                )
                self.assertAlmostEqual(
                    result.at[1, "svf"], 0.516, None, "Check svf value (1)", epsilon
                )
                self.assertAlmostEqual(
                    result.at[2, "svf"], 0.823, None, "Check svf value (2)", epsilon
                )

                # self.__plot(masks, sensors, result, "svf")

    def testRun3(self):
        for sensors in [self.sensors1, self.sensors2]:
            for masks in [self.masks1, self.masks2]:
                result = STSkyMap25D(
                    masks,
                    sensors,
                    nRays=64,
                    rayLength=100.0,
                    elevationFieldname="HAUTEUR",
                    h0=0.0,
                    size=2.0,
                    epsilon=1e-2,
                    projectionName="Stereographic",
                    withIndices=True,
                    withAngles=True,
                ).run()
                self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
                self.assertEqual(len(sensors), len(result), "Count rows")
                self.assertEqual(
                    len(sensors.columns) + 11, len(result.columns), "Count columns"
                )
                self.assertTrue(
                    all(result.apply(lambda row: row.w_mean > row.gid * 25, axis=1)),
                    "Check w_mean values",
                )
                self.assertTrue(
                    all(result.apply(lambda row: row.gid * 0.25 < row.svf < 1, axis=1)),
                    "Check svf values",
                )

                epsilon = 1e-3
                self.assertAlmostEqual(
                    result.at[0, "svf"], 0.266, None, "Check svf value (0)", epsilon
                )
                self.assertAlmostEqual(
                    result.at[1, "svf"], 0.516, None, "Check svf value (1)", epsilon
                )
                self.assertAlmostEqual(
                    result.at[2, "svf"], 0.823, None, "Check svf value (2)", epsilon
                )

                # self.__plot(masks, sensors, result, "svf")

    def testRun4(self):
        masks1 = self.masks1.copy(deep=True)
        masks1.geometry = masks1.geometry.apply(lambda geom: translate(geom, xoff=1000))

        masks2 = self.masks2.copy(deep=True)
        masks2.geometry = masks2.geometry.apply(lambda geom: translate(geom, xoff=1000))

        for sensors in [self.sensors1, self.sensors2]:
            for masks in [masks1, masks2]:
                result = STSkyMap25D(
                    masks,
                    sensors,
                    nRays=64,
                    rayLength=100.0,
                    elevationFieldname="HAUTEUR",
                    h0=0.0,
                    size=2.0,
                    epsilon=1e-2,
                    projectionName="Stereographic",
                    withIndices=True,
                    withAngles=True,
                ).run()

                self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
                self.assertEqual(len(sensors), len(result), "Count rows")
                self.assertEqual(
                    len(sensors.columns) + 11, len(result.columns), "Count columns"
                )
                self.assertTrue(all(result.w_mean == 100.0), "Check w_mean values")
                self.assertTrue(all(result.h_mean == 0.0), "Check h_mean values")
                self.assertTrue(all(result.h_over_w == 0.0), "Check h_over_w values")
                self.assertTrue(all(result.svf == 1.0), "Check svf values")

                # self.__plot(masks, sensors, result, "svf")

    def testRun5(self):
        masks, sensors = self.masks3, self.sensors3
        result = STSkyMap25D(
            masks,
            sensors,
            nRays=64,
            rayLength=100.0,
            elevationFieldname="HAUTEUR",
            h0=0.0,
            size=2.0,
            epsilon=1e-2,
            projectionName="Stereographic",
            withIndices=False,
            withAngles=False,
        ).run()
        self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
        self.assertEqual(len(sensors), len(result), "Count rows")
        self.assertEqual(len(sensors.columns) + 1, len(result.columns), "Count columns")
        # self.__plot(masks, sensors, result, bbox=None)

    def testRun6(self):
        from io import StringIO
        from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
        from t4gpd.demos.NantesBDT import NantesBDT

        _sio = StringIO(
            """gid;geometry
150755;"POLYGON ((355050.15 6689030.25, 355050.15 6689032.25, 355048.15 6689032.25, 355048.15 6689030.25, 355050.15 6689030.25))"
"""
        )
        sensors = GeoDataFrameLib.read_csv(_sio)
        masks = NantesBDT.buildings()
        masks = masks.loc[
            masks[
                masks.ID.isin(["BATIMENT0000000302927659", "BATIMENT0000000302930463"])
            ].index
        ]
        result = STSkyMap25D(
            masks,
            sensors,
            nRays=64,
            rayLength=100,
            elevationFieldname="HAUTEUR",
            h0=0.0,
            size=1.0,
            withIndices=True,
            withAngles=True,
            encode=True,
            threshold=1e-7,
        ).run()
        self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
        self.assertEqual(len(sensors), len(result), "Count rows")
        self.assertEqual(len(sensors.columns) + 11, len(result.columns), "Count columns")
        # self.__plot(masks, sensors, result, bbox=None)

    def testRun7(self):
        from io import StringIO
        from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
        from t4gpd.demos.NantesBDT import NantesBDT

        _sio = StringIO(
            """gid;geometry
86751;"POLYGON ((355042.15 6688780.25, 355042.15 6688782.25, 355040.15 6688782.25, 355040.15 6688780.25, 355042.15 6688780.25))"
"""
        )
        sensors = GeoDataFrameLib.read_csv(_sio)
        masks = NantesBDT.buildings()
        masks = masks.loc[masks[masks.ID == "BATIMENT0000000302923050"].index]
        result = STSkyMap25D(
            masks,
            sensors,
            nRays=64,
            rayLength=100,
            elevationFieldname="HAUTEUR",
            h0=0.0,
            size=1.0,
            withIndices=True,
            withAngles=True,
            encode=True,
            threshold=1e-7,
        ).run()
        self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
        self.assertEqual(len(sensors), len(result), "Count rows")
        self.assertEqual(len(sensors.columns) + 11, len(result.columns), "Count columns")
        # self.__plot(masks, sensors, result, bbox=None)

    def testRun8(self):
        from io import StringIO
        from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib

        _sio = StringIO(
            """gid,row,column,dist_to_ctr,dalle_id,geometry
0,0,0,44.89237128934325,488,"POLYGON ((354596.15 6688442.25, 354596.15 6688444.25, 354594.15 6688444.25, 354594.15 6688442.25, 354596.15 6688442.25))"
"""
        )
        sensors = GeoDataFrameLib.read_csv(_sio, sep=",")

        _sio = StringIO(
            """ID,NATURE,USAGE1,USAGE2,LEGER,ETAT,DATE_CREAT,DATE_MAJ,DATE_APP,DATE_CONF,SOURCE,ID_SOURCE,ACQU_PLANI,PREC_PLANI,ACQU_ALTI,PREC_ALTI,NB_LOGTS,NB_ETAGES,MAT_MURS,MAT_TOITS,HAUTEUR,Z_MIN_SOL,Z_MIN_TOIT,Z_MAX_TOIT,Z_MAX_SOL,ORIGIN_BAT,APP_FF,geometry
BATIMENT0000000302923133,Indifférenciée,Indifférencié,,Non,En service,2012-06-19 18:43:00,2018-09-18 13:36:26,,,,,BDParcellaire recalée,3.0,Corrélation,1.0,,,,,6.2,6.0,12.2,16.0,6.2,Cadastre,,"POLYGON Z ((354657.1 6688439.9 12.2, 354664.3 6688441.8 12.2, 354668.8 6688424 12.2, 354661.7 6688422.2 12.2, 354657.1 6688439.9 12.2))"
BATIMENT0000000302923132,"Industriel, agricole ou commercial",Commercial et services,,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,2011-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,0.0,1.0,,,13.4,6.0,19.5,24.2,6.5,Cadastre,C 0.4,"POLYGON Z ((354685.5 6688242.4 19.5, 354678.8 6688271.8 19.5, 354645 6688417.2 19.5, 354691.9 6688429.2 19.5, 354695.3 6688414.5 19.5, 354701.4 6688415.9 19.5, 354702.9 6688409.7 19.5, 354704.3 6688410 19.5, 354705.9 6688403.4 19.5, 354707.6 6688403.8 19.5, 354710 6688393.9 19.5, 354713.3 6688394.7 19.5, 354714.8 6688388.6 19.5, 354716.3 6688388.9 19.5, 354717.8 6688382.7 19.5, 354719.3 6688383 19.5, 354720.8 6688376.8 19.5, 354722.2 6688377.1 19.5, 354723.8 6688370.6 19.5, 354725.3 6688370.9 19.5, 354727 6688364.2 19.5, 354717.8 6688361.9 19.5, 354742.7 6688255.8 19.5, 354685.5 6688242.4 19.5))"
BATIMENT0000000302923159,Indifférenciée,Indifférencié,,Non,En service,2012-06-19 18:43:00,2018-09-18 13:36:27,,,,,BDParcellaire recalée,3.0,Interpolation bâti BDTopo,2.5,,,,,11.7,6.0,17.7,24.3,6.6,Cadastre,,"POLYGON Z ((354543.4 6688344.2 17.7, 354534.3 6688360.8 17.7, 354617.6 6688407.1 17.7, 354626.8 6688390.2 17.7, 354543.4 6688344.2 17.7))"
BATIMENT0000002335125943,Indifférenciée,Indifférencié,,Non,En service,2023-10-16 08:40:22,,,,DGFiP,,BDParcellaire,5.0,Pas de Z,9999.0,,,,,,,,,,Cadastre,,"POLYGON Z ((354627.8 6688496.5 -1000, 354637.3 6688498.8 -1000, 354643.7 6688473.3 -1000, 354634.2 6688470.9 -1000, 354627.8 6688496.5 -1000))"
BATIMENT0000002335125944,Indifférenciée,Indifférencié,,Oui,En service,2023-10-16 08:40:22,,,,DGFiP,,BDParcellaire,5.0,Pas de Z,9999.0,,,,,,,,,,Cadastre,,"POLYGON Z ((354626.4 6688497.1 -1000, 354627.8 6688496.5 -1000, 354634.2 6688470.9 -1000, 354643.7 6688473.3 -1000, 354645 6688472.7 -1000, 354633.2 6688469.6 -1000, 354626.4 6688497.1 -1000))"
BATIMENT0000002335125945,Indifférenciée,Indifférencié,,Oui,En service,2023-10-16 08:40:22,,,,DGFiP,,BDParcellaire,5.0,Pas de Z,9999.0,,,,,,,,,,Cadastre,,"POLYGON Z ((354627.8 6688496.5 -1000, 354626.4 6688497.1 -1000, 354638.2 6688500 -1000, 354645 6688472.7 -1000, 354643.7 6688473.3 -1000, 354637.3 6688498.8 -1000, 354627.8 6688496.5 -1000))"
BATIMENT0000000302923157,"Industriel, agricole ou commercial",Industriel,,Non,En service,2012-06-19 18:43:00,2018-09-18 13:36:27,,,,,BDParcellaire recalée,3.0,Interpolation bâti BDTopo,2.5,,,,,6.6,6.0,12.6,13.8,6.8,Cadastre,,"POLYGON Z ((354697.2 6688468.6 12.6, 354679.9 6688499.1 12.6, 354699.5 6688510.2 12.6, 354712.5 6688486.8 12.6, 354716.3 6688479.6 12.6, 354717.1 6688478.4 12.6, 354712.7 6688475.8 12.6, 354708.8 6688473.3 12.6, 354707.9 6688474.7 12.6, 354697.2 6688468.6 12.6))"
BATIMENT0000000302923139,"Industriel, agricole ou commercial",Commercial et services,,Oui,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,,,,,BDParcellaire recalée,3.0,Corrélation,1.0,0.0,1.0,,,7.9,6.3,14.2,16.6,6.6,Cadastre,B 1.0,"POLYGON Z ((354676.8 6688507.4 14.2, 354669.8 6688519.7 14.2, 354677.9 6688524.4 14.2, 354683.4 6688527.7 14.2, 354685.2 6688528.7 14.2, 354689.3 6688531 14.2, 354712.5 6688543.7 14.2, 354719.9 6688530.4 14.2, 354689.1 6688514 14.2, 354676.8 6688507.4 14.2))"
BATIMENT0000000302923135,Indifférenciée,Résidentiel,Commercial et services,Non,En service,2012-06-19 18:43:00,2023-01-31 17:40:48,1900-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,5.0,4.0,10,20,10.5,6.2,16.7,20.0,6.5,Cadastre,A 1.0,"POLYGON Z ((354677.9 6688524.4 16.7, 354669.8 6688519.7 16.7, 354664.6 6688529 16.7, 354676.4 6688535.4 16.7, 354680.2 6688528.6 16.7, 354676.5 6688526.6 16.7, 354677.9 6688524.4 16.7))"
BATIMENT0000000302923137,"Industriel, agricole ou commercial",Industriel,,Oui,En service,2012-06-19 18:43:00,2023-01-31 17:40:49,,,,,BDParcellaire recalée,3.0,Interpolation bâti BDTopo,2.5,,,,,4.9,6.0,10.9,15.4,6.6,Cadastre,,"POLYGON Z ((354680.5 6688537.6 10.9, 354684.6 6688539.7 10.9, 354686.6 6688535.9 10.9, 354689.3 6688531 10.9, 354685.2 6688528.7 10.9, 354683.4 6688527.7 10.9, 354678.8 6688536.8 10.9, 354680.5 6688537.6 10.9))"
BATIMENT0000000302923136,Indifférenciée,Commercial et services,Résidentiel,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,1900-01-01,,,,BDParcellaire recalée,3.0,Interpolation bâti BDTopo,2.5,6.0,3.0,,,7.3,6.2,13.5,18.3,6.6,Cadastre,A 1.0,"POLYGON Z ((354664.6 6688529 13.5, 354659.1 6688538.6 13.5, 354660.4 6688542 13.5, 354671.5 6688548 13.5, 354678 6688536.3 13.5, 354676.4 6688535.4 13.5, 354664.6 6688529 13.5))"
BATIMENT0000000302923134,Indifférenciée,Résidentiel,Commercial et services,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,1880-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,19.0,5.0,20,20,12.2,6.3,18.5,22.0,6.5,Cadastre,A 1.0,"POLYGON Z ((354684.6 6688539.7 18.5, 354680.5 6688537.6 18.5, 354678.8 6688536.8 18.5, 354678 6688536.3 18.5, 354671.5 6688548 18.5, 354683.8 6688554.7 18.5, 354689.5 6688545.1 18.5, 354683.3 6688542.2 18.5, 354684.6 6688539.7 18.5))"
BATIMENT0000000302923570,"Industriel, agricole ou commercial",Commercial et services,,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,2007-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,0.0,1.0,,,9.0,6.4,15.5,18.5,6.6,Cadastre,C 0.4,"POLYGON Z ((354686.6 6688535.9 15.5, 354692.5 6688539.2 15.5, 354690.5 6688542.8 15.5, 354707.6 6688552.4 15.5, 354712.5 6688543.7 15.5, 354689.3 6688531 15.5, 354686.6 6688535.9 15.5))"
BATIMENT0000000302923571,Indifférenciée,Résidentiel,Commercial et services,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,2007-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,8.0,4.0,00,00,9.4,6.3,15.8,21.1,6.6,Cadastre,C 0.5,"POLYGON Z ((354683.8 6688554.7 15.8, 354692.6 6688559.5 15.8, 354698.9 6688562.9 15.8, 354701.9 6688562.4 15.8, 354707.6 6688552.4 15.8, 354690.5 6688542.8 15.8, 354689.5 6688545.1 15.8, 354683.8 6688554.7 15.8))"
"""
        )
        masks = GeoDataFrameLib.read_csv(_sio, sep=",")
        masks.fillna({"HAUTEUR": 3.33}, inplace=True)

        result = STSkyMap25D(
            masks,
            sensors,
            nRays=64,
            rayLength=100,
            elevationFieldname="HAUTEUR",
            h0=0.0,
            size=1.0,
            withIndices=True,
            withAngles=True,
            encode=True,
            threshold=1e-7,
        ).run()
        self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
        self.assertEqual(len(sensors), len(result), "Count rows")
        self.assertEqual(len(sensors.columns) + 11, len(result.columns), "Count columns")
        # self.__plot(masks, sensors, result, bbox=None)

    def testRun9(self):
        from io import StringIO
        from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib

        _sio = StringIO(
            """gid,row,column,dist_to_ctr,dalle_id,geometry
0,0,0,1358.9938870355277,276,"POLYGON ((352548.15 6683322.25, 352548.15 6683324.25, 352546.15 6683324.25, 352546.15 6683322.25, 352548.15 6683322.25))"
"""
        )
        sensors = GeoDataFrameLib.read_csv(_sio, sep=",")

        _sio = StringIO(
            """ID,NATURE,USAGE1,USAGE2,LEGER,ETAT,DATE_CREAT,DATE_MAJ,DATE_APP,DATE_CONF,SOURCE,ID_SOURCE,ACQU_PLANI,PREC_PLANI,ACQU_ALTI,PREC_ALTI,NB_LOGTS,NB_ETAGES,MAT_MURS,MAT_TOITS,HAUTEUR,Z_MIN_SOL,Z_MIN_TOIT,Z_MAX_TOIT,Z_MAX_SOL,ORIGIN_BAT,APP_FF,geometry
"""
        )
        masks = GeoDataFrameLib.read_csv(_sio, sep=",")

        result = STSkyMap25D(
            masks,
            sensors,
            nRays=4,
            rayLength=100,
            elevationFieldname="HAUTEUR",
            h0=0.0,
            size=1.0,
            withIndices=True,
            withAngles=True,
            encode=True,
            threshold=1e-7,
        ).run()
        self.assertIsInstance(result, GeoDataFrame, "result is a GeoDataFrame")
        self.assertEqual(len(sensors), len(result), "Count rows")
        self.assertEqual(len(sensors.columns) + 11, len(result.columns), "Count columns")
        # self.__plot(masks, sensors, result, bbox=None)


if __name__ == "__main__":
    # import sys; sys.argv = ['', 'Test.testRun']
    unittest.main()
