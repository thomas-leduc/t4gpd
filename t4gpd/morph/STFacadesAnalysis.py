'''
Created on 2 avr. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from shapely.geometry import LineString, MultiPolygon
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STFacadesAnalysis(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, gidFieldname='ID', elevationFieldname='HAUTEUR', exteriorOnly=True):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'GeoDataFrame')
        self.buildings = buildings

        if not ((gidFieldname is None) or (gidFieldname in buildings)):
            raise Exception('%s is not a relevant field name!' % (gidFieldname))
        self.gidFieldname = gidFieldname

        if not ((elevationFieldname is None) or (elevationFieldname in buildings)):
            raise Exception('%s is not a relevant field name!' % (elevationFieldname))
        self.elevationFieldname = elevationFieldname

        self.exteriorOnly = exteriorOnly

    def __analyzeFacades(self, geom, gid, elev):
        rows = []

        if isinstance(geom, MultiPolygon):
            for _geom in geom.geoms:
                rows += self.__analyzeFacades(_geom, gid, elev)
        else:
            if self.exteriorOnly:
                geom = geom.exterior
            for _currEdge in GeomLib.toListOfBipointsAsLineStrings(geom):
                _midPoint = GeomLib.getMidPoint(*_currEdge.coords)
                _normal = GeomLib.unitVector(*_currEdge.coords)
                _normal = [_normal[1], -_normal[0]]
                _azim = AngleLib.toDegrees(AngleLib.normAzimuth(_normal))
                _normal = [_midPoint[0] + _normal[0], _midPoint[1] + _normal[1]]
                _normal = LineString([_midPoint, _normal])
                _length = _currEdge.length
                rows.append({ 
                    'buildingID': None if (gid is None) else gid,
                    'length': _length,
                    'height': None if (elev is None) else elev,
                    'surface': None if (elev is None) else _length * elev,
                    'azimuth': _azim,
                    'normal': _normal.wkt,
                    'geometry': _currEdge
                    })

        return rows

    def run(self):
        rows = []
        for _, row in self.buildings.iterrows():
            if not GeomLib.isPolygonal(row.geometry):
                continue            
            gid = None if (self.gidFieldname is None) else row[self.gidFieldname] 
            elev = None if (self.elevationFieldname is None) else row[self.elevationFieldname] 
            geom = GeomLib.normalizeRingOrientation(row.geometry)
            rows += self.__analyzeFacades(geom, gid, elev)

        result = GeoDataFrame(rows, crs=self.buildings.crs)
        result['gid'] = range(len(result))
        return result
