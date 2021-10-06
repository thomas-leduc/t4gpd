'''
Created on 17 sept. 2020

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
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STIdentifyRowOfTrees(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, treesGdf, treeIdFieldname, roadIdFieldname='road_id', roadDistFieldname='road_dist',
                 roadAbscissaFieldname='road_absc', roadSideFieldname='road_side', nTreesThreshold=4):
        '''
        Constructor
        '''
        if not isinstance(treesGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(treesGdf, 'GeoDataFrame')
        self.treesGdf = treesGdf

        if treeIdFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (treeIdFieldname))
        self.treeIdFieldname = treeIdFieldname

        if roadIdFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (roadIdFieldname))
        self.roadIdFieldname = roadIdFieldname

        if roadDistFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (roadDistFieldname))
        self.roadDistFieldname = roadDistFieldname

        if roadAbscissaFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (roadAbscissaFieldname))
        self.roadAbscissaFieldname = roadAbscissaFieldname

        if roadSideFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (roadSideFieldname))
        self.roadSideFieldname = roadSideFieldname

        self.nTreesThreshold = nTreesThreshold

    def run(self):
        ht = dict()

        for _, row in self.treesGdf.iterrows():
            treeGeom = row.geometry.coords[0]
            treeId = row[self.treeIdFieldname]
            roadId = row[self.roadIdFieldname]
            roadDist = row[self.roadDistFieldname]
            roadAbsc = row[self.roadAbscissaFieldname]
            roadSide = row[self.roadSideFieldname]

            currItem = {
                'tree_id': treeId,
                'road_dist': roadDist,
                'road_absc': roadAbsc,
                'geometry': treeGeom
                }

            if roadId not in ht:
                ht[roadId] = {roadSide: [currItem]}
            elif roadSide not in ht[roadId]:
                ht[roadId][roadSide] = [currItem]
            else:
                ht[roadId][roadSide].append(currItem)

        rows = []
        for roadId in ht.keys():
            for roadSide in ht[roadId].keys():
                if self.nTreesThreshold < len(ht[roadId][roadSide]):
                    ht[roadId][roadSide].sort(key=lambda t: t['road_absc'])
                    geom = LineString([t['geometry'] for t in ht[roadId][roadSide]])
                    rows.append({'geometry': geom, 'road_id': roadId, 'road_side': roadSide})

        return GeoDataFrame(rows, crs=self.treesGdf.crs)
