'''
Created on 22 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from pandas import merge
from shapely.geometry import MultiLineString
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STCrossroadsGeneration import STCrossroadsGeneration
from t4gpd.morph.geoProcesses.CrossroadRecognition import CrossroadRecognition
from t4gpd.graph.STToRoadsSectionsNodes import STToRoadsSectionsNodes
from t4gpd.isovist.STIsovistField2D import STIsovistField2D
from t4gpd.morph.geoProcesses.AngularAbscissa import AngularAbscissa
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyplot.MultipleMarkerStyles import MultipleMarkerStyles

import matplotlib.pyplot as plt


class CrossroadRecognitionTest(unittest.TestCase):

    def setUp(self):
        nbranchs, streetWidth = 4, 10.0
        self.nRays, self.rayLength = 64, 100.0
        
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.roads = GeoDataFrameDemos.ensaNantesRoads()
        self.viewpoints = STToRoadsSectionsNodes(self.roads).run()
        self.viewpoints = self.viewpoints[ self.viewpoints.gid.isin([7, 74]) ]
        self.isovRays, _ = STIsovistField2D(self.buildings, self.viewpoints, self.nRays, self.rayLength).run()

        self.patterns = STCrossroadsGeneration(nbranchs, self.rayLength, streetWidth,
                                               mirror=False, withBranchs=True, withSectors=True,
                                               crs='EPSG:2154', magnitude=2.5).run()
        self.pattRays = STGeoProcess(AngularAbscissa(self.patterns, 'vpoint_x',
                                                     'vpoint_y', self.nRays), self.patterns).run()

    def tearDown(self):
        pass

    def _check(self, result, recFieldname, pattIds):
        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(result.crs, self.buildings.crs, 'Verify CRS')
        self.assertEqual(2, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiLineString, 'Is a GeoDataFrame of MultiLineString')
            self.assertIn(row[recFieldname], pattIds, f'Test {recFieldname} attr. value')

    def _plot(self, result, recFieldname):
        fig, axes = plt.subplots(nrows=1, ncols=2, squeeze=False, figsize=(2 * 8.26, 1 * 8.26))

        ax = axes[0, 0]
        self.patterns.plot(ax=ax, color='lightgrey')
        self.patterns.apply(lambda x: ax.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0][0:2],
            color='black', size=14, ha='center'), axis=1);
        ax.axis('off')

        ax = axes[0, 1]
        ax.set_title(recFieldname, fontsize=20)
        self.buildings.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=0.3)
        self.roads.plot(ax=ax, color='darkgrey', linewidth=0.7)
        self.isovRays.plot(ax=ax, color='blue', linewidth=0.1)
        self.viewpoints.plot(ax=ax, color='black')
        ax.axis('off')
        vp = merge(self.viewpoints[['gid', 'geometry']], result[['gid', recFieldname]], on='gid')
        
        vp.apply(lambda x: ax.annotate(
            text=f'{x.gid}:: (pattId={x[recFieldname]})', xy=x.geometry.coords[0][0:2],
            color='black', size=14, ha='center'), axis=1);

        if ('recId_fwt' == recFieldname):
            MultipleMarkerStyles(result, patterns=self.patterns,
                                 left_on=recFieldname, right_on='gid',
                                 rotation='rotation', basemap=ax,
                                 marker_color='red', marker_size=4000,
                                 alpha=0.71).run()
        plt.show()
        plt.close(fig)

    def testRunFFT(self):
        recognEngine = CrossroadRecognition('FFT', self.pattRays, 'gid', self.nRays, self.rayLength)
        result = STGeoProcess(recognEngine, self.isovRays).run()
        print(self.viewpoints.columns, result.columns)
        self._check(result, 'recId_fft', [-21])
        self._plot(result, 'recId_fft')

    def testRunMeanAngularity(self):
        recognEngine = CrossroadRecognition('MeanAngularity', self.pattRays, 'gid', self.nRays, self.rayLength)
        result = STGeoProcess(recognEngine, self.isovRays).run()
        self._check(result, 'recId_avgA', [-21, 20])

        for _, row in result.iterrows():
            if 7 == row['gid']:
                expectedPatternId = -21
            elif 74 == row['gid']:
                expectedPatternId = 20
            self.assertEqual(expectedPatternId, row['recId_avgA'], 'Pattern ID recognition')
        self._plot(result, 'recId_avgA')

    def testRunMeanVector(self):
        recognEngine = CrossroadRecognition('MeanVector', self.pattRays, 'gid', self.nRays, self.rayLength)
        result = STGeoProcess(recognEngine, self.isovRays).run()
        self._check(result, 'recId_avgV', [-21])
        self._plot(result, 'recId_avgV')

    def testRunFWT(self):
        recognEngine = CrossroadRecognition('FWT', self.pattRays, 'gid', self.nRays, self.rayLength)
        result = STGeoProcess(recognEngine, self.isovRays).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(result.crs, self.buildings.crs, 'Verify CRS')
        self.assertEqual(2, len(result), 'Count rows')
        self.assertEqual(8, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiLineString, 'Is a GeoDataFrame of MultiLineString')
            self.assertEqual(-21, row['recId_fwt'], 'Pattern ID recognition')
        self._plot(result, 'recId_fwt')
        # result.to_file('/tmp/xxx.shp')


if __name__ == '__main__':
    # import sys;sys.argv = ['', 'Test.testRun']
    unittest.main()
