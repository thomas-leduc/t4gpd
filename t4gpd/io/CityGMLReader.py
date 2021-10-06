'''
Created on 22 oct. 2020

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
import re
from shapely.geometry import Polygon

from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.CSVLib import CSVLib
from t4gpd.commons.GeoProcess import GeoProcess


class CityGMLReader(GeoProcess):
    '''
    classdocs
    '''
    RE_BUILDING = re.compile(r'<bldg:Building\s')
    RE_OUTER_BUILDING_INSTALLATION = re.compile(r'<bldg:outerBuildingInstallation')
    RE_GROUND_SURFACE = re.compile(r'<bldg:GroundSurface')
    RE_ROOF_SURFACE = re.compile(r'<bldg:RoofSurface')
    RE_WALL_SURFACE = re.compile(r'<bldg:WallSurface')
    RE_DOOR = re.compile(r'<bldg:Door')
    RE_WINDOW = re.compile(r'<bldg:Window')
    RE_RELIEF_FEATURE = re.compile(r'<dem:ReliefFeature')
    RE_TIN_RELIEF = re.compile(r'<dem:TINRelief')
    RE_POLYGON = re.compile(r'<gml:Polygon')
    RE_EXTERIOR_RING = re.compile(r'<gml:exterior')
    RE_INTERIOR_RING = re.compile(r'<gml:interior')
    RE_POS_LIST = re.compile(r'<gml:posList')
    RE_EXTRACT_NODES = re.compile(r'<gml:posList[^>]*>(.*)<\/gml:posList>')
    RE_EXTRACT_POLYGON_ID = re.compile(r'<gml:Polygon[^>]*gml:id="([^"]*)"[^>]*>')
  
    def __init__(self, inputFile, srcEpsgCode='EPSG:4326', dstEpsgCode=None):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.crs = srcEpsgCode
        self.dstEpsgCode = dstEpsgCode

    def __fromPosListToArrayOfPoint3d(self, txt):
        coords = txt.strip().split()
        return [
            (CSVLib.readLexeme(coords[i]),
             CSVLib.readLexeme(coords[i + 1]),
             CSVLib.readLexeme(coords[i + 2])) for i in range(0, len(coords), 3)
            ]

    def __version2(self):
        the_type, subType, subSubType = None, None, None
        polygonId, objectId, subObjectId = 1, 1, 1
        extNodes, holesNodes = None, None
        isExteriorRing = None

        rows = []
        with open(self.inputFile, 'r') as f:
            for line in f:
                line = line.strip()

                if self.RE_BUILDING.match(line):
                    the_type = 'Building_%d' % (objectId)
                    subType, subSubType = None, None
                    objectId += 1
                elif self.RE_OUTER_BUILDING_INSTALLATION.match(line):
                    # TODO
                    pass
                elif self.RE_GROUND_SURFACE.match(line):
                    subType = 'GroundSurface_%d' % (subObjectId)
                    subSubType = None
                    subObjectId += 1
                elif self.RE_ROOF_SURFACE.match(line):
                    subType = 'RoofSurface_%d' % (subObjectId)
                    subSubType = None
                    subObjectId += 1
                elif self.RE_WALL_SURFACE.match(line):
                    subType = 'WallSurface_%d' % (subObjectId)
                    subSubType = None
                    subObjectId += 1
                elif self.RE_DOOR.match(line):
                    subSubType = 'Door'
                elif self.RE_WINDOW.match(line):
                    subSubType = 'Window'
                elif self.RE_RELIEF_FEATURE.match(line):
                    the_type = 'ReliefFeature'
                    subType, subSubType = None, None
                elif self.RE_TIN_RELIEF.match(line):
                    subType = 'TINRelief'
                elif self.RE_POLYGON.match(line):
                    tmp = self.RE_EXTRACT_POLYGON_ID.search(line.strip()).group(1)
                    polygonId = None if tmp is None else tmp[1]
                    if extNodes is not None:
                        rows.append({
                            'type': the_type,
                            'subType': subType,
                            'subSubType': subSubType,
                            'polygonId': polygonId,
                            'geometry': Polygon(extNodes, holesNodes)
                            })
                        extNodes, holesNodes = None, None

                elif self.RE_EXTERIOR_RING.match(line):
                    isExteriorRing = True
                elif self.RE_INTERIOR_RING.match(line):
                    isExteriorRing = False

                elif self.RE_POS_LIST.match(line):
                    tmp = self.RE_EXTRACT_NODES.search(line.strip()).group(1)
                    if tmp is not None:
                        if isExteriorRing:
                            extNodes = self.__fromPosListToArrayOfPoint3d(tmp)
                        else:
                            if holesNodes is None:
                                holesNodes = []
                            holesNodes.append(self.__fromPosListToArrayOfPoint3d(tmp))
        return rows

    def run(self):
        rows = self.__version2()
        outputGdf = GeoDataFrame(rows, crs=self.crs)
        if not self.dstEpsgCode is None:
            outputGdf = outputGdf.to_crs(self.dstEpsgCode)
        return outputGdf
