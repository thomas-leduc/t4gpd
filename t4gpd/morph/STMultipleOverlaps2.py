'''
Created on 19 sept. 2020

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
from itertools import combinations
from shapely.ops import unary_union

from geopandas.geodataframe import GeoDataFrame

from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.ListUtilities import ListUtilities


class STMultipleOverlaps2(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, by=None):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf
        if (by is not None) and (by not in inputGdf):
            raise Exception('%s is not a relevant field name!' % (by))
        self.by = by

    def run(self):
        rows = []

        if self.by is None:
            i, allIntersections = 0, dict({ 1: dict() })
            for geom in self.inputGdf.geometry:
                _geoms = []
                for _geom in GeomLib.flattenGeometry(geom):
                    if 1.0 < _geom.area:
                        _geoms.append(_geom)
                if 0 < len(_geoms):
                    allIntersections[1][tuple([i])] = unary_union(_geoms)
                    i += 1

            nGeoms = len(allIntersections[1])
            geomIds = list(range(nGeoms))

            for n in range(2, nGeoms + 1):
                allIntersections[n] = dict()
                for combin in combinations(geomIds, n):
                    keyLeft = combin[:-1]
                    keyRight = tuple([combin[-1]])

                    allIntersections[n][combin] = allIntersections[n - 1][keyLeft].intersection(
                        allIntersections[1][keyRight])

            for n in sorted(allIntersections.keys()):
                row = { 'geometry': unary_union(allIntersections[n].values()), 'nOverlap': n }
                rows.append(row)

            for n in range(len(rows) - 1):
                rows[n]['geometry'] = rows[n]['geometry'].difference(rows[n + 1]['geometry'])

        else:
            allIntersections = dict({ 1: dict() })
            for _, row in self.inputGdf.iterrows():
                key, geom = row[self.by], row.geometry
                _geoms = []
                for _geom in GeomLib.flattenGeometry(geom):
                    if 1.0 < _geom.area:
                        _geoms.append(_geom)
                if 0 < len(_geoms):
                    allIntersections[1][tuple([key])] = unary_union(_geoms)

            nGeoms = len(allIntersections[1])
            geomIds = ListUtilities.flatten(allIntersections[1].keys())

            for n in range(2, nGeoms + 1):
                allIntersections[n] = dict()
                for combin in combinations(geomIds, n):
                    keyLeft = combin[:-1]
                    keyRight = tuple([combin[-1]])

                    allIntersections[n][combin] = allIntersections[n - 1][keyLeft].intersection(
                        allIntersections[1][keyRight])

            uog = None
            for n in range(nGeoms, 0, -1):
                for combin in combinations(geomIds, n):
                    _geom = allIntersections[n][combin]
                    if uog is not None:
                        _geom = _geom.difference(uog)

                    if 0.0 < _geom.area:
                        row = { 'geometry': _geom, 'nOverlap': n,
                               'matched_id': ArrayCoding.encode(combin) }
                        rows.append(row)
                uog = unary_union(allIntersections[n].values())

        return GeoDataFrame(rows, crs=self.inputGdf.crs)
