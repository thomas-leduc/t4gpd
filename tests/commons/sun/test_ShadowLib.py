'''
Created on 21 avr. 2021

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

from numpy import cos, pi, sin, sqrt
from shapely.geometry import CAP_STYLE, Point, Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.sun.ShadowLib import ShadowLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class ShadowLibTest(unittest.TestCase):

    def setUp(self):
        self.polygon = Point((0.5, 0.5)).buffer(0.5, cap_style=CAP_STYLE.square)
        self.polygonWithHole = Point((0.5, 0.5)).buffer(0.6, cap_style=CAP_STYLE.square)
        self.polygonWithHole = self.polygonWithHole.difference(self.polygon)

        self.trees = GeoDataFrameDemos.districtGraslinInNantesTrees()
        self.trees = self.trees[self.trees.osm_id == 1961183678]
        self.treePosition = self.trees.geometry.squeeze()

    def tearDown(self):
        pass

    def __fromAltiAzimToRadDir(self, alti, azim):
        x = cos(alti) * cos(azim)
        y = cos(alti) * sin(azim)
        z = sin(alti)
        return [x, y, z]

    def testProjectBuildingOntoShadowPlane1(self):
        # alti, azim = 45, 270
        # x, y, z = 0, -1 / sqrt(2), 1 / sqrt(2)
        alti, azim = pi / 4, 3 * pi / 2
        radDir = self.__fromAltiAzimToRadDir(alti, azim)

        result = ShadowLib.projectBuildingOntoShadowPlane(
            self.polygon, occluderElevation=1.0, radDir=radDir,
            altitudeOfShadowPlane=0.0)

        self.assertIsInstance(result, Polygon, 'Is a Polygon')
        self.assertAlmostEqual(2, result.area, None, 'Test area', 1e-3)

        '''
        import matplotlib.pyplot as plt
        from geopandas.geodataframe import GeoDataFrame

        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        inputPolygon = GeoDataFrame([{'geometry': self.polygon}])
        outputPolygon = GeoDataFrame([{'geometry': result}])
        inputPolygon.plot(ax=basemap, color='lightgrey')
        outputPolygon.boundary.plot(ax=basemap, color='dimgrey')
        plt.show()
        '''

    def testProjectBuildingOntoShadowPlane2(self):
        # alti, azim = 45, 315
        alti, azim = pi / 4, 7 * pi / 4
        radDir = self.__fromAltiAzimToRadDir(alti, azim)

        result = ShadowLib.projectBuildingOntoShadowPlane(
            self.polygon, occluderElevation=1.0, radDir=radDir,
            altitudeOfShadowPlane=0.0)

        self.assertIsInstance(result, Polygon, 'Is a Polygon')
        self.assertAlmostEqual(1 + sqrt(2), result.area, None, 'Test area', 1e-3)

        '''
        import matplotlib.pyplot as plt
        from geopandas.geodataframe import GeoDataFrame

        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        inputPolygon = GeoDataFrame([{'geometry': self.polygon}], crs='epsg:2154')
        outputPolygon = GeoDataFrame([{'geometry': result}], crs='epsg:2154')
        inputPolygon.plot(ax=basemap, color='lightgrey')
        outputPolygon.boundary.plot(ax=basemap, color='dimgrey')
        plt.show()
        '''

    def testProjectBuildingOntoShadowPlane3(self):
        # alti, azim = 45, 315
        alti, azim = pi / 4, 7 * pi / 4
        radDir = self.__fromAltiAzimToRadDir(alti, azim)

        result = ShadowLib.projectBuildingOntoShadowPlane(
            self.polygonWithHole, occluderElevation=1.0, radDir=radDir,
            altitudeOfShadowPlane=0.0)

        self.assertIsInstance(result, Polygon, 'Is a Polygon')
        self.assertTrue(GeomLib.isHoled(result), 'Test is holed')
        _area = sqrt(2 * 1.2 ** 2) + (1.2 ** 2) - (1 - 1 / sqrt(2)) ** 2
        self.assertAlmostEqual(_area, result.area, None, 'Test area', 1e-3)

        '''
        import matplotlib.pyplot as plt
        from geopandas.geodataframe import GeoDataFrame

        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        inputPolygon = GeoDataFrame([{'geometry': self.polygonWithHole}], crs='epsg:2154')
        outputPolygon = GeoDataFrame([{'geometry': result}], crs='epsg:2154')
        inputPolygon.plot(ax=basemap, color='lightgrey')
        outputPolygon.boundary.plot(ax=basemap, color='dimgrey')
        plt.show()
        '''

    def testProjectSphericalTreeOntoShadowPlane1(self):
        # alti, azim = 90, 270
        alti, azim = pi / 2, 3 * pi / 2
        radDir = self.__fromAltiAzimToRadDir(alti, azim)

        treeCrownRadius = 3.0

        result = ShadowLib.projectSphericalTreeOntoShadowPlane(
            self.treePosition, treeHeight=9.0, treeCrownRadius=treeCrownRadius, treeTrunkRadius=None,
            radDir=radDir, solarAlti=alti, solarAzim=azim, altitudeOfShadowPlane=0, npoints=32)

        self.assertIsInstance(result, Polygon, 'Is a Polygon')
        self.assertAlmostEqual(pi * treeCrownRadius ** 2, result.area, None, 'Test area', 0.3)
        self.assertLess(self.treePosition.distance(result.centroid), 0.1, 'Test shadow centroid')

        '''
        import matplotlib.pyplot as plt
        from geopandas.geodataframe import GeoDataFrame

        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        shadow = GeoDataFrame([{'geometry': result}], crs='epsg:2154')
        self.trees.plot(ax=basemap, color='red')
        shadow.boundary.plot(ax=basemap, color='grey')
        plt.show()
        '''

    def testProjectSphericalTreeOntoShadowPlane2(self):
        # alti, azim = 45, 270
        alti, azim = pi / 4, 3 * pi / 2
        radDir = self.__fromAltiAzimToRadDir(alti, azim)

        treeCrownRadius = 3.0

        result = ShadowLib.projectSphericalTreeOntoShadowPlane(
            self.treePosition, treeHeight=9.0, treeCrownRadius=treeCrownRadius, treeTrunkRadius=None,
            radDir=radDir, solarAlti=alti, solarAzim=azim, altitudeOfShadowPlane=0, npoints=32)

        self.assertIsInstance(result, Polygon, 'Is a Polygon')
        self.assertAlmostEqual(pi * sqrt(2) * treeCrownRadius ** 2, result.area, None, 'Test area', 0.3)
        self.assertAlmostEqual(result.centroid.x, self.treePosition.x, None, 'Test shadow centroid', 1e-3)

        '''
        import matplotlib.pyplot as plt
        from geopandas.geodataframe import GeoDataFrame

        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        shadow = GeoDataFrame([{'geometry': result}], crs='epsg:2154')
        self.trees.plot(ax=basemap, color='red')
        shadow.boundary.plot(ax=basemap, color='grey')
        plt.show()
        '''

    def testProjectSphericalTreeOntoShadowPlane3(self):
        # alti, azim = 45, 315
        alti, azim = pi / 4, 7 * pi / 4
        radDir = self.__fromAltiAzimToRadDir(alti, azim)

        treeCrownRadius = 3.0

        result = ShadowLib.projectSphericalTreeOntoShadowPlane(
            self.treePosition, treeHeight=9.0, treeCrownRadius=treeCrownRadius, treeTrunkRadius=None,
            radDir=radDir, solarAlti=alti, solarAzim=azim, altitudeOfShadowPlane=0, npoints=32)

        self.assertIsInstance(result, Polygon, 'Is a Polygon')

        '''
        import matplotlib.pyplot as plt
        from geopandas.geodataframe import GeoDataFrame

        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        shadow = GeoDataFrame([{'geometry': result}], crs='epsg:2154')
        self.trees.plot(ax=basemap, color='red')
        shadow.boundary.plot(ax=basemap, color='grey')
        '''

    def testProjectConicalTreeOntoShadowPlane1(self):
        # alti, azim = 90, 270
        alti, azim = pi / 2, 3 * pi / 2
        radDir = self.__fromAltiAzimToRadDir(alti, azim)

        treeCrownHeight = 6.0
        treeUpperCrownRadius = 3.0
        treeLowerCrownRadius = 3.0

        result = ShadowLib.projectConicalTreeOntoShadowPlane(
            self.treePosition, treeHeight=9.0,
            treeCrownHeight=treeCrownHeight,
            treeUpperCrownRadius=treeUpperCrownRadius,
            treeLowerCrownRadius=treeLowerCrownRadius,
            treeTrunkRadius=None, radDir=radDir, solarAlti=alti,
            solarAzim=azim, altitudeOfShadowPlane=0, npoints=32)

        self.assertIsInstance(result, Polygon, 'Is a Polygon')
        self.assertAlmostEqual(pi * treeUpperCrownRadius ** 2, result.area, None, 'Test area', 0.3)
        self.assertLess(self.treePosition.distance(result.centroid), 0.1, 'Test shadow centroid')

        '''
        import matplotlib.pyplot as plt
        from geopandas.geodataframe import GeoDataFrame

        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        shadow = GeoDataFrame([{'geometry': result}], crs='epsg:2154')
        self.trees.plot(ax=basemap, color='red')
        shadow.boundary.plot(ax=basemap, color='grey')
        plt.show()
        '''

    def testProjectConicalTreeOntoShadowPlane2(self):
        # alti, azim = 45, 315
        alti, azim = pi / 4, 7 * pi / 4
        radDir = self.__fromAltiAzimToRadDir(alti, azim)

        treeCrownHeight = 6.0
        treeUpperCrownRadius = 3.0
        treeLowerCrownRadius = 3.0

        result = ShadowLib.projectConicalTreeOntoShadowPlane(
            self.treePosition, treeHeight=9.0,
            treeCrownHeight=treeCrownHeight,
            treeUpperCrownRadius=treeUpperCrownRadius,
            treeLowerCrownRadius=treeLowerCrownRadius,
            treeTrunkRadius=None, radDir=radDir, solarAlti=alti,
            solarAzim=azim, altitudeOfShadowPlane=0, npoints=32)

        self.assertIsInstance(result, Polygon, 'Is a Polygon')
        self.assertTrue(self.treePosition.within(result), 'Test shadow geometry')

        '''
        '''
        import matplotlib.pyplot as plt
        from geopandas.geodataframe import GeoDataFrame

        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        shadow = GeoDataFrame([{'geometry': result}], crs='epsg:2154')
        self.trees.plot(ax=basemap, color='red')
        shadow.boundary.plot(ax=basemap, color='grey')
        plt.show()
        '''
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
