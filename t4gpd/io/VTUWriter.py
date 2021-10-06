'''
Created on 31 aug. 2020

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
from shapely.geometry import Point, Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class VTUWriter(GeoProcess):
    '''
    classdocs
    
    For more information, please see
    https://www.vtk.org/wp-content/uploads/2015/04/file-formats.pdf
    '''
    VTKTYPE = 7  # VTK_POLYGON=7, VTK_POLY_LINE=4, VTK_POLY_VERTEX=2

    def __init__(self, inputGdf, outputFile):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        self.cellData = dict()
        for fname in self.inputGdf.columns:
            ftype = str(self.inputGdf.dtypes[fname])
            if 'int64' == ftype:
                self.cellData[fname] = { 'type':'Int32', 'values':[] }
            elif 'float64' == ftype:
                self.cellData[fname] = { 'type':'Float32', 'values':[] }
            # LE CHARGEMENT DE CHAMPS DE TYPES STRING SEMBLE PLANTER PARAVIEW
            # elif (object == ftype):
                # self.cellData[fname] = { 'type':'String', 'values':[] }

        self.outputFile = outputFile

    def __addAndGetANode(self, x, y, z=0.0):
        hashCoord = GeomLib.hashCoords(x, y, z)
        if hashCoord in self.ciVertices:
            nodeIndex = self.ciVertices[hashCoord]
        else:
            nodeIndex = len(self.ciVertices)
            self.ciVertices[hashCoord] = nodeIndex
            self.icVertices[nodeIndex] = [x, y, z]
        return nodeIndex           

    def __addContour(self, geom):
        contour = []
        if isinstance(geom, Polygon):
            if (GeomLib.isHoled(geom)):
                print("*** Holed polygon:: %s" % geom.wkt)
            elif not GeomLib.isConvex(geom):
                print("*** Concave polygon:: %s" % geom.wkt)

            for xyz in geom.exterior.coords:
                p = Point(xyz)
                if p.has_z:
                    nodeIndex = self.__addAndGetANode(p.x, p.y, p.z)
                else:
                    nodeIndex = self.__addAndGetANode(p.x, p.y)
                contour.append(nodeIndex)

        return contour
        # Remove final point
        # return contour[:-1]

    def run(self):
        self.ciVertices = dict()
        self.icVertices = dict()
        contours, offsets = [], []

        for _, row in self.inputGdf.iterrows():
            for fieldname in self.cellData:
                self.cellData[fieldname]['values'].append(row[fieldname])

            geom = row.geometry
            if GeomLib.isMultipart(geom):
                for g in geom.geoms:
                    ctr = self.__addContour(g)
                    contours.append(ctr)

                    if (0 == len(offsets)):
                        offsets.append(len(ctr))
                    else:
                        offsets.append(offsets[-1] + len(ctr))
            else:
                ctr = self.__addContour(geom)
                contours.append(ctr)

                if (0 == len(offsets)):
                    offsets.append(len(ctr))
                else:
                    offsets.append(offsets[-1] + len(ctr))

        with open(self.outputFile, 'w') as f: 
            f.write("<VTKFile type='UnstructuredGrid' version='0.1'>\n")
            f.write("\t<UnstructuredGrid>\n")
            f.write("\t\t<Piece NumberOfPoints='%d' NumberOfCells='%d'>\n" % (len(self.icVertices), len(contours)))

            # ===== CELLDATA =====
            f.write("\t\t\t<CellData Scalars='scalars'>\n")
            f.writelines([
                "\t\t\t\t<DataArray Name='%s' type='%s' format='ascii'>\n%s\t\t\t\t</DataArray>\n" % 
                    (k, v['type'], ' '.join(str(i) for i in v['values']))
                for k, v in list(self.cellData.items())
            ])
            '''
            f.writelines(
                map(lambda(k, v): 
                    "\t\t\t\t<DataArray Name='%s' type='%s' format='ascii'>\n%s\t\t\t\t</DataArray>\n" % 
                    (k, v['type'], ' '.join(str(i) for i in v['values'])), self.cellData.iteritems())
                )
            '''
            f.write("\t\t\t</CellData>\n")

            f.write("\t\t\t<Points>\n")
            f.write("\t\t\t\t<DataArray type='Float32' NumberOfComponents='3' format='ascii'>\n")
            f.writelines([
                '%f %f %f\n' % (v[0], v[1], v[2]) for k, v in sorted(self.icVertices.items())
            ])
            # f.writelines(map(lambda(k, v): '%f %f %f\n' % (v[0], v[1], v[2]), sorted(self.icVertices.iteritems())))  # COORDS
            f.write("\t\t\t\t</DataArray>\n")
            f.write("\t\t\t</Points>\n")
            f.write("\t\t\t<Cells>\n")
            f.write("\t\t\t\t<DataArray type='Int32' Name='connectivity' format='ascii'>\n")
            f.writelines([' '.join(str(i) for i in ctr) + ' ' for ctr in contours] + ['\n'])  # CONNECTIVITY
            f.write("\t\t\t\t</DataArray>\n")
            f.write("\t\t\t\t<DataArray type='Int32' Name='offsets' format='ascii'>\n")
            f.writelines(['%d ' % i for i in offsets] + ['\n'])  # OFFSETS
            f.write("\t\t\t\t</DataArray>\n")
            f.write("\t\t\t\t<DataArray type='Int32' Name='types' format='ascii'>\n")
            f.writelines(['%d ' % (VTUWriter.VTKTYPE) for _ in range(len(contours))] + ['\n'])  # TYPES
            f.write("\t\t\t\t</DataArray>\n")
            f.write("\t\t\t</Cells>\n")
            f.write("\t\t</Piece>\n")
            f.write("\t</UnstructuredGrid>\n")
            f.write("</VTKFile>\n")

            print('%s has been written!' % self.outputFile)
