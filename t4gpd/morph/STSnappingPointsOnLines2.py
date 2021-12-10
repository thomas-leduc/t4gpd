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
from pandas import DataFrame
from shapely.geometry import Point
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STSnappingPointsOnLines2(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, pointsGdf, linesGdf, wayPointsGdf, stepCountFieldname, tagName,
                 wayPointsIdFieldname):
        '''
        Constructor
        '''
        if not isinstance(pointsGdf, DataFrame):
            raise IllegalArgumentTypeException(pointsGdf, 'DataFrame')
        self.pointsGdf = pointsGdf

        if not isinstance(linesGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(linesGdf, 'GeoDataFrame')
        self.linesGdf = linesGdf
        self.spatialIdx = linesGdf.sindex
        if (1 != len(self.linesGdf)):
            raise Exception('%s is not a one-row GeoDataFrame!' % (self.linesGdf))

        if not isinstance(wayPointsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(wayPointsGdf, 'GeoDataFrame')
        self.wayPointsGdf = wayPointsGdf

        if stepCountFieldname not in pointsGdf:
            raise Exception('%s is not a relevant field name!' % (stepCountFieldname))
        self.stepCountFieldname = stepCountFieldname

        if tagName not in pointsGdf:
            raise Exception('%s is not a relevant field name!' % (tagName))
        self.tagName = tagName

        if wayPointsIdFieldname not in wayPointsGdf:
            raise Exception('%s is not a relevant field name!' % (wayPointsIdFieldname))
        self.wayPointsIdFieldname = wayPointsIdFieldname

    def run(self):
        pathGeom = self.linesGdf.geometry.squeeze()

        # 1st STEP: PROJECT WAYPOINTS ONTO THE LINES
        projWayPoints = dict()
        for _, wayPoint in self.wayPointsGdf.iterrows():
            wayPointId = wayPoint[self.wayPointsIdFieldname]
            wayPointCurvDist = pathGeom.project(wayPoint.geometry)
            wayPointGeom = pathGeom.interpolate(wayPointCurvDist)

            projWayPoints[wayPointId] = {
                'gid': wayPointId,
                'curv_absc': wayPointCurvDist,
                'geometry': wayPointGeom
                }

        # 2nd STEP: READ MEASURE POINTS AND IDENTIFY THE POTENTIAL WAYPOINTS
        self.pointsGdf = self.pointsGdf.sort_values(self.stepCountFieldname)

        prevStartStepCount, prevCurvAbsc = 0, 0.0
        _pointsGdf = self.pointsGdf[
            (~self.pointsGdf[self.tagName].isin(['NA', '"NA"'])) & 
            (~self.pointsGdf[self.tagName].isnull())
            ]

        for _, point in _pointsGdf.iterrows():
            tagName = point[self.tagName]
            tagName = int(tagName.replace('"', '')) if isinstance(tagName, str) else tagName
            stepCount = point[self.stepCountFieldname]

            if tagName in projWayPoints:
                projWayPoints[tagName]['startStepCount'] = prevStartStepCount
                projWayPoints[tagName]['stopStepCount'] = stepCount
                projWayPoints[tagName]['nPoints'] = 0
                projWayPoints[tagName]['deltaL'] = projWayPoints[tagName]['curv_absc'] - prevCurvAbsc
                prevStartStepCount = stepCount + 1
                prevCurvAbsc = projWayPoints[tagName]['curv_absc']
            else:
                raise Exception('Unreachable instruction!')

        wayPointIdMax = 1 + max([ v['gid'] for v in projWayPoints.values() ])
        stepCountMax = max(self.pointsGdf[self.stepCountFieldname])

        projWayPoints[wayPointIdMax] = {
            'gid': wayPointIdMax,
            'curv_absc': pathGeom.length,
            'geometry': Point((list(pathGeom.coords)[-1])),
            'startStepCount': prevStartStepCount,
            'stopStepCount': stepCountMax,
            'nPoints': 0,
            'deltaL': pathGeom.length - prevCurvAbsc
            }

        # 3rd STEP: COUNT MEASURE POINTS PER PAIR OF WAYPOINTS
        for _, point in self.pointsGdf.iterrows():
            stepCount = point[self.stepCountFieldname]
            for tagName in projWayPoints.keys():
                if (projWayPoints[tagName]['startStepCount'] <= stepCount <= projWayPoints[tagName]['stopStepCount']):
                    projWayPoints[tagName]['nPoints'] += 1

        for tagName in list(projWayPoints.keys()):
            if (0 == projWayPoints[tagName]['nPoints']):
                del(projWayPoints[tagName])
            else:
                projWayPoints[tagName]['deltaL'] = projWayPoints[tagName]['deltaL'] / projWayPoints[tagName]['nPoints']

        # 4th STEP: POPULATE THE OUTPUT ROWS RESULT
        inputMeasurePoints = dict()
        for _, point in self.pointsGdf.iterrows():
            stepCount = point[self.stepCountFieldname]
            inputMeasurePoints[stepCount] = point

        initialStartStepCount = min(inputMeasurePoints.keys())
        currCurvAbsc, startStepCount, rows = 0, initialStartStepCount, []
        for tagName in sorted(projWayPoints.keys()):
            incCurvAbsc = projWayPoints[tagName]['deltaL']
            stopStepCount = projWayPoints[tagName]['stopStepCount']

            for stepCount in range(startStepCount, stopStepCount + 1):
                if initialStartStepCount < stepCount:
                    currCurvAbsc += incCurvAbsc
                row = inputMeasurePoints[stepCount]
                projPoint = pathGeom.interpolate(currCurvAbsc)
                dist_to_l = row['geometry'].distance(projPoint) if ('geometry' in row) else None    
                row['geometry'] = projPoint
                row['dist_to_l'] = dist_to_l
                row['curv_absc'] = currCurvAbsc
                rows.append(row)

            startStepCount = stopStepCount + 1

        return GeoDataFrame(rows, crs=self.wayPointsGdf.crs)
