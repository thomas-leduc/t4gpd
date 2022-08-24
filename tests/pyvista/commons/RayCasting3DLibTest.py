'''
Created on 20 juil. 2022

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

from numpy import asarray, dot, ndarray

from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.commons.RayCasting3DLib import RayCasting3DLib


class RayCasting3DLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testFromNCellsToThetaPhi(self):
        n_cells = 1024
        theta, phi, ncells = RayCasting3DLib.fromNCellsToThetaPhi(n_cells)
        self.assertEqual(32, theta, 'Test the theta-value')
        self.assertEqual(18, phi, 'Test the phi-value')
        self.assertEqual(n_cells, ncells, 'Test the ncells-value')
        
    def testFromThetaPhiToNCells(self):
        theta, phi = 32, 18
        ncells = RayCasting3DLib.fromThetaPhiToNCells(theta, phi)
        self.assertEqual(1024, ncells, 'Test the ncells-value')

    def testPrepareOrientedRandomRays1(self):
        nrays, normal_vec = 50, [0, 1, 0]
        result = RayCasting3DLib.prepareOrientedRandomRays(nrays, normal_vec, openness=2)

        self.assertIsInstance(result, ndarray, 'Test the return type')
        self.assertEqual(nrays, len(result), 'Test the length of the return list')
        self.assertEqual(3 * nrays, len(asarray(result).reshape(-1)), 'Test the length of the return list (2)')
        for nv in result:
            self.assertAlmostEqual(1, dot(normal_vec, nv), None, 'msg', 1e-1)

    def testPrepareOrientedRandomRays2(self):
        nrays1, nrays2, dfs = 1000, 400, []

        for i, nv in enumerate([ [], [1, 0, 0], [0, 1, 0], [1, 1, 1], [0, 0, 1]]):
            if (0 == i):
                rays = RayCasting3DLib.preparePanopticRandomRays(nrays1)
            else:
                rays = RayCasting3DLib.prepareOrientedRandomRays(nrays2, nv, openness=8)
            df = RayCasting3DLib.intoGeoDataFrame(rays)
            df['attr'] = i
            dfs.append(df)

        scene = ToUnstructuredGrid(dfs, 'attr').run()
        scene.plot()

    def testPreparePanopticRays(self):
        nrays = 8

        result = RayCasting3DLib.preparePanopticRays(nrays, method='geodeciel')
        self.assertIsInstance(result, ndarray, 'Test the return type')
        self.assertEqual(nrays, len(result), 'Test the length of the return list')
        self.assertEqual(3 * nrays, len(asarray(result).reshape(-1)), 'Test the length of the return list (2)')

        for i, x in enumerate(asarray(result).reshape(-1)):
            self.assertAlmostEqual(1 / 3, abs(x), None,
                                   f'Test the {i} value of the return list', 1e-6)
        '''
        rays = RayCasting3DLib.intoGeoDataFrame(result)
        norecursions = GeodeCiel.fromNRaysToNRecursions(nrays)
        ciel = GeodeCiel(norecursions).run()
        scene = ToUnstructuredGrid([ciel, rays]).run()
        scene.plot(show_edges=False, opacity=0.99)
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
