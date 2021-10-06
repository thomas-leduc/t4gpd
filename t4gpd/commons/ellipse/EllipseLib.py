'''
Created on 23 juin 2020

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
from numpy import cos, isnan, linspace, math, pi, prod, sin, sqrt
from shapely.geometry import LineString, Point, Polygon


class EllipseLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def getEllipseContour(centre, semiXAxis, semiYAxis, azim, npoints=40):
        x0, y0 = centre.x, centre.y
        if isnan(azim):
            # CIRCLE
            result = Polygon([Point((x0 + semiXAxis * cos(t), y0 + semiXAxis * sin(t))) for t in linspace(0, 2 * pi, npoints)])
        else:
            if (semiXAxis < semiYAxis):
                azim = (azim + pi / 2.0) if (azim < 0) else (azim - pi / 2.0)
            result = Polygon([EllipseLib.parametricEquation(x0, y0, semiXAxis, semiYAxis, azim, t) for t in linspace(0, 2 * pi, npoints)])
        # result[-1] = result[0]
        return result

    @staticmethod
    def getEllipseMainAxis(centre, semiXAxis, semiYAxis, azim):
        if isnan(azim):
            return None

        semiAxis = semiXAxis if (semiXAxis >= semiYAxis) else semiYAxis
        p1 = Point((centre.x - semiAxis * cos(azim), centre.y - semiAxis * sin(azim)))
        p2 = Point((centre.x + semiAxis * cos(azim), centre.y + semiAxis * sin(azim)))
        return LineString((p1, p2))

    @staticmethod
    def getEllipsePerimeter(semiXAxis, semiYAxis, order=None):
        return EllipseLib.__getEllipsePerimeter_ramanujan(semiXAxis, semiYAxis)
        # return EllipseLib.__getEllipsePerimeter_infinite_series(semiXAxis, semiYAxis)

    @staticmethod
    def __getEllipsePerimeter_ramanujan(semiXAxis, semiYAxis):
        # https://en.wikipedia.org/wiki/Ellipse
        # According to Ramanujan 2nd formula
        diff = semiXAxis - semiYAxis
        summ = semiXAxis + semiYAxis
        if (0.0 == summ):
            return 0.0
        h = diff * diff / (summ * summ)
        perim = pi * summ * (1.0 + (3.0 * h) / (10.0 + sqrt(4.0 - 3.0 * h)))
        return float(perim)

    @staticmethod
    def __doubleFactorial(n):
        # https://en.wikipedia.org/wiki/Double_factorial
        # 9!! = 9 * 7 * 5 * 3 * 1 = 945
        # 8!! = 8 * 6 * 4 * 2 = 384
        return prod(list(range(n, 1, -2)))

    @staticmethod
    def __getEllipsePerimeter_infinite_series(semiXAxis, semiYAxis, order=100):
        diff = semiXAxis - semiYAxis
        summ = semiXAxis + semiYAxis
        if (0.0 == summ):
            return 0.0
        h = diff * diff / (summ * summ)

        acc = 1.0 + 0.25 * h
        for n in range(2, order):
            tmp = EllipseLib.__doubleFactorial(2 * n - 3) / ((2 ** n) * math.factorial(n))
            acc += tmp * tmp * h ** n
        return float(pi * summ * acc)

    @staticmethod
    def parametricEquation(x0, y0, semiXAxis, semiYAxis, theta, t):
        x = x0 + semiXAxis * cos(theta) * cos(t) - semiYAxis * sin(theta) * sin(t)
        y = y0 + semiXAxis * sin(theta) * cos(t) + semiYAxis * cos(theta) * sin(t)
        return ((x, y))
