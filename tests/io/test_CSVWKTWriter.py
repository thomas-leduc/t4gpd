'''
Created on 30 sept. 2020

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
from os import getpid
import tempfile
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point
from t4gpd.io.CSVWKTReader import CSVWKTReader
from t4gpd.io.CSVWKTWriter import CSVWKTWriter


class CSVWKTWriterTest(unittest.TestCase):

    def setUp(self):
        self.rows = [
            {'gid':1, 'myattr': 1.11, 'geometry': Point((0, 0))},
            {'gid':2, 'myattr': 2.22, 'geometry': Point((0, 0))},
            {'gid':3, 'myattr': 3.33, 'geometry': Point((0, 0))},
            ]
        self.inputGdf = GeoDataFrame(self.rows)

    def tearDown(self):
        pass

    def testRun(self):
        fieldSep, decimalSep = '::', ','

        with tempfile.TemporaryDirectory() as tmpdir:
            outputFile = '%s/_%d.csv' % (tmpdir, getpid())

            CSVWKTWriter(self.inputGdf, outputFile, fieldSep, decimalSep).run()
            newGdf = CSVWKTReader(outputFile, 'the_geom', fieldSep, decimalSep=decimalSep).run()

            for i, newRow in newGdf.iterrows():
                self.assertEqual(self.rows[i]['gid'], newRow['gid'], 'Test gid attribute values') 
                self.assertEqual(self.rows[i]['myattr'], newRow['myattr'], 'Test myattr attribute values') 
                self.assertEqual(self.rows[i]['geometry'], newRow['geometry'], 'Test geometry values') 


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
