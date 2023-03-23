'''
Created on 27 sept. 2020

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
from shapely.geometry import box
from shapely.ops import  linemerge, unary_union
from shapely.prepared import prep
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STPointsDensifier import STPointsDensifier
from t4gpd.morph.STVoronoiPartition import STVoronoiPartition


class STSkeletonizeTheVoid(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildingsGdf, samplingDist=10.0):
        '''
        Constructor
        '''
        if not isinstance(buildingsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(buildingsGdf, 'GeoDataFrame')
        self.buildingsGdf = buildingsGdf
        self.spatialIdx = buildingsGdf.sindex

        self.samplingDist = samplingDist

    def run(self):
        roiGeom = box(*self.buildingsGdf.total_bounds)

        # Sample the building contours
        _nodesGdf = STPointsDensifier(self.buildingsGdf, self.samplingDist).run()

        # Voronoi Diagram
        _voronoiGdf = STVoronoiPartition(_nodesGdf).run()

        pgeom = prep(unary_union(self.buildingsGdf.geometry))
        lls = []
        for geom in _voronoiGdf.geometry:
            lls.extend(filter(pgeom.disjoint, GeomLib.toListOfBipointsAsLineStrings(geom)))
        lls = linemerge(lls).intersection(roiGeom)

        return GeoDataFrame([{'gid': 1, 'geometry': lls}], crs=self.buildingsGdf.crs)
