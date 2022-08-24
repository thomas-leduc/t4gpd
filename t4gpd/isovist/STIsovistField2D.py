'''
Created on 17 juin 2020

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
from multiprocessing import Pool

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, Point, Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCasting3Lib import RayCasting3Lib


class STIsovistField2D(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, viewpoints, nRays=64, rayLength=100.0, multiprocessing=False):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'buildings GeoDataFrame')
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(viewpoints, 'viewpoints GeoDataFrame')
        if not (buildings.crs == viewpoints.crs):
            raise Exception('Illegal argument: buildings and viewpoints must share shames CRS!')

        self.buildings = buildings
        # CLEAN GEOMETRIES
        self.buildings.geometry = self.buildings.geometry.apply(lambda g: g.buffer(0))

        self.viewpoints = viewpoints
        self.shootingDirs = RayCasting3Lib.preparePanopticRays(nRays)
        self.rayLength = rayLength
        self.multiprocessing = multiprocessing

    @staticmethod
    def _process(params):
        row, masks, viewPoint, shootingDirs, rayLength = params
        return row, RayCasting3Lib.outdoorMultipleRayCast2D(masks, viewPoint, shootingDirs, rayLength)

    def run(self):
        rowsIsovRays, rowsIsov = list(), list()

        if self.multiprocessing:
            # PREPROCESS
            listOfParams = [
                (row, self.buildings, Point((row.geometry.x, row.geometry.y)), self.shootingDirs, self.rayLength)
                for _, row in self.viewpoints.iterrows()
                ]

            # PROCESS
            pool = Pool()
            quartets = pool.map(STIsovistField2D._process, listOfParams)
            pool.close()

            # POSTPROCESS
            for row, (rays, ctrPoints, _) in quartets:
                vp = Point((row.geometry.x, row.geometry.y))
                isov = Polygon(ctrPoints)
                isovCentre = isov.centroid
                if isovCentre.is_empty:
                    drift = None
                else:
                    drift = LineString([vp, isovCentre]).wkt

                rowsIsovRays.append(self.updateOrAppend(row, { 
                    'geometry': rays, 'viewpoint': vp.wkt, 'vect_drift': drift }))
                rowsIsov.append(self.updateOrAppend(row, {
                    'geometry': isov, 'viewpoint': vp.wkt, 'vect_drift': drift }))

        else:
            for _, row in self.viewpoints.iterrows():
                vp = Point((row.geometry.x, row.geometry.y))  # To handle Point Z
                rays, ctrPoints, _ = RayCasting3Lib.outdoorMultipleRayCast2D(self.buildings, vp, self.shootingDirs, self.rayLength)
                isov = Polygon(ctrPoints)
                isovCentre = isov.centroid
                if isovCentre.is_empty:
                    drift = None
                else:
                    drift = LineString([vp, isovCentre]).wkt

                rowsIsovRays.append(self.updateOrAppend(row, { 
                    'geometry': rays, 'viewpoint': vp.wkt, 'vect_drift': drift }))
                rowsIsov.append(self.updateOrAppend(row, {
                    'geometry': isov, 'viewpoint': vp.wkt, 'vect_drift': drift }))

        return [
            GeoDataFrame(rowsIsovRays, crs=self.viewpoints.crs),
            GeoDataFrame(rowsIsov, crs=self.viewpoints.crs)
            ]
