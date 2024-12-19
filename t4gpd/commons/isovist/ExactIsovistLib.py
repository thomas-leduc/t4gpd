'''
Created on 25 nov. 2020

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from numpy import arange, cos, pi, sin
from pandas.core.common import flatten
from shapely import union_all
from shapely.geometry import box, CAP_STYLE, LineString, MultiLineString, Point, Polygon
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.PolarCartesianCoordinates import PolarCartesianCoordinates


class Pos(object):
    UNKNOWN = -1
    START = 0
    MID = 1
    STOP = 2


class ExactIsovistLib(object):
    '''
    classdocs
    '''
    EPSILON = 1e-2

    @staticmethod
    def __c2p(viewpoint, linestring):
        a, b = linestring.coords
        ar, at = PolarCartesianCoordinates.fromCartesianToPolarCoordinates(
            a[0] - viewpoint.x, a[1] - viewpoint.y)
        br, bt = PolarCartesianCoordinates.fromCartesianToPolarCoordinates(
            b[0] - viewpoint.x, b[1] - viewpoint.y)
        if pi > abs(bt - at):
            if (at < bt):
                return linestring, (ar, at), (br, bt)
            return LineString([b, a]), (br, bt), (ar, at)
        if (at < bt):
            return LineString([b, a]), (br, bt - 2 * pi), (ar, at)
        return linestring, (ar, at - 2 * pi), (br, bt)

    @staticmethod
    def __fromCartesianToPolarRadiusEquation(viewpoint, linestring):
        a, b = linestring.coords
        x1, y1 = a[0] - viewpoint.x, a[1] - viewpoint.y
        x2, y2 = b[0] - viewpoint.x, b[1] - viewpoint.y
        den = x1 * y2 - x2 * y1
        if (0.0 == den):
            # The straight line goes through the origin
            raise Exception('Unreachable instruction!')
        # Linear equation: ax + by = 1
        a, b = (y2 - y1) / den, (x1 - x2) / den
        return (lambda theta: (1.0 / (a * cos(theta) + b * sin(theta))))

    @staticmethod
    def __isHiddenBy(viewpoint, curr, other):
        # Returns True if 'other' is hidden by 'curr' when observing from 'viewpoint'
        cr1, ct1, cr2, ct2 = curr['r1'], curr['t1'], curr['r2'], curr['t2']
        or1, ot1, or2, ot2 = other['r1'], other['t1'], other['r2'], other['t2']

        if ((ct1 <= ot1 <= ot2 <= ct2) or
                ((ct1 < 0) and (360 + ct1 <= ot1 <= ot2 <= 360 + ct2))):
            if (max(cr1, cr2) < min(or1, or2)):
                return True
            a, b = other['geometry'].coords
            if (LineString([viewpoint.coords[0][0:2], a[0:2]]).intersects(curr['geometry']) and
                    LineString([viewpoint.coords[0][0:2], b[0:2]]).intersects(curr['geometry'])):
                return True
        return False

    @staticmethod
    def __decimationOfOpaqueEdges(buildings, viewpoint, maxRayLength):
        # Selection of buildings located in the region of interest
        roi = viewpoint.buffer(maxRayLength, cap_style=CAP_STYLE.square).bounds
        # ids = buildings.sindex.intersection(roi)
        # masks = [buildings.loc[_id].geometry for _id in ids]
        masks = list(filter(box(*roi).intersection, buildings.geometry))

        # Use a buffer to avoid slivers
        # masks = [mask.buffer(1e-3, join_style=JOIN_STYLE.mitre) for mask in masks]

        # Geometric union of buildings to remove party walls
        masks = union_all(masks)
        masks = masks.geoms if GeomLib.isMultipart(masks) else [masks]

        # Remove non-visible edges (badly oriented)
        masks = [GeomLib.normalizeRingOrientation(m) for m in masks]
        masks = list(
            flatten([GeomLib.toListOfBipointsAsLineStrings(m) for m in masks]))
        masks = [m for m in masks if GeomLib.isInFrontOf(viewpoint, m)]

        # From Cartesian to Polar coordinates (in the coordinates system centered on the viewpoint)
        masks = [{'tmp': ExactIsovistLib.__c2p(viewpoint, m)} for m in masks]

        masks = [{
            'geometry': m['tmp'][0],
            'r1': m['tmp'][1][0],
            't1': AngleLib.toDegrees(m['tmp'][1][1]),
            'r2': m['tmp'][2][0],
            't2': AngleLib.toDegrees(m['tmp'][2][1]),
        } for m in masks]

        # Sort edges according to angles (t1) and radii (r1)
        masks.sort(key=lambda m: (m['t1'], m['r1']), reverse=False)
        '''
        for i, m in enumerate(masks):  # DEBUG
            print(f"{i}:: t1: {m['t1']}, t2: {m['t2']}")  # DEBUG
        '''

        # Remove completely hidden edges (phase 1)
        hiddenEdgeIds, nEdges = set(), len(masks)
        for i, curr in enumerate(masks):
            if (not i in hiddenEdgeIds):
                for j in range(i + 1, nEdges):
                    if (not j in hiddenEdgeIds):
                        other = masks[j]
                        if ExactIsovistLib.__isHiddenBy(viewpoint, curr, other):
                            hiddenEdgeIds.add(j)

        for i in sorted(hiddenEdgeIds, reverse=True):
            del (masks[i])

        '''
        if (0 < len(masks)):  # DEBUG
            GeoDataFrame(masks, crs=buildings.crs).to_file('./x/__dbg1.shp')  # DEBUG
        '''

        # Remove completely hidden edges (phase 2)
        hiddenEdgeIds, nEdges = set(), len(masks)
        for i, curr in enumerate(masks):
            if (not i in hiddenEdgeIds):
                fin, stack, stackOfIdx = -1, [curr['geometry'].coords[0]], [i]
                for j in range(i + 1, nEdges):
                    if ((not j in hiddenEdgeIds) and
                            (curr['r2'] == masks[j]['r1']) and (curr['t2'] == masks[j]['t1'])):
                        fin, maxDist = j, max(
                            curr['r1'], curr['r2'], masks[j]['r1'], masks[j]['r2'])
                        stack.append(masks[j]['geometry'].coords[1])
                        stackOfIdx.append(j)
                        for k in range(j + 1, nEdges):
                            if ((not k in hiddenEdgeIds) and
                                    (masks[fin]['r2'] == masks[k]['r1']) and (masks[fin]['t2'] == masks[k]['t1'])):
                                fin, maxDist = k, max(
                                    maxDist, masks[k]['r1'], masks[k]['r2'])
                                stack.append(masks[k]['geometry'].coords[1])
                                stackOfIdx.append(k)

                if (-1 < fin):
                    fin, stack = masks[fin], LineString(stack)
                    for j in range(i + 1, nEdges):
                        if (not j in hiddenEdgeIds) and (j not in stackOfIdx):
                            other = masks[j]
                            if ((curr['t1'] <= other['t1'] <= other['t2'] <= fin['t2']) or
                                    ((360 + curr['t1'] < 0) and (curr['t1'] <= other['t1'] <= other['t2'] <= 360 + fin['t2']))):
                                if (maxDist < min(other['r1'], other['r2'])):
                                    hiddenEdgeIds.add(j)
                                else:
                                    a, b = other['geometry'].coords
                                    if (LineString([viewpoint.coords[0][0:2], a[0:2]]).intersects(stack) and
                                            LineString([viewpoint.coords[0][0:2], b[0:2]]).intersects(stack)):
                                        hiddenEdgeIds.add(j)

        for i in sorted(hiddenEdgeIds, reverse=True):
            del (masks[i])

        masks = [(x.update({'edge_id': i}), x)[1] for i, x in enumerate(masks)]

        '''
        if (0 < len(masks)):  # DEBUG
            GeoDataFrame(masks, crs=buildings.crs).to_file('./x/__dbg2.shp')  # DEBUG
        '''
        return GeoDataFrame(masks, crs=buildings.crs)

    @staticmethod
    def __fromOpaqueEdgesToNodes(edges, viewpoint, maxRayLength):
        # 1st step: put both ends of each opaque edge into a common "bag" (opaqueNodes)
        opaqueNodes = dict()
        for _, row in edges.iterrows():
            edgeId, r1, t1, r2, t2, geometry = row[[
                'edge_id', 'r1', 't1', 'r2', 't2', 'geometry']]

            # CONSIDER WHETHER maxRayLength < max(r1, r2)
            if (r1 <= maxRayLength) and (r2 <= maxRayLength):
                _pairOfNodes = [(r1, t1, Pos.START), (r2, t2, Pos.STOP)]
            else:
                _tmp = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(
                    geometry, viewpoint, maxRayLength)

                if ((r1 <= maxRayLength) and (maxRayLength < r2) and (1 == len(_tmp))):
                    _pairOfNodes = [geometry.coords[0][0:2], _tmp[0]]
                elif ((maxRayLength < r1) and (r2 <= maxRayLength) and (1 == len(_tmp))):
                    _pairOfNodes = [_tmp[0], geometry.coords[1][0:2]]
                elif ((maxRayLength < r1) and (maxRayLength < r2) and (2 == len(_tmp))):
                    _pairOfNodes = _tmp
                else:
                    _pairOfNodes = []

                if (0 < len(_pairOfNodes)):
                    _tmp = ExactIsovistLib.__c2p(
                        viewpoint, LineString(_pairOfNodes))
                    geometry = _tmp[0]
                    r1, t1 = _tmp[1][0], AngleLib.toDegrees(_tmp[1][1])
                    r2, t2 = _tmp[2][0], AngleLib.toDegrees(_tmp[2][1])
                    _pairOfNodes = [(r1, t1, Pos.START), (r2, t2, Pos.STOP)]
                    for fieldname, fieldvalue in [('r1', r1), ('t1', t1), ('r2', r2), ('t2', t2), ('geometry', geometry)]:
                        row[fieldname] = fieldvalue

            for r, t, pos in _pairOfNodes:
                _geom = geometry.coords[0] if (
                    Pos.START == pos) else geometry.coords[-1]
                t = t if (t >= 0) else (360 + t)
                _curr = {'edge_id': edgeId, 'r': r, 't': t,
                         'geometry': Point(_geom), 'pos': pos}
                if (t in opaqueNodes):
                    if (r in opaqueNodes[t]):
                        opaqueNodes[t][r].append(_curr)
                    else:
                        opaqueNodes[t][r] = [_curr]
                else:
                    opaqueNodes[t] = {r: [_curr]}

        # 2nd step: for each opaque edge, identify the set of covered azimuths
        for _, row in edges.iterrows():
            edgeId, t1, t2, linestring = row[[
                'edge_id', 't1', 't2', 'geometry']]
            _equ = ExactIsovistLib.__fromCartesianToPolarRadiusEquation(
                viewpoint, linestring)

            for t, _mapOfNodes in opaqueNodes.items():
                edgeIds = []
                for _listOfNodes in _mapOfNodes.values():
                    edgeIds += [_node['edge_id'] for _node in _listOfNodes]
                if (((t1 < t < t2) or ((t1 < 0) and (t1 < t - 360 < t2))) and
                        (edgeId not in edgeIds)):
                    _t_rad = AngleLib.toRadians(t)
                    r = _equ(_t_rad)
                    if (r < maxRayLength + ExactIsovistLib.EPSILON):
                        def _ppt(r, t): return Point(
                            (viewpoint.x + r * cos(t), viewpoint.y + r * sin(t)))
                        _curr = {'edge_id': edgeId, 'r': r, 't': t,
                                 'geometry': _ppt(r, _t_rad), 'pos': Pos.UNKNOWN}
                        if r in opaqueNodes[t]:
                            opaqueNodes[t][r].append(_curr)
                        else:
                            opaqueNodes[t][r] = [_curr]

        '''
        if (0 < len(opaqueNodes)):
            rows = []  # DEBUG
            for _k in opaqueNodes.keys():  # DEBUG
                for _kk in opaqueNodes[_k]:  # DEBUG
                    rows += opaqueNodes[_k][_kk]  # DEBUG
            GeoDataFrame(rows, crs='epsg:2154').to_file('./x/__dbg3.shp')  # DEBUG
    
            rows2 = []  # DEBUG
            for _row in rows:  # DEBUG
                _geom = LineString([ (viewpoint.x, viewpoint.y), (_row['geometry'].x, _row['geometry'].y)])  # DEBUG
                rows2.append({  # DEBUG
                    'geometry': _geom, 'edge_id': _row['edge_id'],  # DEBUG
                    'r': _row['r'], 't': _row['t'], 'pos': _row['pos']  # DEBUG
                    })  # DEBUG
            GeoDataFrame(rows2, crs='epsg:2154').to_file('./x/__dbg4.gpkg')  # DEBUG
        '''

        return opaqueNodes

    @staticmethod
    def __decimationOfOpaqueNodes(nodes, viewpoint, maxRayLength):
        opaqueNodes = dict()

        # 1st step: remove hidden nodes
        for t in nodes.keys():
            opaqueNodes[t] = dict()
            for r in sorted(nodes[t].keys()):
                nNodes = len(nodes[t][r])

                if (1 == nNodes):
                    currNode = nodes[t][r][0]
                    currNode['edge_id'] = str(currNode['edge_id'])
                    opaqueNodes[t][r] = currNode
                    if (Pos.UNKNOWN == currNode['pos']):
                        # do not store all nodes beyond an intermediate node
                        opaqueNodes[t][r]['pos'] = Pos.MID
                        break
                    elif ((Pos.START == currNode['pos']) and Epsilon.equals(currNode['r'], maxRayLength, ExactIsovistLib.EPSILON)):
                        # do not store nodes beyond an extreme one
                        break

                elif (2 == nNodes):
                    n1, n2 = nodes[t][r]

                    # TODO: add one more test regarding possible edge alignment
                    if (((n1['pos'] in [Pos.STOP, Pos.UNKNOWN]) and (Pos.START == n2['pos'])) or
                            ((Pos.STOP == n1['pos']) and (n2['pos'] in [Pos.START, Pos.UNKNOWN]))):
                        _ids = ArrayCoding.encode(
                            [n1['edge_id'], n2['edge_id']])
                    elif (((Pos.START == n1['pos']) and (n2['pos'] in [Pos.STOP, Pos.UNKNOWN])) or
                          ((n1['pos'] in [Pos.START, Pos.UNKNOWN]) and (Pos.STOP == n2['pos']))):
                        _ids = ArrayCoding.encode(
                            [n2['edge_id'], n1['edge_id']])
                    else:
                        raise Exception('Unreachable instruction!')

                    opaqueNodes[t][r] = {
                        'edge_id': _ids, 'r': r, 't': t, 'geometry': n1['geometry'], 'pos': Pos.MID}
                    # do not store all nodes beyond a pair of start and end nodes
                    break

                else:
                    raise Exception('Unreachable instruction!')

        '''
        if (0 < len(opaqueNodes)):  # DEBUG
            rows = []  # DEBUG
            for _k in opaqueNodes.keys():  # DEBUG
                for _kk in opaqueNodes[_k]:  # DEBUG
                    rows.append(opaqueNodes[_k][_kk])  # DEBUG
            GeoDataFrame(rows, crs='epsg:2154').to_file('./x/__dbg5.shp')  # DEBUG
        '''

        # 2nd step: build the ordered list of contour points
        ctrPts = []
        for t in sorted(opaqueNodes.keys()):
            _nNodes = len(opaqueNodes[t])
            if 0 < _nNodes:
                _curr = list(opaqueNodes[t].values())[0]

                if (1 == _nNodes):
                    ctrPts.append(_curr)

                else:
                    if (Pos.STOP == _curr['pos']):
                        _rev = False
                    elif (Pos.START == _curr['pos']):
                        _rev = True
                    else:
                        raise Exception('Unreachable instruction!')
                    for r in sorted(opaqueNodes[t], reverse=_rev):
                        ctrPts.append(opaqueNodes[t][r])

        '''
        if (0 < len(ctrPts)):  # DEBUG
            GeoDataFrame(ctrPts, crs='epsg:2154').to_file('./x/__dbg6.shp')  # DEBUG
        '''

        return ctrPts

    @staticmethod
    def __addAnArtificialPoint(viewpoint, maxRayLength, theta):
        _t_rad = AngleLib.toRadians(theta)
        _geom = Point((
            viewpoint.x + maxRayLength * cos(_t_rad),
            viewpoint.y + maxRayLength * sin(_t_rad)))
        return {
            'edge_id': None,
            'r': maxRayLength,
            't': theta % 360,
            'geometry': _geom,
            'pos': Pos.UNKNOWN
        }

    @staticmethod
    def __addSetOfArtificialPoints(viewpoint, maxRayLength, theta1, theta2, delta):
        result = []
        for _t in arange(theta1, theta2, delta):
            result.append(ExactIsovistLib.__addAnArtificialPoint(
                viewpoint, maxRayLength, _t))
        if (_t < theta2):
            result.append(ExactIsovistLib.__addAnArtificialPoint(
                viewpoint, maxRayLength, theta2))
        return result

    @staticmethod
    def __addAnArtificialHorizon(nodes, viewpoint, maxRayLength, delta):
        ctrPts = []
        if (0 == len(nodes)):
            ctrPts = ExactIsovistLib.__addSetOfArtificialPoints(
                viewpoint, maxRayLength, 0, 360, delta)

        elif (2 == len(nodes)):
            if (Pos.START == nodes[0]['pos']) and (Pos.STOP == nodes[1]['pos']):
                _start, _stop = nodes
            elif (Pos.STOP == nodes[0]['pos']) and (Pos.START == nodes[1]['pos']):
                _stop, _start = nodes
            else:
                raise Exception('Unreachable instruction!')

            _t0 = _stop['t']
            _t1 = (_start['t'] + 360) if (_stop['t']
                                          > _start['t']) else _start['t']

            ctrPts.append(_stop)
            ctrPts += ExactIsovistLib.__addSetOfArtificialPoints(
                viewpoint, maxRayLength, _t0, _t1, delta)
            ctrPts.append(_start)

        else:
            for i, _curr in enumerate(nodes):
                _prev = nodes[i - 1]
                if ((_prev['edge_id'] != _curr['edge_id']) and
                    ((Pos.STOP == _prev['pos']) or ((Pos.MID == _prev['pos']) and (Epsilon.equals(_prev['r'], maxRayLength, ExactIsovistLib.EPSILON)))) and
                        ((Pos.START == _curr['pos']) or ((Pos.MID == _curr['pos']) and (Epsilon.equals(_curr['r'], maxRayLength, ExactIsovistLib.EPSILON))))):

                    _t0 = _prev['t']
                    _t1 = (_curr['t']) if (_prev['t'] <
                                           _curr['t']) else (_curr['t'] + 360)

                    ctrPts += ExactIsovistLib.__addSetOfArtificialPoints(
                        viewpoint, maxRayLength, _t0, _t1, delta)

                ctrPts.append(_curr)
        return ctrPts

    @staticmethod
    def __anticipation(viewpoint, occludingSurfaces):
        _anticip = 0
        for _occl in occludingSurfaces.geoms:
            _FgBg = _occl.length
            _VpFg, _VpBg = [viewpoint.distance(Point(c)) for c in _occl.coords]
            _VpFg, _VpBg = min(_VpFg, _VpBg), max(_VpFg, _VpBg)
            _anticip += (_VpBg * _FgBg) / _VpFg
        return _anticip

    @staticmethod
    def __buildTheIsovist(viewpoint, nodes, crs):
        def __intersects(l1, l2): return 0 < len(
            set(l1.split('#')).intersection(set(l2.split('#'))))

        _isovist = Polygon([(p['geometry'].x, p['geometry'].y) for p in nodes])
        _isovist_perim = _isovist.length

        # Artificial Horizon, material and occluding surfaces
        _artificialHorizon = []
        _materialSurfaces = []
        _occludingSurfaces = []

        for i, _curr in enumerate(nodes):
            _prev = nodes[i - 1]

            if (_prev['edge_id'] is None) and (_curr['edge_id'] is None):
                _edge = LineString((_prev['geometry'], _curr['geometry']))
                _artificialHorizon.append(_edge)

            elif ((_prev['edge_id'] is not None) and (_curr['edge_id'] is not None)):
                _a = GeomLib.removeZCoordinate(_prev['geometry'])
                _b = GeomLib.removeZCoordinate(_curr['geometry'])
                _edge = LineString((_a, _b))

                if __intersects(_prev['edge_id'], _curr['edge_id']):
                    _materialSurfaces.append(_edge)
                else:
                    _occludingSurfaces.append(_edge)

            else:
                _a = GeomLib.removeZCoordinate(_prev['geometry'])
                _b = GeomLib.removeZCoordinate(_curr['geometry'])
                _edge = LineString((_a, _b))
                _occludingSurfaces.append(_edge)

        _artificialHorizon = MultiLineString(_artificialHorizon)
        _skyline_1 = _artificialHorizon.length
        _skyline_2 = _skyline_1 / _isovist_perim

        _materialSurfaces = MultiLineString(_materialSurfaces)
        _solidness_1 = _materialSurfaces.length
        _solidness_2 = _solidness_1 / _isovist_perim

        _occludingSurfaces = MultiLineString(_occludingSurfaces)
        _occlusivity_1 = _occludingSurfaces.length
        _occlusivity_2 = _occlusivity_1 / _isovist_perim

        _isovist = {
            'geometry': _isovist,
            'perim': _isovist_perim,
            'occlusiv': _occlusivity_1,
            'occlusiv_r': _occlusivity_2,
            'solid': _solidness_1,
            'solid_r': _solidness_2,
            'skyline': _skyline_1,
            'skyline_r': _skyline_2,
            'anticipati': ExactIsovistLib.__anticipation(viewpoint, _occludingSurfaces),
            'nodes': nodes,
            'artif_hori': _artificialHorizon,
            'solid_surf': _materialSurfaces,
            'occlu_surf': _occludingSurfaces,
        }
        return _isovist

    @staticmethod
    def run(buildings, viewpoint, maxRayLength, delta=10.0):
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(
                buildings, 'buildings GeoDataFrame')
        if not isinstance(viewpoint, Point):
            raise IllegalArgumentTypeException(viewpoint, 'Point')

        edges = ExactIsovistLib.__decimationOfOpaqueEdges(
            buildings, viewpoint, maxRayLength)
        nodes = ExactIsovistLib.__fromOpaqueEdgesToNodes(
            edges, viewpoint, maxRayLength)
        nodes = ExactIsovistLib.__decimationOfOpaqueNodes(
            nodes, viewpoint, maxRayLength)
        nodes = ExactIsovistLib.__addAnArtificialHorizon(
            nodes, viewpoint, maxRayLength, delta)

        return ExactIsovistLib.__buildTheIsovist(viewpoint, nodes, buildings.crs)
