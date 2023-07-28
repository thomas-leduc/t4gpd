'''
Created on 17 fevr. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

from t4gpd.morph.STBBox import STBBox


class STBBoxTest(unittest.TestCase):


    def setUp(self):
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()


    def tearDown(self):
        pass


    def testRun(self):
        result = STBBox(self.buildings, buffDist=-100.0).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(1, len(result.columns), 'Count columns')

        geom = result.geometry.squeeze()
        self.assertEqual('Polygon', geom.geom_type, 'Is a Polygon')
        self.assertEqual(5, len(geom.exterior.coords), 'Is a rectangle')

        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.buildings.plot(ax=ax, color='lightgrey')
        result.boundary.plot(ax=ax, color='red')
        plt.show()
        plt.close(fig)
        """


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()