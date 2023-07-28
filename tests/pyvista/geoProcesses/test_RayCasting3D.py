'''
Created on 11 juin 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
from numpy import mean
from numpy.random import randint, seed
from pyvista import global_theme, Plotter, Sphere
from shapely.geometry import box, Point
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.FootprintExtruder import FootprintExtruder
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.geoProcesses.RayCasting3D import RayCasting3D

from t4gpd.demos.GeoDataFrameDemos5 import GeoDataFrameDemos5


class RayCasting3DTest(unittest.TestCase):

    def setUp(self):
        seed(0)
        buildings = GeoDataFrameDemos.regularGridOfPlots(3, 4, dw=5.0)
        buildings['HAUTEUR'] = 3.0 * randint(2, 7, size=len(buildings))

        op = FootprintExtruder(buildings, 'HAUTEUR', forceZCoordToZero=True)
        self.buildingsIn3d = STGeoProcess(op, buildings).run()

        self.ground = GeoDataFrame([{'geometry': box(*buildings.total_bounds), 'HAUTEUR': 0}])

        self.shootingDirs = Sphere(
            radius=1.0, center=(0, 0, 0), direction=(0, 0, 1),
            theta_resolution=10, phi_resolution=10).cell_centers().points

    def tearDown(self):
        pass

    def __centroid(self, geom):
        return mean([c for c in geom.exterior.coords], axis=0)

    def __getZ(self, geom):
        return self.__centroid(geom)[2]

    def __plot1(self, result, viewpoints):
        global_theme.background = 'grey'
        global_theme.axes.show = True

        scene = ToUnstructuredGrid(
            [self.buildingsIn3d, self.ground, result, viewpoints], 'HAUTEUR').run()
        scene.plot(scalars='HAUTEUR', cmap='gist_earth', show_edges=False, cpos='xy',
                   opacity=0.99, show_scalar_bar=True, point_size=15.0,
                   render_points_as_spheres=True, line_width=2.0, color='k')

    def __plot2(self, buildings, viewpoints, result):
        global_theme.background = 'grey'
        global_theme.axes.show = True

        scene = ToUnstructuredGrid([buildings, viewpoints, result], 'height').run()

        centroids = buildings.geometry.apply(lambda g: self.__centroid(g)).to_list()

        plotter = Plotter(window_size=(1000, 800))
        plotter.add_mesh(scene, scalars='height', cmap='gist_earth',
            show_edges=False,
            show_scalar_bar=True, point_size=15.0,
            # ~ opacity=0.99, show_scalar_bar=True, point_size=15.0,
            render_points_as_spheres=True, line_width=2.0, color='k')
        plotter.add_point_labels(centroids, buildings.pk.to_list(), font_size=10, point_size=1)
        plotter.camera_position = 'xy'
        plotter.show()

    def testRun1(self):
        viewpoints = GeoDataFrame([{'geometry': Point([0, 0, 4.5])}])

        op = RayCasting3D([self.buildingsIn3d, self.ground], self.shootingDirs)
        result = STGeoProcess(op, viewpoints).execute()
        print(f"Let's cast {result.n_rays.squeeze()} rays!")

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(4, len(result.columns), 'Count columns')
        self.assertEqual(160, result.n_rays.squeeze(), 'Count nb of rays')

        self.__plot1(result, viewpoints)

    def testRun2(self):
        viewpoints = GeoDataFrame([{'geometry': Point([0, 0, 4.5])}])

        op = RayCasting3D([self.buildingsIn3d, self.ground], self.shootingDirs, mc=0.25)
        result = STGeoProcess(op, viewpoints).execute()
        print(f"Let's cast {result.n_rays.squeeze()} rays!")

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(4, len(result.columns), 'Count columns')
        self.assertEqual(40, result.n_rays.squeeze(), 'Count nb of rays')

        self.__plot1(result, viewpoints)

    def testRun3(self):
        viewpoints = GeoDataFrame([
            {'geometry': Point([-20, 0, 3]), 'n_vect': '-1#0#0'},
            {'geometry': Point([20, 0, 3]), 'n_vect': '1#0#0'},
            ])

        op = RayCasting3D(
            [self.buildingsIn3d, self.ground], self.shootingDirs,
            viewpoints=viewpoints, normalFieldname='n_vect',
            maxRayLen=15.0)
        result = STGeoProcess(op, viewpoints).execute()
        print(f"Let's cast {result.n_rays.squeeze()} rays!")

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(2, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertEqual(80, row.n_rays, 'Count nb of rays')

        self.__plot1(result, viewpoints)

    def testRun4(self):
        buildings = GeoDataFrameDemos5.cirSceneMasque1()
        buildings['height'] = buildings.geometry.apply(lambda g: self.__getZ(g))
        buildings['pk'] = buildings.index

        d = 1e-6
        viewpoints = GeoDataFrame([
            {'geometry': Point([80 - d, 45, 22]), 'height': 22, 'normal_vec': '-1#0#0' }])

        shootingDirs = Sphere(
            radius=1.0, center=(0, 0, 0), direction=(0, 0, 1),
            theta_resolution=2, phi_resolution=2).cell_centers().points

        op = RayCasting3D([buildings], shootingDirs, viewpoints=viewpoints,
            normalFieldname='normal_vec', pkFieldname='pk',
            mc=None, maxRayLen=130.0, showHitPoints=False)
        result = STGeoProcess(op, viewpoints).execute()
        print(f"Let's cast {result.n_rays.squeeze()} rays!")

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(4 + len(viewpoints.columns), len(result.columns), 'Count columns')
        self.assertEqual(4, result.n_rays.squeeze(), 'Count nb of rays')
        self.assertEqual(0.5, result.inf_ratio.squeeze(), 'SVF estimate')

        for hitDist in result.hitDists.squeeze():
            self.assertTrue((
                (hitDist == float('inf')) or 
                (hitDist < 130.0)), 'Check hitDist')

        for hitGid in result.hitGids.squeeze():
            self.assertTrue(hitGid in [None, 0, 5], 'Check hitGid')

        self.__plot2(buildings, viewpoints, result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
