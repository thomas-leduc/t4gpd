'''
Created on 22 Aug. 2022

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

from pyvista import Plotter
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.demos.GeoDataFrameDemos5 import GeoDataFrameDemos5
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.geoProcesses.MoveSensorsAwayFromSurface import MoveSensorsAwayFromSurface

from t4gpd.pyvista.geoProcesses.SVF3D import SVF3D


class SVF3DTest(unittest.TestCase):

    def setUp(self):
        self.gdf = GeoDataFrameDemos5.cirSceneMasque1Corr()
        self.gdf['normal_vec'] = self.gdf.geometry.apply(lambda g: GeomLib3D.getFaceNormalVector(g))
        self.gdf.reset_index(inplace=True)
        self.gdf.rename(columns={'index': 'gid'}, inplace=True)

        self.sensors = self.gdf.copy(deep=True)
        # ~ WE KEEP ONLY A FEW SENSORS
        self.sensors = self.sensors[ self.sensors.index % 90 == 0 ]
        self.sensors['main_dir'] = self.sensors.normal_vec
        self.sensors.reset_index(drop=True, inplace=True)

        self.sensors.geometry = self.sensors.geometry.apply(lambda g: GeomLib3D.centroid(g))
        op = MoveSensorsAwayFromSurface(self.sensors, 'normal_vec', dist=0.1)
        self.sensors = STGeoProcess(op, self.sensors).run()

    def tearDown(self):
        pass

    def __plot(self, result):
        scene = ToUnstructuredGrid([self.gdf, self.sensors, result], fieldname='svf').run()
        # scene.plot(show_edges=True, point_size=30.0, render_points_as_spheres=True, opacity=1.0, cpos='xy')

        centroids = result.geometry.apply(lambda g: g.coords[0]).to_list()
        labels = result.svf.apply(lambda v: f'{100 * v:.2f}%').to_list()

        plotter = Plotter(window_size=(1000, 800))
        plotter.add_mesh(scene, scalars='svf', cmap='gist_earth',
            show_edges=False,
            show_scalar_bar=True, point_size=30.0,
            # ~ opacity=0.99, show_scalar_bar=True, point_size=15.0,
            render_points_as_spheres=True, line_width=2.0, color='k')
        plotter.add_point_labels(centroids, labels, font_size=20, point_size=1e-3)
        # plotter.camera_position = 'xy'
        plotter.show()

    def testRun1(self):
        nrays = 10000
        op = SVF3D([self.gdf], nrays=nrays, method='MonteCarlo')
        result = STGeoProcess(op, self.sensors).execute()
        self.__plot(result)
        print(result[['gid', 'cir_id', 'svf']])

    def testRun2(self):
        nrays = 10000
        op = SVF3D([self.gdf], nrays=nrays, method='geodeciel')
        result = STGeoProcess(op, self.sensors).execute()
        self.__plot(result)
        print(result[['gid', 'cir_id', 'svf']])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
