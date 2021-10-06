'''
Created on 23 oct. 2020

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
from random import randrange
from shapely.affinity import rotate

from geopandas.geodataframe import GeoDataFrame
from numpy import arctan2, cos, pi, sin
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union


class LandoltRingLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def c_optotype(centre, diameter, angleInDegrees=0, npoints=40):
        r = diameter / 2
        angle0 = arctan2(diameter / 10, r)
        deltaAngle = 2 * (pi - angle0) / (npoints - 1)
        ctrPoints = [
            (centre.x + r * cos(angle0 + i * deltaAngle), centre.y + r * sin(angle0 + i * deltaAngle))
            for i in range(npoints)
            ]

        r = 3 * diameter / 10
        angle0 = arctan2(diameter / 10, r)
        deltaAngle = 2 * (pi - angle0) / (npoints - 1)
        ctrPoints += [
            (centre.x + r * cos(angle0 + i * deltaAngle), centre.y + r * sin(angle0 + i * deltaAngle))
            for i in range(npoints)
            ][::-1]

        optotype = Polygon(ctrPoints)
        if 0 == angleInDegrees:
            return optotype
        return rotate(optotype, angleInDegrees, origin=centre)

    @staticmethod
    def c_chart(diameter, nrows=2, ncols=5, npoints=40):
        x0, y0, rows = diameter, diameter, []

        for l in range(nrows):
            for c in range(ncols):
                angleInDegrees = randrange(0, 360, 45)
                centre = Point((x0 + c * 2 * diameter, y0 + l * 2 * diameter))
                geom = LandoltRingLib.c_optotype(centre, diameter, angleInDegrees, npoints=npoints)
                rows.append({'gid': l * ncols + c, 'row':l, 'col':c, 'geometry':geom})

        return GeoDataFrame(rows)

    @staticmethod
    def a4landscape_c_chart(negativeContrast=True, diameter=None, nrows=2, ncols=5, npoints=40):
        width, height = 842, 595  # A4 landscape
        if diameter is None:
            diameter = min(height / nrows, width / ncols) / 2 
        x0, y0 = diameter, diameter

        holes = []
        for l in range(nrows):
            for c in range(ncols):
                angleInDegrees = randrange(0, 360, 45)
                centre = Point((x0 + c * 2 * diameter, y0 + l * 2 * diameter))
                holes.append(LandoltRingLib.c_optotype(centre, diameter, angleInDegrees, npoints=npoints))

        bbCoords = [(0, 0), (width, 0), (width, height), (0, height)]
        if negativeContrast:
            geom = Polygon(bbCoords)
            rows = [{ 'geometry':  geom.difference(unary_union(holes)) }]
        else:
            geom = Polygon(bbCoords, [[(1, 1), (1, height - 1), (width - 1, height - 1), (width - 1, 1)]])
            rows = [{ 'geometry':  geom.union(unary_union(holes)) }]
        return GeoDataFrame(rows)

'''
from t4gpd.io.SVGWriter import SVGWriter
gdf = LandoltRingLib.a4landscape_c_chart(True)
SVGWriter(gdf, './n_c_chart.svg').run()
# inkscape --export-pdf=n_c_chart.pdf n_c_chart.svg

gdf = LandoltRingLib.a4landscape_c_chart(False)
SVGWriter(gdf, './p_c_chart.svg').run()
# inkscape --export-pdf=p_c_chart.pdf p_c_chart.svg
'''
