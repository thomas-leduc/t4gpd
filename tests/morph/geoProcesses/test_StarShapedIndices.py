"""
Created on 15 janv. 2021

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

from geopandas import GeoDataFrame
from shapely import Point, get_num_geometries
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.isovist.STIsovistField2D import STIsovistField2D
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.morph.geoProcesses.StarShapedIndices import StarShapedIndices


class StarShapedIndicesTest(unittest.TestCase):

    def setUp(self):
        self.nrays, self.raylen = 36, 50.0
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoints = GeoDataFrame(
            [{"geometry": Point((355317.9, 6688409.5))}], crs=self.buildings.crs
        )
        self.isovRays, self.isov = STIsovistField2D(
            self.buildings, self.viewpoints, self.nrays, self.raylen
        ).run()

    def tearDown(self):
        pass

    def __plot(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8.26, 8.26))
        self.buildings.plot(ax=ax, color="lightgrey", edgecolor="grey")
        self.viewpoints.plot(ax=ax, color="red", marker="P")
        self.isovRays.plot(ax=ax, color="blue")
        self.isov.plot(ax=ax, color="yellow", alpha=0.5)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        op = StarShapedIndices(precision=1.0, base=2)
        actual = STGeoProcess(op, self.isovRays).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.viewpoints), len(actual), "Count rows")
        self.assertEqual(len(self.viewpoints) + 8, len(actual.columns), "Count columns")

        for _, row in actual.iterrows():
            self.assertEqual(
                self.nrays,
                get_num_geometries(row.geometry),
                f"Check number of rays",
            )
            self.assertGreaterEqual(row["entropy"], 0, "Test entropy attribute value")
            for fieldname in [
                "min_raylen",
                "avg_raylen",
                "std_raylen",
                "max_raylen",
                "med_raylen",
                "drift",
            ]:
                self.assertTrue(
                    0 <= row[fieldname] <= self.raylen + 1e-6, f"Check {fieldname} value"
                )

        # self.__plot()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
