'''
Created on 22 nov. 2020

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
import copy

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point

from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.graph.AbstractUrbanGraphLib import AbstractUrbanGraphLib
from t4gpd.commons.graph.ShortestPathLib import ShortestPathLib


class NeighborhoodLib(AbstractUrbanGraphLib):
    '''
    classdocs
    '''

    @staticmethod
    def neighborhood(roads, fromPoint, maxDist):
        roi = fromPoint.buffer(maxDist, 1).bounds
        mygraph = ShortestPathLib(roads, roi)

        str_coord = AbstractUrbanGraphLib.hashCoord([fromPoint.x, fromPoint.y])
        if not str_coord in mygraph.ciVertices:
            _, nearestLine = AbstractUrbanGraphLib.addEndPoint(
                roads, roads.sindex, mygraph.graph, mygraph.ciVertices, mygraph.icVertices, mygraph.edges, fromPoint)

            _foo = lambda coord: mygraph.ciVertices[AbstractUrbanGraphLib.hashCoord(coord)]
            first, last = _foo(nearestLine.coords[0]), _foo(nearestLine.coords[-1])
            if (first in mygraph.edges) and (last in mygraph.edges[first]):
                del(mygraph.edges[first][last])
            if (last in mygraph.edges) and (first in mygraph.edges[last]):
                del(mygraph.edges[last][first])

        _icVertices = copy.deepcopy(mygraph.icVertices)

        # Identification of vertices in the neighborhood
        candidates = dict()
        for _vtxIdx, _vtxGeom in _icVertices.items():
            _geom = Point(_vtxGeom)
            if (maxDist >= fromPoint.distance(_geom)):
                pathGeom, pathLen = mygraph.shortestPath(fromPoint, _geom)
                if (pathGeom is not None) and (maxDist >= pathLen):
                    candidates[_vtxIdx] = maxDist - pathLen

        # Identification of edges in the neighborhood
        _burnedEdges, rows, gid = dict(), [], 0
        for _vtxIdx in candidates.keys():
            _remainingDist = candidates[_vtxIdx]
            for _neighborIdx in mygraph.edges[_vtxIdx].keys():
                _hash = '%d_%d' % (min(_neighborIdx, _vtxIdx), max(_neighborIdx, _vtxIdx))
                if _hash not in _burnedEdges:
                    _edgeItem = mygraph.edges[_vtxIdx][_neighborIdx]
                    if (_remainingDist >= _edgeItem['length']):
                        rows.append({ 'gid': gid, 'geometry': _edgeItem['geometry'], 'length': _edgeItem['length']})
                        _burnedEdges[_hash] = None
                        gid += 1

                    elif (_neighborIdx in candidates):
                        if ((candidates[_neighborIdx] >= _edgeItem['length']) or
                            (_remainingDist + candidates[_neighborIdx] >= _edgeItem['length'])):
                            rows.append({ 'gid': gid, 'geometry': _edgeItem['geometry'], 'length': _edgeItem['length']})
                            _burnedEdges[_hash] = None
                            gid += 1
                        else:
                            tmp = GeomLib.cutsLineStringByCurvilinearDistance(_edgeItem['geometry'], _remainingDist)
                            rows.append({ 'gid': gid, 'geometry': tmp[0], 'length': _remainingDist})
                            _burnedEdges[_hash] = None
                            gid += 1

                            _otherEdgeItem = mygraph.edges[_neighborIdx][_vtxIdx]
                            tmp = GeomLib.cutsLineStringByCurvilinearDistance(_otherEdgeItem['geometry'], candidates[_neighborIdx])
                            rows.append({ 'gid': gid, 'geometry': tmp[0], 'length': candidates[_neighborIdx]})
                            gid += 1

                    else:
                        tmp = GeomLib.cutsLineStringByCurvilinearDistance(_edgeItem['geometry'], _remainingDist)
                        rows.append({ 'gid': gid, 'geometry': tmp[0], 'length': _remainingDist})
                        _burnedEdges[_hash] = None
                        gid += 1
        '''
        rows2 = []
        for vtxIdx in candidates.keys():
            rows2.append({'gid':vtxIdx, 'remain_dist': candidates[vtxIdx], 'geometry': Point(mygraph.icVertices[vtxIdx])})
        return GeoDataFrame(rows, crs=roads.crs), GeoDataFrame(rows2, crs=roads.crs)
        '''
        return GeoDataFrame(rows, crs=roads.crs)
