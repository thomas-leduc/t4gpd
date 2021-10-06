'''
Created on 17 juin 2020

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
from numpy import ceil
from shapely.affinity import translate
from shapely.geometry import LineString, Polygon

from t4gpd.commons.BoundingBox import BoundingBox
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class SVGWriter(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, outputFile, bbox=None, color='black'):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        self.outputFile = outputFile
        self.bbox = BoundingBox(self.inputGdf) if bbox is None else BoundingBox(bbox)
        self.color = color

    def __convertListOfCoords(self, height, coords):
        n = len(coords)
        return ' '.join(["%c %g,%g" % ('M' if (0 == i) else 'L', coords[i][0], height - coords[i][1]) for i in range(n)])

    def __convertGeom(self, height, geom):
        if isinstance(geom, LineString):
            tmp = self.__convertListOfCoords(height, geom.coords)
            return '\t<path d="%s" style="fill:none;stroke:%s;stroke-width:3.0" />\n' % (tmp, self.color)

        elif isinstance(geom, Polygon):
            rings = [geom.exterior] + list(geom.interiors)
            tmp = ''.join([self.__convertListOfCoords(height, ring.coords) + ' z ' for ring in rings])
            return '\t<path d="%s" style="fill:%s;stroke:white;stroke-width:0.025" />\n' % (tmp, self.color)

        return ''

    def run(self):
        x0, y0, h, w = self.bbox.minx, self.bbox.miny, self.bbox.height(), self.bbox.width()

        with open(self.outputFile, 'w') as f: 
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
            f.write('<svg height="%d" width="%d">\n' % (ceil(h), ceil(w)))

            for _, row in self.inputGdf.iterrows():
                geom = row.geometry
                geom = translate(geom, -x0, -y0)
                
                if GeomLib.isMultipart(geom):
                    for g in geom.geoms:
                        f.write(self.__convertGeom(h, g))
                else:
                    f.write(self.__convertGeom(h, geom))

            f.write('</svg>\n')
