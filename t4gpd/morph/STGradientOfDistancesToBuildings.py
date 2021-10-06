'''
Created on 6 oct. 2020

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
from shapely.geometry import LineString
from shapely.ops import substring

from geopandas.geodataframe import GeoDataFrame
from numpy import abs, round
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STGradientOfDistancesToBuildings(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, lines, buildings, sampleDist, pathidFieldname=None, threshold=0.1, order=1):
        '''
        Constructor
        '''
        if not isinstance(lines, GeoDataFrame):
            raise IllegalArgumentTypeException(lines, 'GeoDataFrame')
        self.lines = lines

        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'GeoDataFrame')
        self.buildings = buildings
        self.spatialIdx = buildings.sindex

        if (pathidFieldname is not None) and (pathidFieldname not in lines):
            raise Exception('%s is not a relevant field name!' % (pathidFieldname))

        self.sampleDist = sampleDist
        self.pathidFieldname = pathidFieldname
        self.threshold = threshold

        if not order in (1, 2, 3):
            raise IllegalArgumentTypeException(order, '(1, 2, 3)')
        self.fieldToTest = 'r_deriv%d' % (order)

    def __getType(self, _nodeRow):
        _value = _nodeRow[self.fieldToTest]
        if (_value is not None) and (self.threshold > abs(_value)):
            return 'canyon'
        return 'square'
        
    def run(self):

        nodesRows, segmentsRows, linesRows = [], [], []
        for _id, row in self.lines.iterrows():
            _line = row.geometry
            _lineLen = _line.length
            if (self.sampleDist < _lineLen):
                _pathid = _id if (self.pathidFieldname is None) else row[self.pathidFieldname] 
                _nSegm = int(round(_lineLen / self.sampleDist))
                _sampleDist = _lineLen / _nSegm

                _nodesRows, _segmentsRows = [], []
                for i in range(0, _nSegm + 1):
                    _sampleGeom = _line.interpolate(i * _sampleDist)
                    _r, _nearestPoint, _ = GeomLib.getNearestFeature(
                        self.buildings, self.spatialIdx, _sampleGeom, buffDist=40.0)
                    _nodesRows.append({
                        'pathid': _pathid,
                        'nodeid': i,
                        'geometry': _sampleGeom,
                        'curv_absc': i * _sampleDist,
                        'r': _r,
                        'r_deriv1': None,
                        'r_deriv2': None,
                        'r_deriv3': None,
                        'area_type': None
                        })

                    _segmentsRows.append({
                        'pathid': _pathid,
                        'nodeid': i,
                        'geometry': LineString([(_sampleGeom.x, _sampleGeom.y), (_nearestPoint.x, _nearestPoint.y)]),
                        'curv_absc': i * _sampleDist,
                        'r': _r,
                        'r_deriv1': None,
                        'r_deriv2': None,
                        'r_deriv3': None,
                        'area_type': None
                        })

                # Assess 1st and 2nd order derivatives
                for i in range(1, _nSegm):
                    _hp1 = _nodesRows[i + 1]['geometry'].distance(_nodesRows[i]['geometry'])
                    _hm1 = _nodesRows[i]['geometry'].distance(_nodesRows[i - 1]['geometry'])

                    up1, u0, um1 = _nodesRows[i + 1]['r'], _nodesRows[i]['r'], _nodesRows[i - 1]['r']
                    
                    _fwdDiff = (up1 - u0) / _hp1
                    _bwdDiff = (u0 - um1) / _hm1
                    _nodesRows[i]['r_deriv1'] = (_fwdDiff + _bwdDiff) / 2.0
                    _cenDiff = (up1 - 2 * u0 + um1) / (_hp1 * _hm1)
                    _nodesRows[i]['r_deriv2'] = _cenDiff

                    if (1 < i < _nSegm - 1):
                        up2, um2 = _nodesRows[i + 2]['r'], _nodesRows[i - 2]['r']
                        _hp2 = _nodesRows[i + 2]['geometry'].distance(_nodesRows[i + 1]['geometry'])
                        _hm2 = _nodesRows[i - 2]['geometry'].distance(_nodesRows[i - 1]['geometry'])

                        _fwdDiff2 = (up2 - 3 * up1 + 3 * u0 - um1) / (_hp2 * _hp1 * _hm1)
                        _bwdDiff2 = (up1 - 3 * u0 + 3 * um1 - um2) / (_hp1 * _hm1 * _hm2)

                        _nodesRows[i]['r_deriv3'] = (_fwdDiff2 + _bwdDiff2) / 2.0
                        _segmentsRows[i]['r_deriv3'] = _nodesRows[i]['r_deriv3']

                    elif (1 < i):
                        um2 = _nodesRows[i - 2]['r']
                        _hm2 = _nodesRows[i - 2]['geometry'].distance(_nodesRows[i - 1]['geometry'])

                        _bwdDiff2 = (up1 - 3 * u0 + 3 * um1 - um2) / (_hp1 * _hm1 * _hm2)

                        _nodesRows[i]['r_deriv3'] = _bwdDiff2
                        _segmentsRows[i]['r_deriv3'] = _nodesRows[i]['r_deriv3']

                    elif (i < _nSegm - 1):
                        up2 = _nodesRows[i + 2]['r']
                        _hp2 = _nodesRows[i + 2]['geometry'].distance(_nodesRows[i + 1]['geometry'])

                        _fwdDiff2 = (up2 - 3 * up1 + 3 * u0 - um1) / (_hp2 * _hp1 * _hm1)

                        _nodesRows[i]['r_deriv3'] = _fwdDiff2
                        _segmentsRows[i]['r_deriv3'] = _nodesRows[i]['r_deriv3']

                    _nodesRows[i]['area_type'] = self.__getType(_nodesRows[i])

                    _segmentsRows[i]['r_deriv1'] = _nodesRows[i]['r_deriv1']
                    _segmentsRows[i]['r_deriv2'] = _nodesRows[i]['r_deriv2']
                    _segmentsRows[i]['area_type'] = _nodesRows[i]['area_type']

                _nodesRows[0]['r_deriv1'] = (_nodesRows[1]['r'] - _nodesRows[0]['r']) / _nodesRows[1]['geometry'].distance(_nodesRows[0]['geometry'])
                _nodesRows[0]['area_type'] = self.__getType(_nodesRows[0])

                _segmentsRows[0]['r_deriv1'] = _nodesRows[0]['r_deriv1']
                _segmentsRows[0]['area_type'] = _nodesRows[0]['area_type']

                _nodesRows[-1]['r_deriv1'] = (_nodesRows[-1]['r'] - _nodesRows[-2]['r']) / _nodesRows[-1]['geometry'].distance(_nodesRows[-2]['geometry'])
                _nodesRows[-1]['area_type'] = self.__getType(_nodesRows[-1])

                _segmentsRows[-1]['r_deriv1'] = _nodesRows[-1]['r_deriv1']
                _segmentsRows[-1]['area_type'] = _nodesRows[-1]['area_type']

                nodesRows += _nodesRows
                segmentsRows += _segmentsRows

                # Extract "continuous" sub-linestrings
                _prevRow, _prevStatus = _nodesRows[0], self.__getType(_nodesRows[0])
                for i in range(1, _nSegm + 1):
                    _currRow = _nodesRows[i]
                    _currStatus = self.__getType(_currRow)

                    if (_prevStatus != _currStatus) or (_nSegm == i):
                        _subls = substring(_line, _prevRow['curv_absc'], _currRow['curv_absc'])
                        linesRows.append({
                            'pathid': _pathid,
                            'geometry': _subls,
                            'area_type': _prevStatus
                            })
                        _prevRow, _prevStatus = _currRow, _currStatus

        return [
            GeoDataFrame(nodesRows, crs=self.lines.crs),
            GeoDataFrame(segmentsRows, crs=self.lines.crs),
            GeoDataFrame(linesRows, crs=self.lines.crs)]
