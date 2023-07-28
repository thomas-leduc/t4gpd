'''
Created on 23 nov. 2020

@author: tleduc
'''
from shapely.affinity import translate
import unittest

from geopandas.geodataframe import GeoDataFrame
from numpy import pi
from shapely.geometry import Point, Polygon
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

from t4gpd.morph.geoProcesses.SkyMap2D import SkyMap2D


class SkyMap2DTest(unittest.TestCase):

    def setUp(self):
        dx, dy, h = 10, 100, 10 
        bar = Polygon([(0, 0), (dx, 0), (dx, dy), (0, dy), (0, 0)])
        bar1, bar2, bar3, bar4 = Polygon(bar), Polygon(bar), Polygon(bar), Polygon(bar)
        bar1 = translate(bar1, xoff=h / 2.0, yoff=h / 2.0)
        bar2 = translate(bar2, xoff=-dx - h / 2.0, yoff=h / 2.0)
        bar3 = translate(bar3, xoff=-dx - h / 2.0, yoff=-dy - h / 2.0)
        bar4 = translate(bar4, xoff=h / 2.0, yoff=-dy - h / 2.0)

        self.buildings = GeoDataFrame([
            {'geometry': bar1, 'HAUTEUR': h},
            {'geometry': bar2, 'HAUTEUR': h},
            {'geometry': bar3, 'HAUTEUR': h},
            {'geometry': bar4, 'HAUTEUR': h},
            ])
        self.viewpoints = GeoDataFrame([
            { 'gid': 1, 'geometry': Point((0, 0)) },
            { 'gid': 2, 'geometry': Point((0, dy / 2.0)) },
            { 'gid': 3, 'geometry': Point((0, dy + h / 2.0)) },
            { 'gid': 4, 'geometry': Point((dx + h / 2.0, 0)) }
            ])

    def tearDown(self):
        pass

    def testRunWithArgs(self):
        nRays, size, maxRayLen = 180, 4.0, 100.0
        skymapOp = SkyMap2D(self.buildings, nRays, size, maxRayLen, elevationFieldname='HAUTEUR')
        result = STGeoProcess(skymapOp, self.viewpoints).run() 

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(4, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertLessEqual(row.geometry.area, pi * size * size, 'Areas test')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=basemap, color='grey')
        result.plot(ax=basemap, color='black')
        self.viewpoints.plot(ax=basemap, marker='+', color='black')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
