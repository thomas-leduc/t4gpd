"""
Created on 15 nov. 2024

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

import unittest

from geopandas.geodataframe import GeoDataFrame
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.geoProcesses.OrientedSVF import OrientedSVF
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.skymap.STSkyMap25D import STSkyMap25D


class OrientedSVFTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoints = STGrid(
            self.buildings, dx=80, indoor=False, intoPoint=True
        ).run()
        self.viewpoints.sort_values(by="gid", inplace=True)
        self.viewpoints.drop(
            columns=["row", "column", "neighbors4", "neighbors8", "indoor"],
            inplace=True,
        )

        nRays = 48  # 96
        self.skymaps = STSkyMap25D(
            self.buildings,
            self.viewpoints,
            nRays=nRays,
            rayLength=100,
            elevationFieldname="HAUTEUR",
            h0=0,
            size=4,
            withIndices=True,
            withAngles=True,
            encode=False,
        ).run()

    def tearDown(self):
        pass

    def __plot(self, actual, method):
        import matplotlib.pyplot as plt
        from numpy import sqrt
        from t4gpd.morph.geoProcesses.Translation import Translation

        vmin, vmax = 0, 1.0

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.15 * 8.26))
        self.buildings.plot(ax=ax, color="grey")
        self.viewpoints.plot(ax=ax, color="red", marker="P")
        self.skymaps.set_geometry("viewpoint").plot(
            ax=ax,
            alpha=0.5,
            column="svf",
            cmap="viridis",
            vmin=vmin,
            vmax=vmax,
            legend=True,
            legend_kwds={"label": "svf*"},
        )
        self.skymaps.apply(
            lambda x: ax.annotate(
                text=f"{x['svf']:.2f}",
                xy=x.geometry.centroid.coords[0],
                color="red",
                size=12,
                ha="center",
            ),
            axis=1,
        )

        if "quadrants" == method:
            dxy = 10
            trios = [
                ("svf4_north", 0, dxy),
                ("svf4_east", dxy, 0),
                ("svf4_south", 0, -dxy),
                ("svf4_west", -dxy, 0),
            ]
        elif "octants" == method:
            dxy = 10
            trios = [
                ("svf8_north", 0, dxy),
                ("svf8_northeast", dxy, dxy),
                ("svf8_east", dxy, 0),
                ("svf8_southeast", dxy, -dxy),
                ("svf8_south", 0, -dxy),
                ("svf8_southwest", -dxy, -dxy),
                ("svf8_west", -dxy, 0),
                ("svf8_northwest", -dxy, dxy),
            ]
        elif "duodecants" == method:
            dxy = 15
            da, db = 0.5 * dxy, (dxy * sqrt(3)) / 2
            trios = [
                ("svf12_n", 0, dxy),
                ("svf12_nne", da, db),
                ("svf12_ene", db, da),
                ("svf12_e", dxy, 0),
                ("svf12_ese", db, -da),
                ("svf12_sse", da, -db),
                ("svf12_s", 0, -dxy),
                ("svf12_ssw", -da, -db),
                ("svf12_wsw", -db, -da),
                ("svf12_w", -dxy, 0),
                ("svf12_wnw", -db, da),
                ("svf12_nnw", -da, db),
            ]
        for indic, dx, dy in trios:
            op = Translation((dx, dy))
            skymaps3 = STGeoProcess(op, actual).run()
            skymaps3.plot(
                ax=ax, alpha=0.5, column=indic, cmap="viridis", vmin=vmin, vmax=vmax
            )
            skymaps3.apply(
                lambda x: ax.annotate(
                    text=f"{x[indic]:.2f}",
                    xy=x.geometry.centroid.coords[0],
                    color="black",
                    size=12,
                    ha="center",
                ),
                axis=1,
            )
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        method = "quadrants"
        op = OrientedSVF(self.skymaps, "angles", method=method, svf=2018)
        actual = STGeoProcess(op, self.skymaps).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.skymaps), len(actual), "Count rows")
        self.assertEqual(
            len(self.skymaps.columns) + 4, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            avgSvf = (
                row.svf4_north + row.svf4_east + row.svf4_south + row.svf4_west
            ) / 4
            self.assertAlmostEqual(row.svf, avgSvf, None, "Test svf* values", 1e-9)

        # self.__plot(actual, method)

    def testRun2(self):
        method = "octants"
        op = OrientedSVF(self.skymaps, "angles", method=method, svf=2018)
        actual = STGeoProcess(op, self.skymaps).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.skymaps), len(actual), "Count rows")
        self.assertEqual(
            len(self.skymaps.columns) + 8, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            avgSvf = (
                row.svf8_north
                + row.svf8_northeast
                + row.svf8_east
                + row.svf8_southeast
                + row.svf8_south
                + row.svf8_southwest
                + row.svf8_west
                + row.svf8_northwest
            ) / 8
            self.assertAlmostEqual(row.svf, avgSvf, None, "Test svf* values", 1e-9)

        # self.__plot(actual, method)

    def testRun3(self):
        method = "duodecants"
        op = OrientedSVF(self.skymaps, "angles", method=method, svf=2018)
        actual = STGeoProcess(op, self.skymaps).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.skymaps), len(actual), "Count rows")
        self.assertEqual(
            len(self.skymaps.columns) + 12, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            avgSvf = (
                row.svf12_n
                + row.svf12_nne
                + row.svf12_ene
                + row.svf12_e
                + row.svf12_ese
                + row.svf12_sse
                + row.svf12_s
                + row.svf12_ssw
                + row.svf12_wsw
                + row.svf12_w
                + row.svf12_wnw
                + row.svf12_nnw
            ) / 12
            self.assertAlmostEqual(row.svf, avgSvf, None, "Test svf* values", 1e-9)

        # self.__plot(actual, method)

    def testRun4(self):
        method1, method2, method3 = "quadrants", "octants", "duodecants"
        op1 = OrientedSVF(self.skymaps, "angles", method=method1, svf=2018)
        op3 = OrientedSVF(self.skymaps, "angles", method=method3, svf=2018)
        actual = STGeoProcess([op1, op3], self.skymaps).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.skymaps), len(actual), "Count rows")
        self.assertEqual(
            len(self.skymaps.columns) + 4 + 12, len(actual.columns), "Count columns"
        )

        for _, row in actual.iterrows():
            north = (row.svf12_nne + row.svf12_n + row.svf12_nnw) / 3
            east = (row.svf12_ene + row.svf12_e + row.svf12_ese) / 3
            south = (row.svf12_sse + row.svf12_s + row.svf12_ssw) / 3
            west = (row.svf12_wsw + row.svf12_w + row.svf12_wnw) / 3

            epsilon = 1e-9
            self.assertAlmostEqual(
                row.svf4_north, north, None, "Test north values", epsilon
            )
            self.assertAlmostEqual(
                row.svf4_east, east, None, "Test east values", epsilon
            )
            self.assertAlmostEqual(
                row.svf4_south, south, None, "Test south values", epsilon
            )
            self.assertAlmostEqual(
                row.svf4_west, west, None, "Test west values", epsilon
            )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRun']
    unittest.main()
