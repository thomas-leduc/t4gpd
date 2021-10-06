'''
Created on 28 sept. 2020

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
from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.graph.UrbanGraphLibOld import UrbanGraphLibOld
from t4gpd.morph.STVoronoiPartition import STVoronoiPartition

from t4gpd.morph.STPointsDensifier import STPointsDensifier


class STSkeletonize(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, samplingDist=10.0):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        self.samplingDist = samplingDist

    def __skeletonizePolygon(self, shapeGeom):
        # Use a buffer to avoid slivers
        shapeGeom = shapeGeom.buffer(0.001)
        prepShapeGeom = prep(shapeGeom)

        # Sample the building contours
        _currGdf = GeoDataFrame([{ 'geometry': shapeGeom }])
        _nodesGdf = STPointsDensifier(_currGdf, self.samplingDist).run()

        if (5 < len(_nodesGdf)):
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
                            _currGeom = LineString((_prev, _curr))
                            if prepShapeGeom.contains(_currGeom):
                                _ug.add(_currGeom)
                        _prev = _curr
            return unary_union([rs['geometry'] for rs in _ug.getUniqueRoadsSections()])

        return LineString()  # Empty geometry

    def run(self):
        rows = []
        for _, row in self.inputGdf.iterrows():
            geom = row.geometry
            if isinstance(geom, Polygon):
                edges = self.__skeletonizePolygon(geom)
                if (0 < edges.length):
                    rows.append(self.updateOrAppend(row, { 'geometry': edges }))
            elif isinstance(geom, MultiPolygon):
                listOfEdges = []
                for _geom in geom.geoms:
                    edges = self.__skeletonizePolygon(geom)
                    if (0 < edges.length):
                        listOfEdges.append(edges)
                edges = unary_union(listOfEdges)
                if (0 < edges.length):
                    rows.append(self.updateOrAppend(row, { 'geometry': edges }))

        return GeoDataFrame(rows, crs=self.inputGdf.crs)
