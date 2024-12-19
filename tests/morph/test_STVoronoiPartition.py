'''
Created on 25 sept. 2020

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
along with t4gpd. If not, see <https://www.gnu.org/licenses/>.
'''
import unittest
from shapely import MultiPoint, Polygon
from geopandas import GeoDataFrame
from t4gpd.morph.STVoronoiPartition import STVoronoiPartition


class STVoronoiPartitionTest(unittest.TestCase):

    def setUp(self):
        pointsGeom = MultiPoint(((0, 0), (100, 100), (0, 100), (100, 0), (20, 70),
                                 (70, 80), (60, 50), (50, 20), (20, 30), (80, 10),
                                 (10, 10)))
        self.points = GeoDataFrame([
            {"gid": gid, "geometry": point}
            for gid, point in enumerate(pointsGeom.geoms)
        ])

    def tearDown(self):
        pass

    @staticmethod
    def _plot(inputs, tin, vor):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))

        inputs.plot(ax=ax, color="black", marker="+", label="Input points")
        inputs.apply(lambda x: ax.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0],
            color="black", size=9, ha="left", va="top"), axis=1)

        tin.boundary.plot(ax=ax, color="green", linewidth=0.5,
                          linestyle="-.",
                          label="Delaunay Triangul.")

        vor.boundary.plot(ax=ax, color="red", label="Voronoi Tessel.")
        vor.apply(lambda x: ax.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0],
            color="red", size=14, ha="center"), axis=1)
        plt.legend(fontsize=14)
        plt.axis("equal")
        plt.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        op = STVoronoiPartition(self.points)
        result = op.run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.points), len(result), "Count rows")
        self.assertEqual(len(self.points.columns),
                         len(result.columns), "Count columns")

        for i, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon,
                                  "Is a GeoDataFrame of Polygon")

        # STVoronoiPartitionTest._plot(
        #     self.points, op.getDelaunayTriangles(), result)
        # result.to_file("/tmp/xxx.shp")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
