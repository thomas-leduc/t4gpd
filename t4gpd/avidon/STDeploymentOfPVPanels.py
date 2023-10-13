'''
Created on 1 juil. 2021

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
from geopandas import GeoDataFrame, sjoin
from shapely.ops import unary_union
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STFacadesAnalysis import STFacadesAnalysis


class STDeploymentOfPVPanels(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, idFieldName='ID', elevationFieldName='HAUTEUR', coverRate=0.3,
                 azimuthRange=(270 - 45, 270 + 45), sizeOfPVPanel=(1.6, 1.0)):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'buildings GeoDataFrame')
        self.buildings = buildings

        if idFieldName not in buildings:
            raise Exception('%s is not a relevant field name!' % (idFieldName))
        self.idFieldName = idFieldName

        if elevationFieldName not in buildings:
            raise Exception('%s is not a relevant field name!' % (elevationFieldName))
        self.elevationFieldName = elevationFieldName

        self.coverRate = coverRate
        self.azim0, self.azim1 = azimuthRange
        self.dh, self.dw = sizeOfPVPanel

    def run(self):
        # ------
        # REMOVE SHARED WALLS
        uob = unary_union(self.buildings.geometry).buffer(1e-4)
        uob = GeoDataFrame([{'geometry': uob}], crs=self.buildings.crs)
        uob = uob.explode(ignore_index=True)

        # ------
        # SELECT WELL ORIENTED AND BIG ENOUGH FACADES
        facades = STFacadesAnalysis(uob, gidFieldname=None, elevationFieldname=None,
                                    exteriorOnly=False).run()
        facades = facades[(facades.azimuth >= self.azim0) & (facades.azimuth <= self.azim1) & 
                          (facades.length > (0.5 + min(self.dh, self.dw)))]
        facades.drop(columns=['buildingID', 'height', 'surface'], inplace=True)

        # ------
        # SPATIAL JOIN BETWEEN FACADES AND BUILDINGS
        _facades = facades.copy()
        _facades.geometry = _facades.geometry.apply(lambda g: g.centroid.buffer(1e-2))
        _facades = sjoin(_facades[['gid', 'geometry']],
                         self.buildings[[self.idFieldName, self.elevationFieldName, 'geometry']],
                         how='left', predicate='intersects')
        _facades.drop(columns=['index_right', 'geometry'], inplace=True)

        # ------
        # ATTRIBUTE JOIN BETWEEN FACADES AND _FACADES
        pvFacades = facades.merge(_facades, on='gid')

        # ------
        # NUMBER OF PHOTOVOLTAIC MODULES PER FACADES
        pvFacades['n_modules'] = list(zip(pvFacades.length, pvFacades.HAUTEUR))
        pvFacades.n_modules = pvFacades.n_modules.apply(lambda t: int(t[0] / self.dw) * int(t[1] / self.dh))
        pvFacades.n_modules = self.coverRate * pvFacades.n_modules  # apply the coverage rate
        pvFacades = pvFacades[pvFacades.n_modules > 1]  # Remove facades without modules
        pvFacades.n_modules = pvFacades.n_modules.astype(int)

        return pvFacades
