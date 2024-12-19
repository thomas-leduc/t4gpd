'''
Created on 17 janv. 2021

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

from datetime import date, time, timezone
from geopandas import GeoDataFrame
from shapely.geometry import box, Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.skymap.STSkyMap25D import STSkyMap25D
from t4gpd.sun.STSunMap2D import STSunMap2D


class STSunMap2DTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        self.buildings.fillna({"HAUTEUR": 3.33}, inplace=True)

        self.viewpoint = GeoDataFrame([
            {"gid": 1, "geometry": Point((355143.0, 6689359.4))}], crs=self.buildings.crs)
        self.datetimes = [date(2023, month, 21) for month in (3, 6, 12)]
        self.datetimes += [time(hour) for hour in range(7, 18)]

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt

        skymap = STSkyMap25D(self.buildings, self.viewpoint, nRays=180,
                             rayLength=100.0, elevationFieldname="HAUTEUR",
                             h0=0, size=6.0, epsilon=0.01, projectionName="Stereographic").run()

        minx, miny, maxx, maxy = box(*skymap.total_bounds).buffer(10.0).bounds

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        ax.set_title("Sky + Sun Maps", fontsize=16)
        self.buildings.plot(ax=ax, color="dimgrey")
        skymap.plot(ax=ax, color="lightgrey")
        self.viewpoint.plot(ax=ax, marker="+")
        # result.plot(ax=ax, linewidth=0.5, color="black")
        result[result.label == "framework"].plot(
            ax=ax, linewidth=0.5, color="dimgrey")
        result[result.label.str.startswith(
            "2023-")].plot(ax=ax, linewidth=0.5, color="red")
        result[result.label.str.endswith(":00:00")].plot(
            ax=ax, linewidth=0.5, color="blue")
        plt.axis([minx, maxx, miny, maxy])
        plt.axis("off")
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STSunMap2D(self.viewpoint, self.datetimes, size=6.0,
                            projectionName="Stereographic", tz=timezone.utc,
                            model="pysolar").run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(17, len(result), "Count rows")
        self.assertEqual(2, len(result.columns), "Count columns")

        self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
