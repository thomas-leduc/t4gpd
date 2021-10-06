'''
Created on 2 oct. 2020

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
from numpy import inf
from shapely.geometry import LineString
from shapely.ops import unary_union
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STPointsDensifier import STPointsDensifier
from t4gpd.morph.STVoronoiPartition import STVoronoiPartition


class STCoolscapesTessellation(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, linesGdf, sampleDist, buffDist, magnitude=5):
        '''
        Constructor
        '''
        if not isinstance(linesGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(linesGdf, 'GeoDataFrame')

        self.linesGdf = linesGdf
        self.pathGeom = unary_union(self.linesGdf.geometry)
        if not isinstance(self.pathGeom, LineString):
            raise IllegalArgumentTypeException(linesGdf, 'GeoDataFrame of continuous LineStrings')

        self.sampleDist = sampleDist
        self.buffDist = buffDist
        self.magnitude = magnitude

    def __getSensors(self):
        _sensors = STPointsDensifier(
            self.linesGdf, self.sampleDist, pathidFieldname=None, adjustableDist=True,
            removeDuplicate=True).run()

        _bigBuffZoneGeom = self.pathGeom.buffer(self.magnitude * self.buffDist)
        _bigBuffZone = GeoDataFrame([{'geometry': _bigBuffZoneGeom}], crs=self.linesGdf.crs)

        _otherSensors = STPointsDensifier(
            _bigBuffZone, self.magnitude * self.sampleDist, pathidFieldname=None,
            adjustableDist=True, removeDuplicate=True).run()

        return _sensors.append(_otherSensors)

    def __orderTessellationCells(self, tessellation):
        mydict = dict()
        for _, rowCell in tessellation.iterrows():
            cellGid = rowCell['gid']
            cellCurvAbsc = self.pathGeom.project(rowCell.geometry.centroid)
            mydict[cellGid] = float(cellCurvAbsc)

        orddict = sorted(mydict.items(), key=lambda kv: kv[1])
        correspTable = { cellGid:i for i, (cellGid, _) in enumerate(orddict)}
        tessellation['gid'] = tessellation['gid'].apply(lambda cellGid: correspTable[cellGid])
        tessellation.sort_values(by='gid', inplace=True)
        return tessellation

    def run(self):
        _tessellation = STVoronoiPartition(self.__getSensors()).run()
        _buffZoneGeom = self.pathGeom.buffer(self.buffDist)

        _tessellation.geometry = _tessellation.geometry.apply(lambda g: g.intersection(_buffZoneGeom))

        # FILTER EMPTY GEOMETRIES
        _tessellation = _tessellation[~_tessellation.is_empty]
        # ORDER TESSELLATION CELLS
        _tessellation = self.__orderTessellationCells(_tessellation)

        # ADD START/STOP CURVILINEAR ABSCISSA TO EACH TESSELLATION CELL
        startCurvAbsc, stopCurvAbsc = [], []

        nCells = len(_tessellation)
        for _, row in _tessellation.iterrows():
            _gid = row['gid']
            _tmpGeom = row.geometry.boundary.intersection(self.pathGeom)
            _tmpGeom = GeomLib.getListOfShapelyPoints(_tmpGeom)
            _tmpCurvAbsc = sorted([self.pathGeom.project(p) for p in _tmpGeom])

            if (0 == _gid):
                startCurvAbsc.append(-inf)
                stopCurvAbsc.append(_tmpCurvAbsc[-1])
            elif (nCells - 1 == _gid):
                startCurvAbsc.append(stopCurvAbsc[-1])
                stopCurvAbsc.append(inf)
            else:
                if (2 != len(_tmpCurvAbsc)):
                    raise Exception('STCoolscapesTessellation:: Unreachable instruction!')
                startCurvAbsc.append(_tmpCurvAbsc[0])
                stopCurvAbsc.append(_tmpCurvAbsc[1])

        _tessellation['curv_abs_0'] = startCurvAbsc
        _tessellation['curv_abs_1'] = stopCurvAbsc

        return _tessellation
