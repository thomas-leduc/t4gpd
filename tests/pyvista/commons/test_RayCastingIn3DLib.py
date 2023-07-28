'''
Created on 5 juin 2022

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
from pyvista import global_theme
from shapely.geometry import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.FootprintExtruder import FootprintExtruder
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.commons.RayCastingIn3DLib import RayCastingIn3DLib


class RayCastingIn3DLibTest(unittest.TestCase):

    def setUp(self):
        seed(0)
        buildings = GeoDataFrameDemos.regularGridOfPlots(3, 4, dw=5.0)
        buildings['HAUTEUR'] = 3.0 * randint(2, 7, size=len(buildings))

        '''
        import matplotlib.pyplot as plt
        _, ax = plt.subplots(figsize=(0.5 * 8.26, 0.5 * 8.26))
        buildings.plot(ax=ax)
        buildings.apply(lambda x: ax.annotate(
            text=x.HAUTEUR, xy=x.geometry.centroid.coords[0],
            color='black', size=12, ha='center'), axis=1)
        plt.show()
        '''

        op = FootprintExtruder(buildings, 'HAUTEUR', forceZCoordToZero=True)
        self.buildingsIn3d = STGeoProcess(op, buildings).run()

        self.viewpoint = GeoDataFrame([{'geometry': Point([0, 0, 4.5])}])

    def tearDown(self):
        pass

    def testAreCovisibleObbTree(self):
        self.buildingsIn3d = self.buildingsIn3d.explode(ignore_index=True)

        obbTree = RayCastingIn3DLib.prepareVtkOBBTree(self.buildingsIn3d)

        epsilon = 1e-3
        TRIOS = [
            ([-25, -15, 18], [25, 15, 18], True),
            ([-25, -15, 15 + epsilon], [25, 15, 15 + epsilon], True),
            ([-25, -15, 15], [25, 15, 15], False),
            ([-25, -15, 15], [15, 5, 15], False),
            ([-35, -25, 17], [-25, -15, 17], True),  # INDOOR COVISIBILITY!
            ]
        for srcPt, dstPt, expected in TRIOS:
            actual = RayCastingIn3DLib.areCovisibleObbTree(obbTree, srcPt, dstPt)
            self.assertEqual(actual, expected, f'covisible ( {srcPt} and {srcPt} ) = {actual}')
        '''
        op = FromContourToNormalVector(magn=3.0)
        nvect = STGeoProcess(op, self.buildingsIn3d).run()

        scene = ToUnstructuredGrid([self.buildingsIn3d, nvect]).run()
        scene.plot(show_edges=True)
        '''

    def testMraycast2DToGeoDataFrame(self):
        global_theme.background = 'grey'
        global_theme.axes.show = True

        rays = RayCastingIn3DLib.mraycast2DToGeoDataFrame(
            [self.buildingsIn3d], self.viewpoint.geometry.squeeze(), nRays=36, crs=None)

        result = ToUnstructuredGrid([self.buildingsIn3d, rays, self.viewpoint], 'HAUTEUR').run()
        result.plot(scalars='HAUTEUR', cmap='gist_earth', show_edges=False, cpos='xy', opacity=0.99,
                    show_scalar_bar=True, point_size=15.0, render_points_as_spheres=True)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
