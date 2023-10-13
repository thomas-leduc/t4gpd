'''
Created on 12 oct. 2023

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
from geopandas import GeoDataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.grid.GridLib import GridLib


class STAdaptativeGrid(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, dx, thresholds=None, indoor=False, intoPoint=False,
                 encode=True):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        self.gdf = gdf

        self.dx = dx
        self.thresholds = self.dx if thresholds is None else thresholds

        if indoor in [None, True, False, "both"]:
            self.indoor = indoor
        else:
            raise Exception(
                "Illegal argument: indoor must be chosen in [None, True, False, 'both']!")
        self.intoPoint = intoPoint
        self.encode = encode

    def run(self):
        for i, (dx, threshold) in enumerate(zip(self.dx, self.thresholds)):
            if i == 0:
                grid0 = GridLib.getGrid1(self.gdf, self.dx[0])
            else:
                grid0 = GridLib.getSubgrid1(self.gdf, grid0, dx, threshold)

        if self.indoor is None:
            pass
        elif ("both" == self.indoor):
            grid0 = GridLib.getIndoorOutdoorGrid(self.gdf, grid0)
        elif self.indoor:
            grid0 = GridLib.getIndoorGrid(self.gdf, grid0)
        else:
            grid0 = GridLib.getOutdoorGrid(self.gdf, grid0)

        if self.intoPoint:
            grid0.geometry = grid0.centroid

        return grid0


"""
import matplotlib.pyplot as plt
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

buildings = GeoDataFrameDemos.ensaNantesBuildings()
grid = STAdaptativeGrid(buildings, dx=[32, 16, 8, 4], indoor=None).run()

buildings.to_file("/tmp/buildings.shp")
grid.to_file("/tmp/grid.shp")

fig, ax = plt.subplots(figsize=(1*8.26, 1*8.26))
ax.set_title(f"{len(grid)} cells", fontsize=24)
buildings.plot(ax=ax, color="grey")
grid.boundary.plot(ax=ax, color="red", linewidth=0.5)
ax.axis("off")
plt.show()
plt.close(fig)
"""
