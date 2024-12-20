'''
Created on 26 sep. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
import meshio
from geopandas import GeoDataFrame
from shapely import Polygon
from t4gpd.commons.GeoProcess import GeoProcess


class MedReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputFile, crs="EPSG:2154"):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.crs = crs

    def __analyze(self, mesh):
        dictOfMaterials = mesh.cell_tags
        points = mesh.points
        triangles = mesh.cells_dict["triangle"]
        ntriangles = len(triangles)
        for materials in mesh.cell_data["cell_tags"]:
            if ntriangles == len(materials):
                break
        return dictOfMaterials, points, triangles, materials

    def run(self):
        mesh = meshio.read(self.inputFile)
        dictOfMaterials, points, triangles, materials = self.__analyze(mesh)
        return GeoDataFrame([
            {
                "geometry": Polygon([points[t[0]], points[t[1]], points[t[2]], points[t[0]]]),
                "material": dictOfMaterials[m][0]
            } for t, m in zip(triangles, materials)
        ], crs=self.crs)
