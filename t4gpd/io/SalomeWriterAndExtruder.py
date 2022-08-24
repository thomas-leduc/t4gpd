'''
Created on 22 juil. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
from datetime import datetime
from os.path import splitext

from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.io.SalomeWriter import SalomeWriter


class SalomeWriterAndExtruder(SalomeWriter):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, outputFile, elevationFieldname='HAUTEUR',
                 withFaceIds=False, exportBrep=True):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        self.outputFile = splitext(outputFile)[0]

        if elevationFieldname not in inputGdf:
                raise Exception(f'{elevationFieldname} is not a relevant field name!')
        self.elevationFieldname = elevationFieldname

        self.withFaceIds = withFaceIds
        self.exportBrep = exportBrep

    def _dumpBody(self, out):
        cntFaces, cntCtrs, cntNodes = 1, 1, 1
        
        for _, row in self.inputGdf.iterrows():
            geom = row.geometry
            elevation = row[self.elevationFieldname]
            if ('Polygon' == geom.geom_type):
                cntFaces, cntCtrs, cntNodes = self._dumpPolygon(out, geom, elevation, cntFaces, cntCtrs, cntNodes)
            else:
                print(f'SalomeWriter does not handle {geom.geom_type}!')

    def _dumpHeader(self, out):
        out.write(f'''"""
# t4gpd (SalomeWriterAndExtruder), {datetime.now().strftime('%Y-%m-%d %X')}
# ================================================================
# To be copied and pasted into SALOME's console:
with open('{self.outputFile}.py') as f:
    exec(compile(f.read(), '{self.outputFile}.py', 'exec'))
# ================================================================
"""
import sys
sys.stdout.flush()
import salome
salome.salome_init()
import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()
gg = salome.ImportComponentGUI('GEOM')
isPlanarWanted = 1

# ================================================================
''')

    def _dumpPolygon(self, out, geom, elevation, cntFaces, cntCtrs, cntNodes):
        out.write(f'\n# ===== FACE {cntFaces}: CONTOUR {cntCtrs} =====\n')
        cntNode0 = cntNodes
        cntFaces, cntCtrs, cntNodes = self._dumpLinearRing(
            out, geom.exterior, cntFaces, cntCtrs, cntNodes, lbl=str(cntFaces))

        if GeomLib.isHoled(geom):
            nHoles = len(geom.interiors)
            out.write(f'\n# -- Subtract {nHoles} hole(s) --\n')
            for numHole, hole in enumerate(geom.interiors, start=1):
                lbl = f'{cntFaces}_H{numHole}'
                cntFaces, cntCtrs, cntNodes = self._dumpLinearRing(
                    out, hole, cntFaces, cntCtrs, cntNodes, lbl)
                out.write(f'face{cntFaces} = geompy.MakeCut(face{cntFaces}, face{lbl})\n\n')

        if self.withFaceIds:
            out.write(f'''
id_face{cntFaces} = geompy.addToStudy(face{cntFaces}, 'Face_{cntFaces}')
gg.createAndDisplayGO(id_face{cntFaces})
gg.setDisplayMode(id_face{cntFaces}, 1)
''')
        if (1 == cntFaces):
            out.write(f'allBuildFaces = face1\n')
        else:
            out.write(f'allBuildFaces = geompy.MakeFuse(allBuildFaces, face{cntFaces})\n')

        coords = geom.exterior.coords[0]
        x, y, z = coords[0], coords[1], (0 if (2 == len(coords)) else coords[2]) + elevation
        out.write(f'''
ptZ{cntNode0} = geompy.MakeVertex({x}, {y}, {z})
building{cntFaces} = geompy.MakePrism(face{cntFaces}, pt{cntNode0}, ptZ{cntNode0})
id_building{cntFaces} = geompy.addToStudy(building{cntFaces}, 'Building_{cntFaces}')
gg.createAndDisplayGO(id_building{cntFaces})
''')

        cntFaces += 1
        return cntFaces, cntCtrs, cntNodes

'''
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.io.SalomeWriterAndExtruder import SalomeWriterAndExtruder

gdf = GeoDataFrameDemos.ensaNantesBuildings()
gdf.geometry = gdf.geometry.apply(lambda g: GeomLib.forceZCoordinateToZ0(g, 0))
SalomeWriterAndExtruder(gdf, '/tmp/salome_script2.py', elevationFieldname='HAUTEUR',
                        withFaceIds=False, exportBrep=False).run()
'''
