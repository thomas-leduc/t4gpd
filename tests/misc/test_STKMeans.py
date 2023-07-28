'''
Created on 5 janv. 2021

@author: tleduc

Copyright 2020 Thomas Leduc

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

from numpy.random import default_rng
from pandas import DataFrame
from t4gpd.misc.STKMeans import STKMeans


class STKMeansTest(unittest.TestCase):

    def setUp(self):
        npts, pairs = 30, [(0, 0), (1, 0), (0, 1)]
        
        rng = default_rng(1234)  # seeds is set to 1234!
        rints = rng.integers(low=0, high=len(pairs), size=npts)
        self.inputGdf = DataFrame([{"X": pairs[i][0], "Y": pairs[i][1], "Groupe": f"g{i}"}
                                   for i in rints])
        self.inputGdf["X"] = rng.normal(loc=self.inputGdf.X, scale=0.2)
        self.inputGdf["Y"] = rng.normal(loc=self.inputGdf.Y, scale=0.2)

    def tearDown(self):
        pass

    def testRun(self):
        nclusters = 3
        result = STKMeans(self.inputGdf, nclusters, verbose=True).run()

        self.assertIsInstance(result, DataFrame, "Is a DataFrame")
        self.assertEqual(len(self.inputGdf), len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row["kmeans_lbl"], int, "Test 'kmeans_lbl' attribute values")
            self.assertIn(row["kmeans_lbl"], range(nclusters), "Test 'kmeans_lbl' attribute values")

        '''
        import matplotlib.pyplot as plt
        from geopandas import GeoDataFrame
        
        result["geometry"] = result.apply(lambda row: Point(row.X, row.Y), axis=1)
        result = GeoDataFrame(result, crs="epsg:2154")
        result.plot(column="kmeans_lbl")
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
