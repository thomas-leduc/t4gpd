'''
Created on 17 dec. 2021

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
import unittest

from geopandas import GeoDataFrame
from numpy import pi
from shapely.geometry import MultiLineString, Point, Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.commons.isovist.ExactIsovistLib import ExactIsovistLib
from t4gpd.morph.STGrid import STGrid


class ExactIsovistLibTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        pass

    def __common_tests(self, result, perim=None):
        self.assertIsInstance(result, dict, "Is a Python dict")
        self.assertEqual(13, len(result.keys()), "Count keys")

        self.assertIsInstance(result["geometry"], Polygon, "Is a Polygon")
        self.assertIsInstance(result["artif_hori"], MultiLineString,
                              "'artif_hori' Is a MultiLineString")
        self.assertIsInstance(result["solid_surf"], MultiLineString,
                              "'solid_surf' Is a MultiLineString")
        self.assertIsInstance(result["occlu_surf"], MultiLineString,
                              "'occlu_surf' Is a MultiLineString")
        self.assertAlmostEqual(result["perim"],
                               result["occlusiv"] +
                               result["solid"] + result["skyline"],
                               None, "Test attr. values (1)", 1e-6)
        self.assertAlmostEqual(1.0,
                               result["occlusiv_r"] +
                               result["solid_r"] + result["skyline_r"],
                               None, "Test attr. values (2)", 1e-6)
        if perim is not None:
            self.assertAlmostEqual(
                perim, result["perim"], None, "Test perimeter value", 1e-2)

    def __plot_tests(self, buildings, viewpoint, result, workdir=None):
        import matplotlib.pyplot as plt
        
        viewpoint = GeoDataFrame(
            [{"geometry": viewpoint}], crs=self.buildings.crs)
        isovist = GeoDataFrame(
            [{"geometry": result["geometry"]}], crs=self.buildings.crs)
        nodes = GeoDataFrame(result["nodes"], crs=self.buildings.crs)
        artificialHorizon = GeoDataFrame(
            [{"geometry": result["artif_hori"]}], crs=self.buildings.crs)
        materialSurfaces = GeoDataFrame(
            [{"geometry": result["solid_surf"]}], crs=self.buildings.crs)
        occludingSurfaces = GeoDataFrame(
            [{"geometry": result["occlu_surf"]}], crs=self.buildings.crs)

        if not workdir is None:
            buildings.to_file(f"{workdir}/_buildings.shp")
            viewpoint.to_file(f"{workdir}/_viewpoint.shp")
            isovist.to_file(f"{workdir}/_isovist.shp")
            nodes.to_file(f"{workdir}/_nodes.shp")
            artificialHorizon.to_file(f"{workdir}/_skyline.shp")
            if (not result["solid_surf"].is_empty):
                materialSurfaces.to_file(f"{workdir}/_material.shp")
            if (not result["occlu_surf"].is_empty):
                occludingSurfaces.to_file(f"{workdir}/_occluding.shp")

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        buildings.plot(ax=ax, color="grey")
        viewpoint.plot(ax=ax, marker="o", color="red")
        isovist.boundary.plot(ax=ax, color="yellow", hatch="/", linewidth=0.5)
        artificialHorizon.plot(ax=ax, color="blue", linewidth=5.0, alpha=0.3)
        if (not result["solid_surf"].is_empty):
            materialSurfaces.plot(ax=ax, color="brown",
                                  linewidth=5.0, alpha=0.3)
        if (not result["occlu_surf"].is_empty):
            occludingSurfaces.plot(ax=ax, color="green",
                                   linewidth=5.0, alpha=0.3)
        nodes.plot(ax=ax, marker="+", color="black")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        buildings = GeoDataFrameDemos.regularGridOfPlots(1, 1, dw=1.0)
        pairs = [
            (Point((5, 0)), 71.68),
            (Point((0, 5)), 71.68),
            (Point((-5, 0)), 71.68),
            (Point((0, -5)), 71.68),
            (Point((0, 11)), 2 * pi * 10.0),
            (Point((0, 12)), 2 * pi * 10.0),
        ]
        for viewpoint, perim in pairs:
            result = ExactIsovistLib.run(
                buildings, viewpoint, maxRayLength=10.0, delta=3.0)
            self.__common_tests(result, perim)
            # self.__plot_tests(buildings, viewpoint, result)

    def testRun2(self):
        buildings = GeoDataFrameDemos.regularGridOfPlots(6, 6, dw=5.0)
        pairs = [
            (Point((0, 0)), 873.94),
            (Point((5, 0)), 877.93),
        ]
        for viewpoint, perim in pairs:
            result = ExactIsovistLib.run(
                buildings, viewpoint, maxRayLength=100.0, delta=3.0)
            self.__common_tests(result, perim)
            # self.__plot_tests(buildings, viewpoint, result)

    def testRun3(self):
        pairs = [
            (Point((355388.222, 6688408.698)), 959.88),
            (Point((355262.596, 6688405.552)), 1438.24),
            (Point((355350.125, 6688445.012)), 632.92),
            (Point((355271.557, 6688570.859)), 1036.61),
            (Point((355184.075, 6688676.868)), 960.11),
            (Point((355159.626, 6688560.735)), 1059.28),
            (Point((355384.5, 6688497.02)), None),
        ]
        for viewpoint, perim in pairs:
            result = ExactIsovistLib.run(
                self.buildings, viewpoint, maxRayLength=150.0, delta=3.0)
            self.__common_tests(result, perim)
            # self.__plot_tests(self.buildings, viewpoint, result)

    def testRun4(self):
        # dx = 5
        # dx = 25
        dx = 50
        grid = STGrid(self.buildings, dx, dy=None, indoor=False,
                      intoPoint=True, encode=False).run()
        print(f"{len(grid)} viewpoints")
        gids = []
        for _, (gid, viewpoint) in grid[["gid", "geometry"]].iterrows():
            try:
                result = ExactIsovistLib.run(
                    self.buildings, viewpoint, maxRayLength=150.0, delta=3.0)
                self.__common_tests(result, None)
                # self.__plot_tests(self.buildings, viewpoint, result)
            except:
                gids.append(gid)
        print(f"Problem with {len(gids)} viewpoint(s): {sorted(gids)}")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
