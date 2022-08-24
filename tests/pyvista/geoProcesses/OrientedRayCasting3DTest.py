'''
Created on 21 juil. 2022

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
from pyvista import Plotter
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.demos.GeoDataFrameDemos5 import GeoDataFrameDemos5
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.geoProcesses.MoveSensorsAwayFromSurface import MoveSensorsAwayFromSurface

from t4gpd.pyvista.geoProcesses.OrientedRayCasting3D import OrientedRayCasting3D


class OrientedRayCasting3DTest(unittest.TestCase):

    def setUp(self):
        self.gdf = GeoDataFrameDemos5.cirSceneMasque1Corr()
        self.gdf['normal_vec'] = self.gdf.geometry.apply(lambda g: GeomLib3D.getFaceNormalVector(g))
        self.gdf.reset_index(inplace=True)
        self.gdf.rename(columns={'index': 'gid'}, inplace=True)

        self.sensors = self.gdf.copy(deep=True)
        # ~ WE KEEP ONLY A FEW SENSORS
        self.sensors = self.sensors[ self.sensors.index % 100 == 0 ]
        self.sensors['main_dir'] = self.sensors.normal_vec
        self.sensors.reset_index(drop=True, inplace=True)

        self.sensors.geometry = self.sensors.geometry.apply(lambda g: GeomLib3D.centroid(g))
        op = MoveSensorsAwayFromSurface(self.sensors, 'normal_vec', dist=1.0)
        self.sensors = STGeoProcess(op, self.sensors).run()

    def tearDown(self):
        pass

    def testRun1(self):
        nrays = 32
        op = OrientedRayCasting3D([self.gdf], maskPkFieldname=None,
                                  viewpoints=self.sensors,
                                  mainDirectionFieldname='main_dir',
                                  openness=8, nrays=nrays, maxRayLen=50,
                                  encode=False)
        result = STGeoProcess(op, self.sensors).execute()

        scene = ToUnstructuredGrid([self.gdf, self.sensors, result]).run()
        maxDiam = scene.length

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(len(self.sensors), len(result), 'Count rows')
        self.assertEqual(3 + len(self.sensors.columns), len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertEqual(nrays, row.n_rays, 'Count nb of rays')
            self.assertTrue(0 <= row.inf_ratio <= 1.0, 'Check inf_ratio attribute value')
            for hitDist in row.hitDists:
                self.assertTrue((hitDist <= maxDiam) or (float('inf') == hitDist),
                                'Check hitDists attribute value')

        # scene.plot(show_edges=True, point_size=10.0, render_points_as_spheres=True, opacity=0.99, cpos='xy')

    def testRun2(self):
        nrays = 8
        op = OrientedRayCasting3D([self.gdf], maskPkFieldname='gid',
                                  viewpoints=self.sensors,
                                  mainDirectionFieldname='main_dir',
                                  openness=8, nrays=nrays, maxRayLen=50,
                                  encode=False)
        result = STGeoProcess(op, self.sensors).execute()

        self.sensors.rename(columns={'gid': 'NEW_GID'}, inplace=True)
        scene = ToUnstructuredGrid([self.gdf, self.sensors, result], 'gid').run()
        maxDiam = scene.length

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(len(self.sensors), len(result), 'Count rows')
        self.assertEqual(4 + len(self.sensors.columns), len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            print(row.gid, row.hitGids)
            self.assertEqual(nrays, row.n_rays, 'Count nb of rays')
            self.assertTrue(0 <= row.inf_ratio <= 1.0, 'Check inf_ratio attribute value')
            for hitDist in row.hitDists:
                self.assertTrue((hitDist <= maxDiam) or (float('inf') == hitDist),
                                'Check hitDists attribute value')
            for hitGid in row.hitGids:
                if 0 == row.gid:
                    self.assertEqual(hitGid, 18, 'Check hitGids attribute value')
                elif 100 == row.gid:
                    self.assertIn(hitGid, [None, 24, 60, 96, 132, 168], 'Check hitGids attribute value')
                elif row.gid in [200, 300]:
                    self.assertIsNone(hitGid, 'Check hitGids attribute value')

        '''
        plotter = Plotter(window_size=(1000, 800))
        plotter.add_mesh(scene, show_edges=True, point_size=10.0,
                         render_points_as_spheres=True,
                         scalars='gid', cmap='gist_earth')
        plotter.add_point_labels(self.gdf.geometry.apply(
            lambda g: GeomLib3D.centroid(g).coords[0]).to_list(),
            self.gdf.gid.to_list(), font_size=10, point_size=1)
        plotter.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
