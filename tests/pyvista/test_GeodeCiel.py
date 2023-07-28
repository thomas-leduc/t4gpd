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
import unittest

from geopandas.geodataframe import GeoDataFrame

from t4gpd.pyvista.GeodeCiel import GeodeCiel


class GeodeCielTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun(self):
        result = GeodeCiel(norecursions=3, radius=None).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(512, len(result), 'Count rows')
        self.assertEqual(1, len(result.columns), 'Count columns')

        '''
        import matplotlib.pyplot as plt
        result.boundary.plot()
        plt.show()

        from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
        scene = ToUnstructuredGrid([result]).run()
        scene.plot(show_edges=False)
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
