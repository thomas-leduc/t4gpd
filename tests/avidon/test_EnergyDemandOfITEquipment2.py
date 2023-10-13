'''
Created on 16 feb. 2022

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
import unittest
'''
import unittest

from datetime import datetime, timezone
from geopandas import clip, GeoDataFrame, overlay
from shapely.geometry import box, JOIN_STYLE, MultiPolygon, Polygon
from t4gpd.avidon.EnergyDemandOfITEquipment2 import EnergyDemandOfITEquipment2
from t4gpd.demos.GeoDataFrameDemos2 import GeoDataFrameDemos2
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class EnergyDemandOfITEquipment2Test(unittest.TestCase):

    def setUp(self):
        self.iris = GeoDataFrameDemos2.irisMadeleineInNantes()
        self.buildings = GeoDataFrameDemos2.irisMadeleineInNantesBuildings()
        self.grid = GeoDataFrameDemos2.irisMadeleineInNantesINSEEGrid()
        self.dwellings = self.buildings.loc[ self.buildings[self.buildings.NATURE == 'Indifférenciée'].index ]

        # ------
        # TOTAL FLOOR AREA PER BUILDING
        self.dwellings = overlay(self.dwellings, self.grid, how='intersection')
        self.dwellings['nb_storeys'] = self.dwellings.HAUTEUR.apply(lambda h: max(h // 3, 1))
        self.dwellings['floor_surf'] = self.dwellings.area * self.dwellings.nb_storeys

        # ------
        # DISAGGREGATION - ESTIMATED POPULATION PER BUILDING/DWELLING
        _fromGridToSurf = self.dwellings.groupby(['IdINSPIRE'])['floor_surf'].sum().to_dict()
        self.dwellings['floor_ratio'] = list(zip(self.dwellings.floor_surf, self.dwellings.IdINSPIRE))
        self.dwellings.floor_ratio = self.dwellings.floor_ratio.apply(lambda t: t[0] / _fromGridToSurf[t[1]])

        for _attr in ['Ind', 'Men', 'Men_pauv', 'Men_1ind', 'Men_5ind', 'Men_prop',
                'Men_fmp', 'Ind_snv', 'Men_surf', 'Men_coll', 'Men_mais',
                'Log_av45', 'Log_45_70', 'Log_70_90', 'Log_ap90', 'Log_inc',
                'Log_soc', 'Ind_0_3', 'Ind_4_5', 'Ind_6_10', 'Ind_11_17',
                'Ind_18_24', 'Ind_25_39', 'Ind_40_54', 'Ind_55_64', 'Ind_65_79',
                'Ind_80p', 'Ind_inc']:
            self.dwellings[_attr] = self.dwellings[_attr] * self.dwellings.floor_ratio

        # ------
        # CHECK THE DISAGGREGATION RESULT
        _tmp = self.dwellings.groupby(by='IdINSPIRE')['floor_ratio'].sum()
        for _v in _tmp:
            self.assertAlmostEqual(1.0, _v, None, 'Check the disaggregation result', 1e-3)

        # ------
        # LIMIT DWELLINGS TO THE IRIS AREA
        self.dwellings = clip(self.dwellings, self.iris)

    def tearDown(self):
        pass

    def testRun(self):
        columns = ['Men', 'Ind_11_17', 'Ind_18_24', 'Ind_25_39',
                   'Ind_40_54', 'Ind_55_64', 'Ind_65_79', 'Ind_80p']
        dt = datetime(2022, 2, 16, 9, 21, tzinfo=timezone.utc)

        op = EnergyDemandOfITEquipment2(columns, dt)
        result = STGeoProcess(op, self.dwellings).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(len(self.dwellings), len(result), 'Count rows')
        self.assertEqual(2 + len(self.dwellings.columns), len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertTrue(isinstance(row.geometry, (Polygon, MultiPolygon)),
                            'Is a GeoDataFrame of (Multi)Polygons')
            self.assertEqual(dt, row['datetime'], 'Test datetime column')
            self.assertLess(0, row['IT_in_Wh'], 'Test IT_in_Wh column (1)')
            self.assertGreater(5587, row['IT_in_Wh'], 'Test IT_in_Wh column (2)')

        '''
        '''
        import matplotlib.pyplot as plt

        minx, miny, maxx, maxy = box(*result.total_bounds).buffer(20, join_style=JOIN_STYLE.mitre).bounds
        fig, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.iris.boundary.plot(ax=basemap, color='red')
        self.buildings.plot(ax=basemap, color='grey', edgecolor='white')
        # self.dwellings.plot(ax=basemap, column='Ind', legend=True)
        result.plot(ax=basemap, column='IT_in_Wh', legend=True)
        # roads.plot(ax=basemap, color='black', linewidth=1)
        self.grid.boundary.plot(ax=basemap, color='green', linewidth=1)
        basemap.axis([minx, maxx, miny, maxy])
        basemap.axis('off')
        plt.show()
        plt.close(fig)
        '''
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
