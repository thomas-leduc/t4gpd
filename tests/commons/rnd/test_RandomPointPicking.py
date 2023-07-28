'''
Created on 9 janv. 2023

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
from shapely.geometry import Point, Polygon
from t4gpd.commons.rnd.RandomPointPicking import RandomPointPicking
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D


class RandomPointPickingTest(unittest.TestCase):

    def setUp(self):
        self.npts = 50

    def tearDown(self):
        pass

    def testConvexPolygonPointPicking(self):
        ngon = Point([0, 0]).buffer(0.5, 4)
        actual = RandomPointPicking.convexPolygonPointPicking(ngon, self.npts)
        self.assertGreaterEqual(self.npts, len(actual), 'Count number of random points')
        for pt in actual:
            self.assertTrue(ngon.contains(Point(pt)), 'Check if points are in the n-gon')

        '''
        import matplotlib.pyplot as plt
        from geopandas import GeoDataFrame
        gdf = RandomPointPicking.toGeoDataFrame(actual)
        ngon = GeoDataFrame([{'geometry': ngon}])
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        ax.set_title(f'{len(gdf)} pts')
        ngon.boundary.plot(ax=ax, color='red')
        gdf.plot(ax=ax, marker='P', column='gid')
        plt.axis('off')
        plt.show()
        '''

    def testSimpleTriangulation(self):
        ngon = Point([0, 0]).buffer(0.5, 3)
        expected = 10
        actual = RandomPointPicking._simpleTriangulation(ngon)
        self.assertEqual(expected, len(actual), 'Test number of triangles from n-gon simple triangulation')

    def testTrianglePointPicking(self):
        tri = Polygon([ (1, 1), (1.5, 3), (1, 3) ])
        actual = RandomPointPicking.trianglePointPicking(tri, self.npts)
        self.assertEqual(self.npts, len(actual), 'Count number of random points')
        for pt in actual:
            self.assertTrue(tri.contains(Point(pt)), 'Check if points are in the triangle')

        '''
        import matplotlib.pyplot as plt
        from geopandas import GeoDataFrame
        gdf = RandomPointPicking.toGeoDataFrame(actual)
        tri = GeoDataFrame([{'geometry': tri}])
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        ax.set_title(f'{len(gdf)} pts')
        tri.boundary.plot(ax=ax, color='red')
        gdf.plot(ax=ax, marker='P', column='gid')
        plt.axis('off')
        plt.show()
        '''

    def testUnitDiskPointPicking(self):
        actual = RandomPointPicking.unitDiskPointPicking(self.npts)
        self.assertEqual(self.npts, len(actual), 'Count number of random points')
        origin = [0, 0]
        for pt in actual:
            self.assertTrue(GeomLib.distFromTo(origin, pt) <= 1, 
                            'Check if points are in the unit disk')

    def test(self):
        actual = RandomPointPicking.unitSpherePointPicking(self.npts)
        self.assertEqual(self.npts, len(actual), 'Count number of random points')
        origin = [0, 0, 0]
        for pt in actual:
            self.assertAlmostEqual(1.0, GeomLib3D.distFromTo(origin, pt), None,
                                   'Check if points are on the unit sphere', 1e-9)

        '''
        from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
        gdf = RandomPointPicking.toGeoDataFrame(actual)
        scene = ToUnstructuredGrid([gdf], fieldname='gid').run()
        scene.plot(scalars='gid', cmap='gist_earth', show_edges=False,
                    show_scalar_bar=True, point_size=6.0, render_points_as_spheres=True)
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
