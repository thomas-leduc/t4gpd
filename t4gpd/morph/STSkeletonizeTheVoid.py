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
from shapely.geometry import LineString
from t4gpd.commons.BoundingBox import BoundingBox
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.graph.UrbanGraphLibOld import UrbanGraphLibOld
from t4gpd.morph.STVoronoiPartition import STVoronoiPartition

from t4gpd.morph.STPointsDensifier import STPointsDensifier


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
        roiGeom = BoundingBox(self.buildingsGdf).asPolygon()

        # Sample the building contours
        _nodesGdf = STPointsDensifier(self.buildingsGdf, self.samplingDist).run()

        # Voronoi Diagram
        _voronoiGdf = STVoronoiPartition(_nodesGdf).run()

        # Remove useless edges
        _ug = UrbanGraphLibOld()
        for _, row in _voronoiGdf.iterrows():
            _edges = GeomLib.toListOfLineStrings(row.geometry)
            for _edge in _edges:
                _prev = None
                for _curr in _edge.coords:
                    if _prev is not None:
                        keep = True
                        _currGeom = LineString((_prev, _curr))
                        _buildingsIds = self.spatialIdx.intersection(_currGeom.bounds)
                        for _buildingId in _buildingsIds:
                            _buildingGeom = self.buildingsGdf.loc[_buildingId].geometry
                            if _currGeom.intersects(_buildingGeom):
                                keep = False
                                break
                        if keep:
                            _ug.add(_currGeom.intersection(roiGeom))
                    _prev = _curr

        rows = _ug.getUniqueRoadsSections()
        return GeoDataFrame(rows, crs=self.buildingsGdf.crs)
