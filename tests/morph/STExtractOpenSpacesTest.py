'''
Created on 14 dec. 2020

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

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import box, MultiPolygon, Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STExtractOpenSpaces import STExtractOpenSpaces


class STExtractOpenSpacesTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

        roi = box(*self.buildings.buffer(10.0).total_bounds)
        self.envelope = GeoDataFrame([{'geometry': roi}], crs=self.buildings.crs)

    def tearDown(self):
        pass

    def testRun1(self):
        result = STExtractOpenSpaces(self.envelope, self.buildings, removeCourtyards=False).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(1, len(result.columns), 'Count columns')

        buildingsArea = sum(self.buildings.area)
        envelopeArea = self.envelope.area.squeeze()
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiPolygon, 'Is a GeoDataFrame of MultiPolygon')
            self.assertLess(row.geometry.area, envelopeArea, 'Test area (1)')
            self.assertAlmostEqual(row.geometry.area, envelopeArea - buildingsArea, 1, 'Test area (2)')

    def testRun2(self):
        result = STExtractOpenSpaces(self.envelope, self.buildings, removeCourtyards=True).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(1, len(result.columns), 'Count columns')

        buildingsArea = sum(self.buildings.area)
        envelopeArea = self.envelope.area.squeeze()
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygonq')
            self.assertLess(row.geometry.area, envelopeArea, 'Test area (1)')
            self.assertLess(row.geometry.area, envelopeArea - buildingsArea, 'Test area (2)')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.envelope.boundary.plot(ax=basemap, color='red')
        self.buildings.plot(ax=basemap, color='blue', hatch='XX', alpha=0.5)
        result.plot(ax=basemap, color='grey', alpha=0.5)
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
