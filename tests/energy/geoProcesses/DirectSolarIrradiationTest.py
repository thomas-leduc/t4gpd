'''
Created on 18 mai 2022

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
from datetime import datetime, timedelta
import unittest

from numpy.random import randint, seed
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STPointsDensifier2 import STPointsDensifier2
from t4gpd.morph.geoProcesses.FootprintExtruder import FootprintExtruder
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid

from t4gpd.energy.geoProcesses.DirectSolarIrradiation import DirectSolarIrradiation


class DirectSolarIrradiationTest(unittest.TestCase):

    def setUp(self):
        seed(0)

        self.buildings = GeoDataFrameDemos.regularGridOfPlots(3, 4, dw=5.0)
        self.buildings['HAUTEUR'] = 3.0 * randint(2, 7, size=len(self.buildings))
        self.buildings.geometry = self.buildings.geometry.apply(lambda g: GeomLib.normalizeRingOrientation(g)) 

        op = FootprintExtruder(self.buildings, 'HAUTEUR', forceZCoordToZero=True)
        self.buildingsIn3d = STGeoProcess(op, self.buildings).run()

        self.sensors = STPointsDensifier2(self.buildings, curvAbsc=[0.25, 0.75], pathidFieldname=None).run()
        self.sensors['__TMP__'] = list(zip(self.sensors.geometry, self.sensors.HAUTEUR))
        self.sensors.geometry = self.sensors.__TMP__.apply(lambda t: GeomLib.forceZCoordinateToZ0(t[0], z0=t[1] / 2))
        self.sensors.geometry = self.sensors.__TMP__.apply(lambda t: GeomLib.forceZCoordinateToZ0(t[0], z0=randint(1, t[1] - 1)))
        self.sensors.drop(columns=['__TMP__'], inplace=True)

    def tearDown(self):
        pass

    def plot2D(self):
        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1.75 * 8.26, 1.2 * 8.26))
        self.buildings.plot(ax=basemap, color='lightgrey')
        self.buildings.apply(lambda x: basemap.annotate(
            text=x.HAUTEUR, xy=x.geometry.centroid.coords[0],
            color='red', size=9, ha='center'), axis=1)
        self.sensors.plot(ax=basemap, column='direct_irradiation', legend=True)
        self.sensors.apply(lambda x: basemap.annotate(
            # text=x.node_id, xy=x.geometry.coords[0][0:2],
            # text=x.normal_vec, xy=x.geometry.coords[0][0:2],
            text=f'{x.direct_irradiation:.1f}', xy=x.geometry.coords[0][0:2],
            color='black', size=9, ha='center'), axis=1)
        plt.show()
        plt.close(fig)

    def plot3D(self):
        scene1 = ToUnstructuredGrid([self.buildingsIn3d, self.sensors], 'direct_irradiation').run()
        scene1.plot(scalars='direct_irradiation', cmap='gist_earth', show_edges=False,
                    show_scalar_bar=True, point_size=20.0, render_points_as_spheres=True)

    def testRun(self):
        # dtStart, dtStop = datetime(2021, 3, 21), datetime(2021, 3, 21)
        # dtStart, dtStop = datetime(2021, 6, 21), datetime(2021, 6, 21)
        dtStart, dtStop = datetime(2021, 12, 21), datetime(2021, 12, 21)
        op = DirectSolarIrradiation(self.sensors, self.buildings, 'normal_vec', 'HAUTEUR',
                                    dtStart, dtStop, dtDelta=timedelta(hours=1))
        self.sensors = STGeoProcess(op, self.sensors).run()

        self.plot2D()
        self.plot3D()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
