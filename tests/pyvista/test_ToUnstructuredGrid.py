'''
Created on 15 avr. 2022

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
from numpy.random import randint, seed
from pyvista import global_theme, Plotter, Sphere
from shapely.geometry import LineString
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STPointsDensifier2 import STPointsDensifier2
from t4gpd.morph.geoProcesses.FootprintExtruder import FootprintExtruder
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid


class ToUnstructuredGridTest(unittest.TestCase):

    def setUp(self):
        seed(0)
        buildings = GeoDataFrameDemos.regularGridOfPlots(3, 4, dw=5.0)
        buildings['HAUTEUR'] = 3.0 * randint(2, 7, size=len(buildings))

        self.sensors = STPointsDensifier2(buildings, curvAbsc=[0.5], pathidFieldname=None).run()
        self.sensors['__TMP__'] = list(zip(self.sensors.geometry, self.sensors.HAUTEUR))
        self.sensors.geometry = self.sensors.__TMP__.apply(lambda t: GeomLib.forceZCoordinateToZ0(t[0], z0=t[1] / 2))
        self.sensors.drop(columns=['__TMP__'], inplace=True)
        self.sensors['MonAttribut'] = 5 * randint(0, 10, size=len(self.sensors))

        self.roads = GeoDataFrame([
            {'gid': 1, 'geometry': LineString([(-30, -10), (30, -10)])},
            {'gid': 2, 'geometry': LineString([(-30, 10), (30, 10)])},
            {'gid': 3, 'geometry': LineString([(-20, -20), (-20, 20)])},
            {'gid': 4, 'geometry': LineString([(0, -20), (0, 20)])},
            {'gid': 5, 'geometry': LineString([(20, -20), (20, 20)])}
            ])

        op = FootprintExtruder(buildings, 'HAUTEUR', forceZCoordToZero=True)
        self.buildingsIn3d = STGeoProcess(op, buildings).run()

    def tearDown(self):
        pass

    def testRun1(self):
        global_theme.background = 'grey'
        global_theme.axes.show = True

        result = ToUnstructuredGrid([self.buildingsIn3d, self.roads, self.sensors], 'MonAttribut').run()
        result.plot(scalars='MonAttribut', cmap='gist_earth', show_edges=False,
                    show_scalar_bar=True, clim=[0, 18], cpos='xy',
                    point_size=20.0, render_points_as_spheres=True,
                    screenshot='./my_pyvista_1.png')

    def testRun2(self):
        bLayer = ToUnstructuredGrid([self.buildingsIn3d], 'HAUTEUR').run()
        rLayer = ToUnstructuredGrid([self.roads]).run()
        sLayer = ToUnstructuredGrid([self.sensors], 'MonAttribut').run()

        sphere = Sphere(radius=0.5, phi_resolution=10, theta_resolution=10)
        sLayerB = sLayer.glyph(scale=False, geom=sphere)

        plotter = Plotter(window_size=(1000, 800))
        plotter.add_mesh(bLayer, color='dimgrey', opacity=0.99, show_edges=False)
        plotter.add_mesh(rLayer, color='black')
        plotter.add_mesh(sLayerB, color='red')
        plotter.show_grid()
        plotter.camera_position = 'xy'
        # plotter.camera.azimuth = 45
        plotter.camera.roll += 10
        plotter.show(screenshot='./my_pyvista_2.png')

    def testRun3(self):
        building = GeoDataFrameDemos.singleBuildingInNantes()
        result = ToUnstructuredGrid([building]).run()
        result.plot(cmap='gist_earth', show_edges=True,
                    screenshot='./my_pyvista_3.png')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRun']
    unittest.main()
