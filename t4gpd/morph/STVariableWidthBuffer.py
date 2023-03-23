'''
Created on 31 janv. 2023

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
from geopandas import GeoDataFrame
from numpy import asarray, sqrt
from shapely.geometry import Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STVariableWidthBuffer(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, widthFieldname):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, 'GeoDataFrame')
        self.gdf = gdf
        self.widthFieldname = widthFieldname

    def __dilate(self, p0, p1, p2, width):
        if (p0 is None):
            before, after = p1, p2
        elif (p2 is None):
            before, after = p0, p1
        else:
            before, after = p0, p2
        # mv: Motion vector; nmv: L2-norm of the motion vector; nv: Normal vector
        mv = asarray([after.x - before.x, after.y - before.y])
        nmv = sqrt((mv ** 2).sum())
        if (0 == nmv):
            return [p1.x, p1.y], [p1.x, p1.y]
        mv = mv / nmv
        nv = [mv[1], -mv[0]]
        return (
            [p1.x + width * nv[0], p1.y + width * nv[1]],
            [p1.x - width * nv[0], p1.y - width * nv[1]]
            )
        
    def run(self):
        pairs = []
        for _, row in self.gdf.iterrows():
            pairs.append({'geometry': row.geometry, 'width': row[self.widthFieldname]})
        n = len(pairs)

        rows1, rows2 = [], []
        for i in range(n):
            p0 = pairs[i - 1]['geometry'] if (0 < i) else None
            p1, width = pairs[i]['geometry'], pairs[i]['width']
            p2 = pairs[i + 1]['geometry'] if (i + 1 < n) else None
            down, up = self.__dilate(p0, p1, p2, width)
            rows1.append(down)
            rows2.insert(0, up)

        geom = Polygon(rows1 + rows2)
        return GeoDataFrame([{'geometry': geom}], crs=self.gdf.crs)
