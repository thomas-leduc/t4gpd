'''
Created on 10 mar. 2022

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
from geopandas import GeoDataFrame, sjoin
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.wkt import loads
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STFacadesAnalysis import STFacadesAnalysis


class STDeploymentOfPVPanels2(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, idFieldName='ID', coverRate=1.0, stripWidth=3.2,
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

        self.coverRate = coverRate
        self.stripWidth = stripWidth
        self.azim0, self.azim1 = azimuthRange
        self.sizeOfPVPanel = sizeOfPVPanel

    @staticmethod
    def __nModules(stripLength, stripWidth, sizeOfPVPanel):
        d1, d2 = sizeOfPVPanel
        return max(
            (stripLength // d1) * (stripWidth // d2),
            (stripLength // d2) * (stripWidth // d1)
            )

    @staticmethod
    def __buildPvArea(edge, normal, stripWidth):
        p0, p1 = edge.coords
        n0, n1 = loads(normal).coords
        n = (n1[0] - n0[0], n1[1] - n0[1])
        return Polygon([
            p0, (p0[0] - stripWidth * n[0], p0[1] - stripWidth * n[1]),
            (p1[0] - stripWidth * n[0], p1[1] - stripWidth * n[1]), p1
            ])

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
                          (facades.length > (0.5 + min(self.sizeOfPVPanel)))]

        facades.drop(columns=['buildingID', 'height', 'surface'], inplace=True)

        # ------
        # SPATIAL JOIN BETWEEN FACADES AND BUILDINGS
        _facades = facades.copy()
        _facades.geometry = _facades.geometry.apply(lambda g: g.centroid.buffer(1e-2))
        _facades = sjoin(_facades[['gid', 'geometry']],
                         self.buildings[[self.idFieldName, 'geometry']],
                         how='left', predicate='intersects')
        _facades.drop(columns=['index_right', 'geometry'], inplace=True)

        # ------
        # ATTRIBUTE JOIN BETWEEN FACADES AND _FACADES
        pvStrip = facades.merge(_facades, on='gid')

        # ------
        # NUMBER OF PHOTOVOLTAIC MODULES PER FACADES
        pvStrip['n_modules'] = pvStrip.length.apply(
            lambda l: self.__nModules(l, self.stripWidth, self.sizeOfPVPanel))
        pvStrip.n_modules = self.coverRate * pvStrip.n_modules  # apply the coverage rate
        pvStrip = pvStrip.loc[ pvStrip[pvStrip.n_modules > 1].index ]  # Remove facades without modules
        pvStrip.n_modules = pvStrip.n_modules.astype(int)

        # ------
        # FROM FACADES TO PV AREA
        pvStrip['__TMP__'] = list(zip(pvStrip.geometry, pvStrip.normal))
        pvStrip.geometry = pvStrip.__TMP__.apply(lambda t: self.__buildPvArea(*t, self.stripWidth))
        pvStrip.drop(columns=['__TMP__'], inplace=True)

        return pvStrip
