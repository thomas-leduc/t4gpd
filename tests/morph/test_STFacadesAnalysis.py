'''
Created on 2 avr. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from shapely.geometry.linestring import LineString
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

from t4gpd.morph.STFacadesAnalysis import STFacadesAnalysis
from t4gpd.commons.AngleLib import AngleLib
from shapely.wkt import loads
from t4gpd.commons.GeomLib import GeomLib


class STFacadesAnalysisTest(unittest.TestCase):

    def setUp(self):
        self.building = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        pass

    def testRun1(self):
        result = STFacadesAnalysis(self.building, gidFieldname=None,
                                   elevationFieldname=None, exteriorOnly=True).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(131, len(result), 'Count rows')
        self.assertEqual(8, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')
            self.assertIsNone(row.buildingID, 'Test buildingID attribute value')
            self.assertIsNone(row.height, 'Test height attribute value')
            self.assertTrue(0 <= row.azimuth < 360, 'Test azimuth attribute value')
            self.assertIsNone(row.surface, 'Test surface attribute value')
            self.assertTrue(0 <= row.gid < len(result), 'Test gid attribute value')

            _normal = loads(row.normal)
            _normal = GeomLib.vector_to(*_normal.coords)
            self.assertAlmostEqual(
                row.azimuth, AngleLib.toDegrees(
                AngleLib.normAzimuth(_normal)), None,
                'Test azimuth attribute value (2)', 1e-6)

    def testRun2(self):
        result = STFacadesAnalysis(self.building).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(131, len(result), 'Count rows')
        self.assertEqual(8, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')
            self.assertEqual('BATIMENT0000000302909608', row.buildingID, 'Test buildingID attribute value')
            self.assertEqual(4.1, row.height, 'Test height attribute value')
            self.assertTrue(0 <= row.azimuth < 360, 'Test azimuth attribute value')
            self.assertEqual(row.surface, row.length * row.height, 'Test surface attribute value')
            self.assertTrue(0 <= row.gid < len(result), 'Test gid attribute value')

            _normal = loads(row.normal)
            _normal = GeomLib.vector_to(*_normal.coords)
            self.assertAlmostEqual(
                row.azimuth, AngleLib.toDegrees(
                AngleLib.normAzimuth(_normal)), None,
                'Test azimuth attribute value (2)', 1e-6)

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.building.plot(ax=basemap, color='grey')
        result.plot(ax=basemap, column='azimuth', linewidth=5, legend=True)
        basemap.axis('off')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
