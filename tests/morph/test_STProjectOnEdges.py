"""
Created on 6 mar. 2025

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
from io import StringIO
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.morph.STProjectOnEdges import STProjectOnEdges


class STProjectOnEdgesTest(unittest.TestCase):
    def setUp(self):
        _sio = StringIO(
            """objectid,geometry,useless
31503,POINT (770266.1247979854 6278803.513605595)
57191,POINT (770273.4363976802 6278809.912107986)
32998,POINT (770255.0043001117 6278814.982907161)
57189,POINT (770264.0773968092 6278820.582199424)
57186,POINT (770258.1593028808 6278827.422499829)
"""
        )
        self.points = GeoDataFrameLib.read_csv(_sio, sep=",")

        _sio = StringIO(
            """ID,geometry
BATIMENT0000000211118739,"POLYGON Z ((770250.7 6278803.4 43.9, 770245.7 6278808.7 43.9, 770255.1 6278816.1 43.9, 770259.9 6278810.8 43.9, 770250.7 6278803.4 43.9))"
BATIMENT0000000211118740,"POLYGON Z ((770254.8 6278798.7 44.2, 770250.7 6278803.4 44.2, 770259.9 6278810.8 44.2, 770265.8 6278804.2 44.2, 770258.1 6278798.3 44.2, 770256.5 6278800.2 44.2, 770254.8 6278798.7 44.2))"
BATIMENT0000000211118744,"POLYGON Z ((770261.9 6278790.9 47, 770258.1 6278795 47, 770259.9 6278796.5 47, 770258.1 6278798.3 47, 770265.8 6278804.2 47, 770271.4 6278798.1 47, 770261.9 6278790.9 47))"
BATIMENT0000000211118755,"POLYGON Z ((770288.6 6278813.4 49.9, 770286.7 6278811.7 49.9, 770278.4 6278804.4 49.9, 770273.4 6278809.9 49.9, 770281.8 6278817.4 49.9, 770283.4 6278815.7 49.9, 770285.4 6278817.3 49.9, 770288.6 6278813.4 49.9))"
BATIMENT0000000211118756,"POLYGON Z ((770279 6278824.8 48.8, 770268.4 6278815.5 48.8, 770263.3 6278821.1 48.8, 770274.7 6278830.1 48.8, 770279 6278824.8 48.8))"
BATIMENT0000000211118757,"POLYGON Z ((770282.7 6278820.5 49.6, 770281.5 6278819.7 49.6, 770281.4 6278818.2 49.6, 770281.8 6278817.4 49.6, 770273.4 6278809.9 49.6, 770268.4 6278815.5 49.6, 770279 6278824.8 49.6, 770282.7 6278820.5 49.6))"
"""
        )
        self.polygons = GeoDataFrameLib.read_csv(_sio, sep=",")

    def tearDown(self):
        pass

    def __plot(self, actual):
        import matplotlib.pyplot as plt

        minx, miny, maxx, maxy = self.points.buffer(2.5).total_bounds
        fig, ax = plt.subplots(figsize=(1.25 * 8.26, 1.5 * 8.26))
        self.polygons.plot(ax=ax, color="lightgrey", edgecolor="dimgrey")
        self.points.plot(ax=ax, color="red", marker="+")
        self.points.apply(
            lambda x: ax.annotate(
                text=x.objectid,
                xy=x.geometry.coords[0],
                color="red",
                size=14,
                ha="left",
                va="top",
            ),
            axis=1,
        )
        actual.plot(ax=ax, color="blue", marker="^")
        ax.axis([minx, maxx, miny, maxy])
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        actual = STProjectOnEdges(
            self.points, "objectid", self.polygons, "ID", distToEdge=0.5
        ).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.points), len(actual), "Count rows")
        self.assertEqual(
            len(self.points.columns) + 1, len(actual.columns), "Count columns"
        )

        self.__plot(actual)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
