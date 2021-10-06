'''
Created on 8 oct. 2020

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
from builtins import isinstance
from datetime import datetime
from warnings import warn

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class ObjWriter(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, outputFile):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        self.outputFile = outputFile

    def __dumpVertex(self, coords):
        z = 0.0
        if 2 == len(coords):
            x, y = coords
        elif 3 == len(coords):
            x, y, z = coords
        return 'v %.5f %.5f %.5f\n' % (x, y, z)
        # return 'v %g %g %g\n' % (x, y, z)

    def __dumpListOfVertices(self, myDictOfVertices, vertices):
        return ' '.join([str(myDictOfVertices[vtx]) for vtx in vertices])

    def run(self):
        myDictOfVertices, myListOfLines, myListOfFaces = dict(), [], []

        for _, row in self.inputGdf.iterrows():
            geom = row.geometry

            points = GeomLib.getListOfShapelyPoints(geom)
            for _p in points:
                p = _p.coords[0]
                if p not in myDictOfVertices:
                    myDictOfVertices[p] = 1 + len(myDictOfVertices)

            if isinstance(geom, Polygon):
                myListOfFaces.append(list(geom.exterior.coords))
            elif isinstance(geom, LineString):
                myListOfLines.append(geom.coords)
            else:
                warn('ObjWriter deals only with LineString and Polygon!')

        with open(self.outputFile, 'w') as out:
            out.write('# t4gpd.io.ObjWriter - dev. in 2020, by T. Leduc, AAU-CRENAU\n')
            out.write('# OBJ generated on %s\n\n' % (datetime.now().strftime("%d.%m.%Y at %H:%M:%S")))
            out.write('# ===== %d vertices =====\n\n' % (len(myDictOfVertices)))

            for p, _ in sorted(myDictOfVertices.items(), key=lambda kv:kv[1]):
                out.write(self.__dumpVertex(p))

            if 0 < len(myListOfFaces):
                out.write('\n# ===== %d face(s) =====\n' % (len(myListOfFaces)))
                for i, f in enumerate(myListOfFaces, start=1):
                    out.write('\ng %d\n' % (i))
                    out.write('f %s\n' % (self.__dumpListOfVertices(myDictOfVertices, f)))

            if 0 < len(myListOfLines):
                out.write('\n# ===== %d polyline(s) =====\n\n' % (len(myListOfLines)))
                for l in myListOfLines:
                    out.write('l %s\n' % (self.__dumpListOfVertices(myDictOfVertices, l)))
