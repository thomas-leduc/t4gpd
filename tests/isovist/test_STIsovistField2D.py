'''
Created on 17 juin 2020

@author: tleduc
'''
import unittest

from geopandas import GeoDataFrame
from numpy import pi
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.wkt import loads
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.isovist.STIsovistField2D import STIsovistField2D
from t4gpd.isovist.STIsovistField2D_new import STIsovistField2D_new
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STPointsDensifier2 import STPointsDensifier2


class STIsovistField2DTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoints = STGrid(
            self.buildings, 50, dy=None, indoor=False, intoPoint=True).run()

    def tearDown(self):
        self.buildings = None
        self.viewpoints = None

    def __plot(self, buildings, sensors, isovField, isovRaysField):
        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        buildings.boundary.plot(ax=basemap, color="grey",
                                edgecolor="grey", hatch="/")
        sensors.plot(ax=basemap, color="black")
        isovField.plot(ax=basemap, color="yellow", alpha=0.4)
        isovRaysField.plot(ax=basemap, color="black", linewidth=0.4)
        plt.show()
        plt.close(fig)

    def testRun1(self):
        nRays, rayLength = 64, 20.0
        isovRaysField, isovField = STIsovistField2D(
            self.buildings, self.viewpoints, nRays, rayLength).run()

        for result in [isovRaysField, isovField]:
            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(result.crs, self.buildings.crs, "Verify CRS")
            self.assertEqual(15, len(result), "Count rows")
            self.assertEqual(2 + len(self.viewpoints.columns),
                             len(result.columns), 'Count columns')

        approxRayLength = rayLength + 1e-6
        for _, row in isovRaysField.iterrows():
            self.assertIsInstance(
                row.geometry, MultiLineString, 'Is a GeoDataFrame of MultiLineString')
            self.assertEqual(0, row['indoor'], 'indoor attribute values')
            self.assertEqual(nRays, len(row.geometry.geoms),
                             'Verify number of rays')
            self.assertTrue(all(
                [0 <= g.length <= approxRayLength for g in row.geometry.geoms]), 'Verify ray lengths')
            self.assertIsInstance(
                loads(row['viewpoint']), Point, 'Test viewpoint attribute')
            self.assertIsInstance(
                loads(row['vect_drift']), LineString, 'Test vect_drift attribute')
            self.assertEqual(loads(row['viewpoint']).coords[0], loads(row['vect_drift']).coords[0],
                             'Test viewpoint and vect_drift attribute values')

        for _, row in isovField.iterrows():
            self.assertIsInstance(row.geometry, Polygon,
                                  'Is a GeoDataFrame of Polygon')
            self.assertEqual(0, row['indoor'], 'indoor attribute values')
            self.assertTrue(0 <= row.geometry.area <= pi *
                            rayLength ** 2, 'Verify isovist field areas')
            self.assertIsInstance(
                loads(row['viewpoint']), Point, 'Test viewpoint attribute')
            self.assertIsInstance(
                loads(row['vect_drift']), LineString, 'Test vect_drift attribute')
            self.assertEqual(loads(row['viewpoint']).coords[0], loads(row['vect_drift']).coords[0],
                             'Test viewpoint and vect_drift attribute values')

        # self.__plot(self.buildings, self.viewpoints, isovField, isovRaysField)

    def testRun2(self):
        nlines, ncols = 2, 2
        bdx, bdy = 50, 50  # building size
        sdx, sdy = 10, 20  # street widths
        buildings = GeoDataFrameDemos.regularGridOfPlots2(
            nlines, ncols, bdx, bdy, sdx, sdy)

        sensors = STPointsDensifier2(
            buildings, curvAbsc=[0.5], pathidFieldname=None).run()

        nRays, rayLength = 64, 20.0
        isovRaysField, isovField = STIsovistField2D(
            buildings, sensors, nRays, rayLength).run()

        for result in [isovRaysField, isovField]:
            self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(result.crs, buildings.crs, "Verify CRS")
            self.assertEqual(16, len(result), "Count rows")
            self.assertEqual(2 + len(sensors.columns),
                             len(result.columns), 'Count columns')

        # self.__plot(buildings, sensors, isovField, isovRaysField)

    def testRun3(self):
        buildings = GeoDataFrame([
            {'geometry': loads(
                'POLYGON ((50 80, 60 80, 60 70, 50 70, 50 80))')},
            {'geometry': loads(
                'POLYGON ((0 100, 10 100, 10 10, 90 10, 90 30, 60 30, 60 60, 70 60, 70 40, 90 40, 90 90, 80 90, 80 80, 70 80, 70 90, 30 90, 30 50, 20 50, 20 100, 100 100, 100 0, 0 0, 0 100))')},
        ])
        for x, y in [(30, 80), (40, 70), (60, 70)]:
            sensors = GeoDataFrame([
                {'geometry': loads(f'POINT ({x} {y})')},
            ])

            nRays, rayLength = 64, 100.0
            isovRaysField, isovField = STIsovistField2D(
                buildings, sensors, nRays, rayLength).run()

            for result in [isovRaysField, isovField]:
                self.assertIsInstance(
                    result, GeoDataFrame, "Is a GeoDataFrame")
                self.assertEqual(result.crs, buildings.crs, "Verify CRS")
                self.assertEqual(1, len(result), "Count rows")
                self.assertEqual(3, len(result.columns), 'Count columns')

            # self.__plot(buildings, sensors, isovField, isovRaysField)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
