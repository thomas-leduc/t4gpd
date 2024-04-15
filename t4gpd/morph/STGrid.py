'''
Created on 11 juin 2020

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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


class STGrid(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, dx, dy=None, indoor=None, intoPoint=True,
                 encode=True, withDist=False, roi=None):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        self.gdf = gdf
        self.dx = dx
        self.dy = dy
        if indoor in [None, True, False, "both"]:
            self.indoor = indoor
        else:
            raise Exception(
                "Illegal argument: indoor must be chosen in [None, True, False, 'both']!")
        self.intoPoint = intoPoint
        self.encode = encode
        self.withDist = withDist
        self.roi = roi

    def run(self):
        if self.roi is None:
            grid = GridLib.getGrid2(self.gdf, self.dx, self.dy, self.encode)
        else:
            grid = GridLib.getGrid2(self.roi, self.dx, self.dy, self.encode)

        if self.indoor is None:
            pass
        elif ("both" == self.indoor):
            grid = GridLib.getIndoorOutdoorGrid(self.gdf, grid)
        elif self.indoor:
            grid = GridLib.getIndoorGrid(self.gdf, grid)
        else:
            grid = GridLib.getOutdoorGrid(self.gdf, grid)

        if self.intoPoint:
            grid.geometry = grid.centroid

        if self.withDist:
            if (0 == len(self.gdf)):
                grid["dist_to_ctr"] = float("inf")
            else:
                grid = GridLib.getDistanceToNearestContour(self.gdf, grid)

        return grid


"""
# -----
import matplotlib.pyplot as plt
from geopandas import clip
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.demos.NantesBDT import NantesBDT
from t4gpd.morph.STBBox import STBBox

buffDist = 100
roi = STBBox(GeoDataFrameDemos.squaresInNantes("Royale"), buffDist).run()
buildings = NantesBDT.buildings(roi)

dx = 30
sensors = STGrid(buildings, dx=dx, dy=None, indoor=False,
	intoPoint=False, withDist=True).execute()

# -----
fig, ax = plt.subplots(figsize=(1*8.26, 1*8.26))
buildings.plot(ax=ax, color="grey")
sensors.boundary.plot(ax=ax, color="black", linewidth=0.15)
fig.tight_layout()
plt.show()
plt.close(fig)
"""
