'''
Created on 18 juin 2020

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
from shapely.geometry import LineString, MultiLineString, Point

from t4gpd.commons.BoundingBox import BoundingBox
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCastingLib import RayCastingLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class AngularAbscissa(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, vpoint_x='vpoint_x', vpoint_y='vpoint_y', nRays=64):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        if vpoint_x not in inputGdf:
            raise Exception('Unknown vpoint_x field name: %s!' % (vpoint_x))
        if vpoint_y not in inputGdf:
            raise Exception('Unknown vpoint_y field name: %s!' % (vpoint_y))

        self.vpoint_x, self.vpoint_y = vpoint_x, vpoint_y
        self.shootingDirs = RayCastingLib.preparePanopticRays(nRays)

    def runWithArgs(self, row):
        # Use a buffer to avoid bugs
        geom = row.geometry.buffer(0.01, -1)
        bbox = BoundingBox(geom)
        maxRayLen = max(bbox.width(), bbox.height())

        vp = Point((float(row[self.vpoint_x]), float(row[self.vpoint_y])))
        rays = []
        for sdCos, sdSin in self.shootingDirs:
            rp = Point((vp.x + sdCos * maxRayLen, vp.y + sdSin * maxRayLen))
            ray = LineString((vp, rp))
            tmp = geom.intersection(ray)
            # QUID DE:
            # from shapely.ops import nearest_points 
            # _, nearestNode = nearest_points(vp, tmp)
            nodes = GeomLib.getListOfShapelyPoints(tmp)
            nearestNode, minDist = None, float('inf')
            for node in nodes:
                dist = vp.distance(node)
                if (0 < dist) and (dist < minDist):
                    minDist = dist
                    nearestNode = node
            if nearestNode is not None:
                rays.append(LineString((vp, nearestNode)))

        return { 'geometry':MultiLineString(rays) }
