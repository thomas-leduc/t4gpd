'''
Created on 23 juin 2022

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
from _io import StringIO
import unittest

from geopandas import GeoDataFrame
from pandas import merge, read_csv
from pyvista import Plotter
from shapely.geometry import LineString, Point
from shapely.wkt import loads
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.STRaysToViewFactors import STRaysToViewFactors
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.commons.RayCasting3DLib import RayCasting3DLib
from t4gpd.pyvista.geoProcesses.RayCasting3D import RayCasting3D


class STRaysToViewFactorsTest(unittest.TestCase):

    def setUp(self):
        _sio = StringIO("""gid;geometry
0;POLYGON Z ((0 0 2, 2 0 2, 2 2 2, 0 2 2, 0 0 2))
1;POLYGON Z ((0 0 0, 0 2 0, 2 2 0, 2 0 0, 0 0 0))
2;POLYGON Z ((0 0 0, 2 0 0, 2 0 2, 0 0 2, 0 0 0))
3;POLYGON Z ((2 0 0, 2 2 0, 2 2 2, 2 0 2, 2 0 0))
4;POLYGON Z ((2 2 0, 0 2 0, 0 2 2, 2 2 2, 2 2 0))
5;POLYGON Z ((0 2 0, 0 0 0, 0 0 2, 0 2 2, 0 2 0))
""")
        _df = read_csv(_sio, sep=';')
        _df.geometry = _df.geometry.apply(lambda g: loads(g))
        _df.geometry = _df.geometry.apply(lambda g: GeomLib.reverseRingOrientation(g))
        self.masks = GeoDataFrame(_df)

        rows, d = [], 0.333
        for _, row in self.masks.iterrows():
            g, v = GeomLib3D.centroid(row.geometry), GeomLib3D.getFaceNormalVector(row.geometry)
            rows.append({
                'gid': row.gid,
                'geometry': LineString([g, Point([g.x + d * v[0], g.y + d * v[1], g.z + d * v[2]])])
                })
        self.arrows = GeoDataFrame(rows)

        self.sensors = GeoDataFrame([{'gid':-1, 'geometry': Point([1, 1, 1])}])

    def tearDown(self):
        pass

    def __plot(self, masks2, rays):
        centroids = masks2.geometry.apply(lambda g: GeomLib3D.centroid(g).coords[0]).to_list()
        
        scene = ToUnstructuredGrid([masks2, self.arrows, self.sensors, rays], 'viewfactor').run()
        
        plotter = Plotter(window_size=(1000, 800))
        plotter.add_mesh(scene, scalars='viewfactor', cmap='gist_earth',
            show_edges=False, show_scalar_bar=True, point_size=15.0,
            opacity=0.99, render_points_as_spheres=True, line_width=2.0, color='k')
        plotter.add_point_labels(centroids, self.masks.gid.to_list(), font_size=10, point_size=1)
        plotter.camera_position = 'xy'
        plotter.show()

    def testRun(self):
        for method in ['pyvista', 'geodeciel', 'icosahedron', 'MonteCarlo']:
            shootingDirs = RayCasting3DLib.preparePanopticRays(nrays=1000, method=method)
            op = RayCasting3D([self.masks], shootingDirs, viewpoints=self.sensors,
                              pkFieldname='gid')
            rays = STGeoProcess(op, self.sensors).execute()
    
            vfSparseMatrix = STRaysToViewFactors(rays, 'gid', 'hitGids').run()
            vfSparseMatrix['delta'] = vfSparseMatrix.viewfactor - 1 / 6
            # print(vfSparseMatrix)
            print(f'*** {method}:: error = {100 * vfSparseMatrix.delta.abs().max():.2f}%\n')
            actual = vfSparseMatrix.viewfactor.sum().squeeze()
            self.assertAlmostEqual(1.0, actual, None, 'Test sum of View Factors', 1e-3)

            '''
            masks2 = merge(self.masks, vfSparseMatrix[['dst', 'viewfactor']], how='left',
                           left_on='gid', right_on='dst')
            masks2.viewfactor = masks2.viewfactor.fillna(value=0)
            self.__plot(masks2, rays)
            '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
