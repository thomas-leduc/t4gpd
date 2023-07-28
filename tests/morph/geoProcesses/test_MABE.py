'''
Created on 23 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Polygon
from shapely.wkt import loads
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STToRoadsSectionsNodes import STToRoadsSectionsNodes
from t4gpd.isovist.STIsovistField2D import STIsovistField2D
from t4gpd.morph.geoProcesses.MABE import MABE
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class MABETest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun1(self):
        inputWktStrings = [
            # TRI
            'POLYGON ((0 0, 10 0, 10 10, 5 15, 0 10, -5 5, 0 0))',
            # TRAPEZ
            'POLYGON ((7 6, 9 8, 7 12, 3 8, 7 6))',
            # PARALLELOGRAM
            'POLYGON ((7 6, 9 8, 5 10, 3 8, 7 6))',
            # SQUARE
            'POLYGON ((1 1, 1 6, 6 6, 6 1, 1 1))',
            # MISC
            'MULTIPOINT ((20 40), (40 50), (30 60), (50 70), (40 60), (50 60), (60 70), (65 77), (80 80), (90 90), (105 97), (120 100), (133 115), (120 120), (100 110), (90 100), (75 89))'
            'MULTIPOINT ((440 140), (260 100), (190 200), (130 330), (280 280), (310 190), (400 290), (220 110), (350 150), (355 199), (400 220), (380 180), (390 140), (350 130), (320 120), (350 110), (380 120), (450 160), (440 190), (440 200), (470 180))' 
            'MULTIPOINT ((-1 -1), (-1 1), (1 -1), (1.4142135623730951 0))'
            'MULTIPOINT ((-1 -1), (-1 1), (1 -1), (0 1.4142135623730951))'
            'POLYGON ((20 0, 6.18034 4.75528, -16.1803 2.93893, -16.1803 -2.93893, 6.18034 -4.75528, 20 0))'
            ]

        for wkt in inputWktStrings:
            inputGeom = loads(wkt)
            inputGdf = GeoDataFrame([ {'gid':1, 'geometry':inputGeom} ], crs='EPSG:2154')

            mabe = MABE()
            result = STGeoProcess(mabe, inputGdf).run()
            
            self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
            self.assertEqual(1, len(result), 'Count rows')
            self.assertEqual(9, len(result.columns), 'Count columns')

            for _, row in result.iterrows():
                currGeom = row.geometry
                self.assertIsInstance(currGeom, Polygon, 'Is a GeoDataFrame of Polygons')
                self.assertLessEqual(inputGeom.area, currGeom.area, 'Areas test')
                self.assertLessEqual(currGeom.length, row['mabe_perim'], 'Perimeters test')
                self.assertTrue(inputGeom.within(currGeom.buffer(0.125)), 'Within test')

    def testRun2(self):
        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        roads = GeoDataFrameDemos.ensaNantesRoads()
        viewpoints = STToRoadsSectionsNodes(roads).run()
        viewpoints = viewpoints.query('gid == 15')
        nRays, rayLength = 64, 100.0
        isovRays, _ = STIsovistField2D(buildings, viewpoints, nRays, rayLength).run()

        mabe = MABE()
        result = STGeoProcess(mabe, isovRays).run()
        
        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(12, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            currGeom = row.geometry
            self.assertIsInstance(currGeom, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertLessEqual(currGeom.area, row['mabe_area'], 'Areas test')
            self.assertLessEqual(currGeom.length, row['mabe_perim'], 'Perimeters test')
            # self.assertTrue(inputGeom.within(currGeom.buffer(0.125)), 'Within test')

        '''
        import matplotlib.pyplot as plt
        basemap = buildings.plot(color='lightgrey', edgecolor='dimgrey', linewidth=0.3)
        roads.plot(ax=basemap, edgecolor='black', linewidth=0.3)
        viewpoints.plot(ax=basemap)
        isovRays.plot(ax=basemap, color='red', linewidth=0.6)
        result.boundary.plot(ax=basemap, color='blue')
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRun']
    unittest.main()
