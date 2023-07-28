'''
Created on 23 mars 2023

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

from numpy import sqrt
from numpy.random import default_rng
from pandas import DataFrame

from t4gpd.misc.OptimalNumberOfClusters import OptimalNumberOfClusters


class OptimalNumberOfClustersTest(unittest.TestCase):

    def setUp(self):
        rng = default_rng(1234)  # seeds is set to 1234!
        
        # CREATE THE DATASET
        npts, centers = 100, [(0, 0), (1 / 2, sqrt(3) / 2), (-1 / 2, sqrt(3) / 2)]
        idx = rng.integers(0, len(centers), size=npts)
        self.df = DataFrame([{
            "X1": centers[i][0],
            "X2": centers[i][1],
            "groupe": chr(ord("A") + i)
            } for i in idx])

        # NOISING THE DATA
        columns = ["X1", "X2"]
        groupes = self.df.groupe
        self.df = DataFrame(
            data=rng.normal(loc=self.df[columns].to_numpy(), scale=0.1),
            columns=columns
            )
        self.df["groupe"] = groupes
        self.nclusters = len(centers)

    def tearDown(self):
        pass

    def testRun(self):
        for method in ["elbow", "silhouette", "bic", "dendrogram"]:
            actual = OptimalNumberOfClusters(self.df, method=method, maxNumber=10, verbose=False).run()
            self.assertIsInstance(actual, DataFrame, f"Is a DataFrame test ({method})")
            self.assertEqual(self.nclusters, actual.nclusters.squeeze(), f"Test nclusters value ({method})")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
