'''
Created on 18 juil. 2022

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
from geopandas import GeoDataFrame
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess
from t4gpd.pyvista.commons.RayCastingIn3DLib import RayCastingIn3DLib
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from shapely.geometry import LinearRing, LineString, Polygon
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class AutomaticFaceOrientation(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, gdf, dist=1e-3):
        '''
        Constructor
        '''
        assert isinstance(gdf, GeoDataFrame), 'gdf must be a GeoDataFrame'
        self.obbTree = RayCastingIn3DLib.prepareVtkOBBTree(gdf)
        self.maxHeight = ToUnstructuredGrid([gdf]).run().length
        self.dist = dist

    @staticmethod
    def __reverseOrientation(obj):
        if isinstance(obj, LineString):
            return LinearRing(reversed(obj.coords))

        elif isinstance(obj, Polygon):
            extRing = AutomaticFaceOrientation.__reverseOrientation(obj.exterior)
            intRings = [AutomaticFaceOrientation.__reverseOrientation(hole) for hole in obj.interiors]
            return Polygon(extRing, intRings)

        raise IllegalArgumentTypeException(obj, 'Shapely LineString or Polygon')

    def runWithArgs(self, row):
        geom = row.geometry
        assert GeomLib.isPolygonal(geom), 'The GeoDataFrame must be composed of (Multi)Polygon'
        c = GeomLib3D.centroid(geom).coords[0]
        n = GeomLib3D.getFaceNormalVector(geom)

        # The objective here is to move the Ray Casting point away from the face
        srcPt = [ c[i] + self.dist * n[i] for i in range(3) ]
        dstPt = [ srcPt[0], srcPt[1], srcPt[2] + self.maxHeight ]
        if RayCastingIn3DLib.areCovisibleObbTree(self.obbTree, srcPt, dstPt):
            # FACE IS CORRECTLY ORIENTED
            return { 'reverse': 0 }

        srcPt = [ c[i] - self.dist * n[i] for i in range(3) ]
        dstPt = [ srcPt[0], srcPt[1], srcPt[2] + self.maxHeight ]
        if RayCastingIn3DLib.areCovisibleObbTree(self.obbTree, srcPt, dstPt):
            # FACE IS NOT CORRECTLY ORIENTED
            geom = AutomaticFaceOrientation.__reverseOrientation(geom)
            return { 'geometry': geom, 'reverse': 1 }

        # INDECISION
        return { 'reverse': 2 }
