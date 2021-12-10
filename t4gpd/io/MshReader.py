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
from shapely.geometry import Point, Polygon
from t4gpd.commons.GeoProcess import GeoProcess


class MshReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputFile, bbox, crs='EPSG:2154'):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.crs = crs
        minx, miny, _, _ = bbox
        self.newOrigin = Point((minx, miny))

    def __getCoordinates(self, nodes, i1, i2, i3):
        # TL 10.03.2021: add z-components
        return Polygon([
            [nodes[i1].x + self.newOrigin.x, nodes[i1].y + self.newOrigin.y, nodes[i1].z],
            [nodes[i2].x + self.newOrigin.x, nodes[i2].y + self.newOrigin.y, nodes[i2].z],
            [nodes[i3].x + self.newOrigin.x, nodes[i3].y + self.newOrigin.y, nodes[i3].z]
            ])

    def __error(self, nline, line, expected):
        separator = '*' * 80
        msg = '''
%s
\tMshReader:: File format error (line %d):
\tActual: %s
\t=> Expecting: %s
%s
''' % (separator, nline, line, expected, separator)
        raise Exception(msg)

    def __getVersion(self):
        with open(self.inputFile, 'r') as f:
            for nline, line in enumerate(f, start=1):
                line = line.strip()
                if (1 == nline):
                    if not '$MeshFormat' == line: 
                        self.__error(nline, line, '$MeshFormat')
                elif (2 == nline):
                    tmp = line.split()
                    if 3 != len(tmp): 
                        self.__error(nline, line, 'version-number file-type data-size')
                    else:
                        # version_number, file_type, data_size = tmp
                        return int(float(tmp[0]))

    def __readV2(self):
        items = []
        with open(self.inputFile, 'r') as f:
            nbNodes, nbElements, nodes = 0, 0, dict()

            for nline, line in enumerate(f, start=1):
                line = line.strip()

                if (nline <= 3):
                    # READ SECTION "MeshFormat"
                    if (1 == nline):
                        if not '$MeshFormat' == line:
                            self.__error(nline, line, '$MeshFormat')
                    elif (2 == nline):
                        tmp = line.split()
                        if 3 != len(tmp): 
                            self.__error(nline, line, 'version-number file-type data-size')
                    elif (3 == nline):
                        if not '$EndMeshFormat' == line: 
                            self.__error(nline, line, '$EndMeshFormat')

                elif (nline <= 6 + nbNodes):
                    # READ SECTION "Nodes"
                    if (4 == nline):
                        if not '$Nodes' == line: 
                            self.__error(nline, line, '$Nodes')
                    elif (5 == nline):
                        nbNodes = int(line)
                    elif (nline <= 5 + nbNodes):
                        # READ ALL NODES
                        nodeNumber, x, y, z = line.split()
                        nodes[int(nodeNumber)] = Point((float(x), float(y), float(z)))
                        if int(nodeNumber) != len(nodes):
                            self.__error(nline, line, 'node-number x-coord y-coord z-coord')
                    else:
                        if not '$EndNodes' == line: 
                            self.__error(nline, line, '$EndNodes')

                else:
                    # READ SECTION "Elements"
                    if (7 + nbNodes == nline):
                        if not '$Elements' == line: 
                            self.__error(nline, line, '$Elements')
                    elif (8 + nbNodes == nline):
                        nbElements = int(line) 
                    elif (nline <= 8 + nbNodes + nbElements):
                        # READ ALL ELEMENTS
                        tmp = line.split()
                        elementNumber, elementType = [int(i) for i in tmp[:2]]
                        if (2 == elementType):
                            # 3-node triangle
                            i1, i2, i3 = [int(i) for i in tmp[-3:]]
                            items.append({'gid': int(elementNumber), 'geometry':self.__getCoordinates(nodes, i1, i2, i3)})
                    else:
                        if not '$EndElements' == line: 
                            self.__error(nline, line, '$Elements')
        '''
        nodes = [{'gid':k, 'geometry':Point((v.x + self.newOrigin.x, v.y + self.newOrigin.y))}
                 for k, v in nodes.items()]
        GeoDataFrame(nodes, crs=self.crs).to_file('/tmp/yyy.shp')
        '''
        return items

    def __analyzeSectionNodesV4(self, content):
        nodes, nline = dict(), 0
        while nline < len(content):
            # entityDim, entityTag, parametric, numNodesInBlock = content[nline].split()        
            entityDim, _, _, numNodesInBlock = content[nline].split()
            entityDim, numNodesInBlock = int(entityDim), int(numNodesInBlock)

            if (0 == entityDim):
                nodeTag = int(content[nline + 1])
                x, y, z = content[nline + 2].split()
                nodes[nodeTag] = Point((float(x), float(y), float(z)))
                nline += 3

            elif (entityDim in [1, 2]):
                for i in range(numNodesInBlock):
                    nodeTag = int(content[nline + 1 + i])
                    x, y, z = content[nline + 1 + numNodesInBlock + i].split()
                    nodes[nodeTag] = Point((float(x), float(y), float(z)))
                nline += 1 + 2 * numNodesInBlock
        return nodes

    def __analyzeSectionElementsV4(self, content, nodes):
        triangles, nline = dict(), 0
        while nline < len(content):
            # entityDim, entityTag, elementType, numElementsInBlock = content[nline].split()
            _, _, elementType, numElementsInBlock = content[nline].split()
            elementType, numElementsInBlock = int(elementType), int(numElementsInBlock)

            if (2 == elementType):
                # 3-node triangle
                for i in range(numElementsInBlock):
                    elementTag, nodeTag1, nodeTag2, nodeTag3 = [int(n) for n in content[nline + 1 + i].split()]
                    triangles[elementTag] = self.__getCoordinates(nodes, nodeTag1, nodeTag2, nodeTag3)
            nline += 1 + numElementsInBlock
        return triangles

    def __readV4(self):
        with open(self.inputFile, 'r') as f:
            nbPoints, nbCurves, nbSurfaces, nbVolumes, nbEntities = 0, 0, 0, 0, 0
            nodes = []

            contentOfSectionNodes, contentOfSectionElements = [], []

            for nline, line in enumerate(f, start=1):
                line = line.strip()

                if (nline <= 3):
                    # READ SECTION "MeshFormat"
                    if (1 == nline):
                        if not '$MeshFormat' == line:
                            self.__error(nline, line, '$MeshFormat')
                    elif (2 == nline):
                        tmp = line.split()
                        if 3 != len(tmp): 
                            self.__error(nline, line, 'version-number file-type data-size')
                    elif (3 == nline):
                        if not '$EndMeshFormat' == line: 
                            self.__error(nline, line, '$EndMeshFormat')

                elif (nline <= 6 + nbEntities):
                    # READ SECTION "Entities"
                    if (4 == nline):
                        if not '$Entities' == line: 
                            self.__error(nline, line, '$Entities')
                    elif (5 == nline):
                        nbPoints, nbCurves, nbSurfaces, nbVolumes = [int(n) for n in line.split()]
                        nbEntities = nbPoints + nbCurves + nbSurfaces + nbVolumes
                    elif (nline <= 4 + nbPoints + 1):
                        '''
                        # USELESS
                        pointTag, x, y, z, _ = line.split()
                        nodes.append(Point((float(x), float(y), float(z))))
                        if int(pointTag) != len(nodes):
                            self.__error(nline, line, 'pointTag X Y Z numPhysicalTags')
                        '''
                        pass
                    elif (6 + nbEntities == nline):
                        beginOfSectionNodes = True
                        if not '$EndEntities' == line: 
                            self.__error(nline, line, '$EndEntities')

                elif beginOfSectionNodes:
                    # READ SECTION "Nodes"
                    if (7 + nbEntities == nline):
                        if not '$Nodes' == line: 
                            self.__error(nline, line, '$Nodes')
                    elif (8 + nbEntities == nline):
                        # USELESS
                        # numEntityBlocks, numNodes, minNodeTag, maxNodeTag = [int(n) for n in line.split()]
                        pass                    
                    else:
                        if ('$' != line[0]):
                            contentOfSectionNodes.append(line)
                        else:
                            if not '$EndNodes' == line: 
                                self.__error(nline, line, '$EndNodes')

                            nodes = self.__analyzeSectionNodesV4(contentOfSectionNodes)
                            beginOfSectionNodes = False
                            beginOfSectionElements = True

                elif beginOfSectionElements:
                    # READ SECTION "Elements"
                    if (10 + nbEntities + len(contentOfSectionNodes) == nline):
                        if not '$Elements' == line: 
                            self.__error(nline, line, '$Elements')
                    elif (11 + nbEntities + len(contentOfSectionNodes) == nline):
                        # USELESS
                        # numEntityBlocks, numElements, minElementTag, maxElementTag = [int(n) for n in line.split()]
                        pass
                    else:
                        if ('$' != line[0]):
                            contentOfSectionElements.append(line)
                        else:
                            if not '$EndElements' == line: 
                                self.__error(nline, line, '$EndElements')

                            triangles = self.__analyzeSectionElementsV4(contentOfSectionElements, nodes)
                            beginOfSectionElements = False

        items = [{'geometry': ring, 'gid': gid} for gid, ring in triangles.items()]

        '''
        nodes = [{'gid':k, 'geometry':Point((v.x + self.newOrigin.x, v.y + self.newOrigin.y))}
                 for k, v in nodes.items()]
        GeoDataFrame(nodes, crs=self.crs).to_file('/tmp/yyy.shp')
        '''

        return items

    def run(self):
        version = self.__getVersion()
        if 2 == version:
            print('MshReader:: read V2')
            rows = self.__readV2()
        elif 4 == version:
            print('MshReader:: read V4')
            rows = self.__readV4()
        else: 
            raise NotImplementedError(f'\n\n\t*** MshReader:: file format version #{version} must be implemented! ***')

        return GeoDataFrame(rows, crs=self.crs)
