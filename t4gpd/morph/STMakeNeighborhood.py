'''
Created on 21 juin 2024

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
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STMakeNeighborhood(object):
    '''
    classdocs
    '''

    def __init__(self, gdf, gidFieldName="gid"):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if gidFieldName not in gdf:
            raise Exception(f"{gidFieldName} is not a relevant field name!")

        self.gdf = gdf
        self.gid = gidFieldName

    def run(self):
        def myAppend(list1, list2):
            if isinstance(list1, list) and isinstance(list2, list):
                return list1 + list2
            if isinstance(list1, list):
                return list1
            if isinstance(list2, list):
                return list2
            raise Exception("Unreachable instruction!")

        left, right = f"{self.gid}_left", f"{self.gid}_right"

        gdf1 = self.gdf.sjoin(self.gdf, how="inner", predicate="touches")
        gdf1 = gdf1.loc[:, [left, right]]
        gdf1 = gdf1.groupby(by=left, as_index=False).agg({right: list})

        gdf2 = self.gdf.sjoin(self.gdf, how="inner", predicate="overlaps")
        gdf2 = gdf2.loc[:, [left, right]]
        gdf2 = gdf2.groupby(by=left, as_index=False).agg({right: list})

        right1, right2 = f"{right}_x", f"{right}_y"
        gdf12 = gdf1.merge(gdf2, how="outer", on=left)
        gdf12["neighbors"] = gdf12.apply(
            lambda row: myAppend(row[right1], row[right2]), axis=1)
        gdf12 = gdf12.loc[:, [left, "neighbors"]]

        gdf = self.gdf.merge(
            gdf12, how="left", left_on=self.gid, right_on=left)
        gdf.drop(columns=[left], inplace=True)

        return gdf


"""
def _plot(gdf, neigh):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
    gdf.boundary.plot(ax=ax, color="grey", label="Input geoms")
    gdf.apply(lambda x: ax.annotate(
                text=x.gid, xy=x.geometry.centroid.coords[0],
                color="black", size=12  , ha="center", va="bottom"), axis=1)
    # neigh.boundary.plot(ax=ax, color="red", label="Result")
    neigh.apply(lambda x: ax.annotate(
                text=x.neighbors, xy=x.geometry.centroid.coords[0],
                color="red", size=12, ha="center", va="top"), axis=1)
    ax.legend(fontsize=14)
    fig.tight_layout()
    plt.show()
    plt.close(fig)
    
from shapely import box
from t4gpd.morph.STGrid import STGrid

gdf = GeoDataFrame([
    {"gid": 1, "geometry": box(0,0,3,3)},
])
grid = STGrid(gdf, dx=1, intoPoint=False).run()
# grid = grid.loc[:,["gid", "geometry"]]
neigh = STMakeNeighborhood(grid, "gid").run()

_plot(grid, neigh)
"""

"""
def _plot(gdf, neigh):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
    gdf.boundary.plot(ax=ax, color="grey", label="Input geoms")
    gdf.apply(lambda x: ax.annotate(
                text=x.gid, xy=x.geometry.centroid.coords[0],
                color="black", size=12  , ha="center", va="bottom"), axis=1)
    # neigh.boundary.plot(ax=ax, color="red", label="Result")
    neigh.apply(lambda x: ax.annotate(
                text=x.neighbors, xy=x.geometry.centroid.coords[0],
                color="red", size=12, ha="center", va="top"), axis=1)
    ax.legend(fontsize=14)
    fig.tight_layout()
    plt.show()
    plt.close(fig)

from geopandas import GeoDataFrame
from numpy.random import default_rng
from shapely.geometry import CAP_STYLE, Point
from t4gpd.morph.STVoronoiPartition2 import STVoronoiPartition2

npts, rng = 20, default_rng(1234)
XY = rng.uniform(low=0, high=100, size=(npts,2))
gdf = GeoDataFrame([{"gid": gid, "geometry": Point(xy)} for gid, xy in enumerate(XY)])
gdf.geometry = gdf.geometry.apply(lambda g: g.buffer(1, cap_style=CAP_STYLE.square))

plots = STVoronoiPartition2(gdf, max_segment_length=0.2).run()
neigh = STMakeNeighborhood(plots, "gid").run()

_plot(plots, neigh)
import matplotlib.pyplot as plt
ax = gdf.boundary.plot(color="grey")
plots.boundary.plot(ax=ax, color="red")
plt.show()
"""

"""
from geopandas import read_file
from t4gpd.demos.GeoDataFrameDemosA import GeoDataFrameDemosA
from t4gpd.morph.STVoronoiPartition2 import STVoronoiPartition2


bdtdir = "/home/tleduc/data/bdtopo/\
BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D044_2024-03-15\
/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/\
BDT_3-3_SHP_LAMB93_D044-ED2024-03-15"

roi = GeoDataFrameDemosA.hamainaP121roi()

gdf = read_file(f"{bdtdir}/BATI/BATIMENT.shp",
                mask=roi, engine="pyogrio")
gdf = gdf.clip(roi)
gdf["gid"] = range(len(gdf))

vor = STVoronoiPartition2(gdf, max_segment_length=0.25, erosion=0.5).run()
vor = vor.clip(roi)

neigh = STMakeNeighborhood(vor, "gid").run()
gdf.to_file("/tmp/abc.gpkg", layer="buildings")
vor.to_file("/tmp/abc.gpkg", layer="voronoi")
neigh.to_file("/tmp/abc.gpkg", layer="neighborhood")
"""
