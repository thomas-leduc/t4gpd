'''
Created on 24 feb. 2021

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
from t4gpd.commons.GeomLib import GeomLib
from shapely.geometry import box, MultiPolygon, Polygon


class KernelLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def __getInteriorHalfPlanePolygon(a, b, bbox):
        minx, miny, maxx, maxy = bbox

        llc = [minx, miny]
        lrc = [maxx, miny]
        ulc = [minx, maxy]
        urc = [maxx, maxy]
        ap = KernelLib.__projectOntoEnvelope(a, b, bbox)
        bp = KernelLib.__projectOntoEnvelope(b, a, bbox)
        result = [bp, ap]
        
        if (a[0] == b[0]):
            if (a[1] > b[1]):
                result.append(lrc)
                result.append(urc)
            elif (a[1] < b[1]):
                result.append(ulc)
                result.append(llc)
            else:
                raise Exception('Points a and b are equals !')
        elif (a[0] < b[0]):
            if (a[1] == b[1]):
                result.append(urc)
                result.append(ulc)
            elif (a[1] < b[1]):
                if (KernelLib.__isOnTheLeftOfABSegment(a, b, urc)):
                    result.append(urc)
                result.append(ulc);
                if (KernelLib.__isOnTheLeftOfABSegment(a, b, llc)):
                    result.append(llc)
            else:  # a[1] > b[1]
                if (KernelLib.__isOnTheLeftOfABSegment(a, b, lrc)):
                    result.append(lrc)
                result.append(urc)
                if (KernelLib.__isOnTheLeftOfABSegment(a, b, ulc)):
                    result.append(ulc)
        else:  # a[0] > b[0]
            if (a[1] == b[1]):
                result.append(llc)
                result.append(lrc)
            elif (a[1] < b[1]):
                if (KernelLib.__isOnTheLeftOfABSegment(a, b, ulc)):
                    result.append(ulc)
                result.append(llc)
                if (KernelLib.__isOnTheLeftOfABSegment(a, b, lrc)):
                    result.append(lrc)
            else:  # a[1] > b[1]
                if (KernelLib.__isOnTheLeftOfABSegment(a, b, llc)):
                    result.append(llc)
                result.append(lrc)
                if (KernelLib.__isOnTheLeftOfABSegment(a, b, urc)):
                    result.append(urc)
        result.append(bp)
        return result

    @staticmethod
    def getKernel(geom):
        if ((not GeomLib.isPolygonal(geom)) or
            (GeomLib.isHoled(geom)) or
            ((isinstance(geom, MultiPolygon)) and (1 != len(geom.geoms)))):
            return None, False

        if GeomLib.isConvex(geom):
            return GeomLib.normalizeRingOrientation(geom), True

        if isinstance(geom, MultiPolygon):
            geom = geom.geoms[0]

        polygon = GeomLib.normalizeRingOrientation(geom)
        bbox = polygon.bounds

        kernel = box(*bbox)
        _coords = polygon.exterior.coords
        for i in range(1, len(_coords)):
            tmp = KernelLib.__getInteriorHalfPlanePolygon(
                _coords[i - 1], _coords[i], bbox)
            tmp = Polygon(tmp)
            kernel = kernel.intersection(tmp)
            # kernel.isEmpty() n'est pas equivalent a : 0.0 == kernel.area
            if (kernel.is_empty) or (0.0 == kernel.area):
                return None, False

        return kernel, True

    @staticmethod
    def __isOnTheLeftOfABSegment(a, b, p):
        # Test if z component of (AB x AP) >= 0
        return (0.0 <= ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])))

    @staticmethod
    def __projectOntoEnvelope(p, q, bbox):
        minx, miny, maxx, maxy = bbox
        # This method returns the projection of point p on the envelope in the
        # direction of point q.
        if (p[0] == q[0]):
            if (p[1] < q[1]):
                return [q[0], maxy]
            elif (p[1] > q[1]):
                return [q[0], miny]
            else:
                raise Exception('Points p and q are equals!');

        elif (p[0] < q[0]):
            x0 = maxx
            y0 = p[1] + ((x0 - p[0]) * (q[1] - p[1])) / (q[0] - p[0])

            if ((miny <= y0) and (y0 <= maxy)):
                return [x0, y0]
            else:
                if (p[1] == q[1]):
                    raise Exception('Should not happen !')
                    # return [x0, y0]
                elif (p[1] < q[1]):
                    y0 = maxy
                else:
                    y0 = miny
                x0 = p[0] + ((q[0] - p[0]) * (y0 - p[1])) / (q[1] - p[1])
                return [x0, y0]

        else:  # p[0] > q[0]
            x0 = minx
            y0 = p[1] + ((x0 - p[0]) * (q[1] - p[1])) / (q[0] - p[0])

            if ((miny <= y0) and (y0 <= maxy)):
                return [x0, y0]
            else:
                if (p[1] == q[1]):
                    raise Exception('Should not happen !')
                    # return [x0, y0]
                elif (p[1] < q[1]):
                    y0 = maxy
                else:
                    y0 = miny
                x0 = p[0] + ((q[0] - p[0]) * (y0 - p[1])) / (q[1] - p[1])
                return [x0, y0]
