'''
Created on 24 sept. 2020

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

from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STSnappingPointsOnLines(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, pointsGdf, linesGdf, stepCountFieldname=None):
        '''
        Constructor
        '''
        if not isinstance(pointsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(pointsGdf, 'GeoDataFrame')
        self.pointsGdf = pointsGdf

        if not isinstance(linesGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(linesGdf, 'GeoDataFrame')
        self.linesGdf = linesGdf
        self.spatialIdx = linesGdf.sindex

        if stepCountFieldname is not None:
            if stepCountFieldname not in pointsGdf:
                raise Exception('%s is not a relevant field name!' % (stepCountFieldname))
        self.stepCountFieldname = stepCountFieldname

    def __check(self, checksum):
        prevStepCount, prevCurvAbsc = None, None
        for stepCount in sorted(checksum.keys()):
            if (prevStepCount is not None) and (prevCurvAbsc > checksum[stepCount]):
                print('Warning: curvilinear abscissa inconsistencies between step %d (%.2f m) and %d (%.2f m)' % 
                      (prevStepCount, prevCurvAbsc, stepCount, checksum[stepCount]))
            prevStepCount, prevCurvAbsc = stepCount, checksum[stepCount]

    def run(self):
        checksum, rows = dict(), []
        for _, rowPoint in self.pointsGdf.iterrows():
            geomPoint = rowPoint.geometry
            buffDist = 40.0
            minDist, nearestPoint, nearestRow = GeomLib.getNearestFeature(
                self.linesGdf, self.spatialIdx, geomPoint, buffDist)

            nearestLine = nearestRow.geometry
            curvilinearAbscissa = nearestLine.project(nearestPoint)
            if self.stepCountFieldname is not None:
                checksum[rowPoint[self.stepCountFieldname]] = curvilinearAbscissa

            rows.append(self.updateOrAppend(rowPoint, {
                # 'geometry': LineString((geomPoint, nearestPoint)),
                'geometry': nearestPoint,
                'dist_to_l': minDist,
                'curv_absc': curvilinearAbscissa 
                }))

        if self.stepCountFieldname is not None:
            self.__check(checksum)
        return GeoDataFrame(rows, crs=self.pointsGdf.crs)
