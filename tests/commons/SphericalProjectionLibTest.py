'''
Created on 19 sept. 2022

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
from shapely.geometry import Point, Polygon
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid

import matplotlib.pyplot as plt
from t4gpd.commons.SphericalProjectionLib import SphericalProjectionLib


class SphericalProjectionLibTest(unittest.TestCase):

    def setUp(self):
        self.vp = Point([10, 10, 1.6])
        h1, h2 = 30, 10
        self.f1 = Polygon([(0, 0, 0), (0, 20, 0), (0, 20, h1), (0, 0, h1), (0, 0, 0)])
        self.f1 = Polygon([(0, 0, 0), (0, 5, 0), (0, 5, h2), (0, 15, h2), (0, 15, 0),
                           (0, 20, 0), (0, 20, h1), (0, 0, h1), (0, 0, 0)])
        self.f2 = Polygon([(20, 0, 0), (20, 0, h2), (20, 20, h2), (20, 20, 0), (20, 0, 0)])
        self.vpGdf = GeoDataFrame(data=[ {'gid': 0, 'geometry': self.vp} ])
        self.facesGdf = GeoDataFrame(data=[
            {'gid': 1, 'geometry': self.f1},
            {'gid': 2, 'geometry': self.f2}
            ])

    def tearDown(self):
        pass

    def __plot2D(self, result, title):
        unitDisc = self.vpGdf.copy(deep=True)
        unitDisc.geometry = unitDisc.geometry.apply(lambda g: g.buffer(1.0)) 

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        ax.set_title(f'Projection: {title}', fontsize=20)
        result.plot(ax=ax, color='red')
        self.vpGdf.plot(ax=ax, color='black')
        unitDisc.boundary.plot(ax=ax, color='black')
        plt.show()
        plt.close(fig)

    def __plot3D(self):
        scene = ToUnstructuredGrid([self.facesGdf, self.vpGdf], fieldname='gid').run()

        plotter = Plotter(window_size=(1000, 800), title='Vue 3D')
        plotter.add_mesh(scene, scalars='gid', cmap='gist_earth',
            show_edges=True, show_scalar_bar=True, point_size=20.0,
            render_points_as_spheres=True, line_width=2.0, color='k')
        # plotter.add_point_labels(centroids, labels, font_size=20, point_size=1e-3)
        plotter.camera_position = 'xz'
        _ = plotter.add_axes(line_width=5, labels_off=False)
        plotter.show()

    def testRun1(self):
        prF1 = SphericalProjectionLib.orthogonal(self.vp, self.f1, npts=51)
        prF2 = SphericalProjectionLib.orthogonal(self.vp, self.f2, npts=51)

        resultGdf = GeoDataFrame(data=[
            {'gid': 1, 'geometry': prF1},
            {'gid': 2, 'geometry': prF2}
            ])
        self.__plot3D()
        self.__plot2D(resultGdf, 'orthogonal')

    def testRun2(self):
        prF1 = SphericalProjectionLib.stereographic(self.vp, self.f1, npts=51)
        prF2 = SphericalProjectionLib.stereographic(self.vp, self.f2, npts=51)

        resultGdf = GeoDataFrame(data=[
            {'gid': 1, 'geometry': prF1},
            {'gid': 2, 'geometry': prF2}
            ])
        # self.__plot3D()
        self.__plot2D(resultGdf, 'stereographic')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
