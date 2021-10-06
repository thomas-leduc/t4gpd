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
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, Point, Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCastingLib import RayCastingLib


class STIsovistField2D(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, viewpoints, nRays=64, rayLength=100.0):
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
        self.masksSIdx = buildings.sindex
        self.viewpoints = viewpoints
        self.shootingDirs = RayCastingLib.preparePanopticRays(nRays)
        self.rayLength = rayLength

    def run(self):
        rowsIsovRays, rowsIsov = list(), list()
        for _, row in self.viewpoints.iterrows():
            vp = Point((row.geometry.x, row.geometry.y))  # To handle Point Z
            rays, ctrPoints, _, _ = RayCastingLib.multipleRayCast2D(self.buildings, self.masksSIdx,
                                                                    vp, self.shootingDirs, self.rayLength)

            isov = Polygon(ctrPoints) 
            isovCentre = isov.centroid
            drift = LineString([vp, isovCentre])

            rowsIsovRays.append(self.updateOrAppend(row, { 
                'geometry': rays, 'viewpoint': vp.wkt, 'vect_drift': drift.wkt }))
            rowsIsov.append(self.updateOrAppend(row, {
                'geometry': isov, 'viewpoint': vp.wkt, 'vect_drift': drift.wkt }))

        return [
            GeoDataFrame(rowsIsovRays, crs=self.viewpoints.crs),
            GeoDataFrame(rowsIsov, crs=self.viewpoints.crs)
            ]
