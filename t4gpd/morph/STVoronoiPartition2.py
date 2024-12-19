'''
Created on 19 juin 2024

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
from shapely import MultiPoint, minimum_clearance, segmentize
from shapely.geometry import JOIN_STYLE
from shapely.ops import voronoi_diagram
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STVoronoiPartition2(object):
    '''
    classdocs
    '''

    def __init__(self, gdf, max_segment_length=1.0, erosion=0):
        '''
        Constructor
        '''
        def __erode(geom, erosion):
            if GeomLib.isPolygonal(geom):
                if ((0 == erosion) or (erosion > minimum_clearance(geom))):
                    _erosion = 0
                else:
                    _erosion = -erosion
                return geom.buffer(_erosion, join_style=JOIN_STYLE.mitre)
            return geom

        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        self.crs = gdf.crs
        self.gdf = gdf.copy(deep=True)
        self.gdf.geometry = self.gdf.geometry.apply(
            lambda g: __erode(g, erosion))

        _multiPoints = []
        for geom in self.gdf.geometry:
            _multiPoints += GeomLib.getListOfShapelyPoints(
                segmentize(geom, max_segment_length), withoutClosingLoops=False)
        _multiPoints = MultiPoint(_multiPoints)

        self.multiPoints = _multiPoints

    def run(self):
        vor = GeoDataFrame([{"geometry": v} for v in voronoi_diagram(
            self.multiPoints).geoms], crs=self.crs)
        vor = vor.sjoin(self.gdf, how="inner",
                        predicate="intersects", rsuffix="right01234567889")
        vor = vor.dissolve(by="index_right01234567889", as_index=False)
        vor.drop(columns="index_right01234567889", inplace=True)
        return vor


"""
def _plot(gdf, vor):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
    gdf.boundary.plot(ax=ax, color="grey", hatch="/", label="Input geoms")
    gdf.apply(lambda x: ax.annotate(
                text=x.gid, xy=x.geometry.centroid.coords[0],
                color="black", size=12, ha="center", va="center"), axis=1)
    vor.boundary.plot(ax=ax, color="red", label="Voronoi Tessel.")
    vor.apply(lambda x: ax.annotate(
                text=x.gid, xy=x.geometry.centroid.coords[0],
                color="red", size=12, ha="left", va="top"), axis=1)
    ax.legend(fontsize=14)
    fig.tight_layout()
    plt.show()
    plt.close(fig)
    
from shapely import box, MultiPolygon, Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

gdf = GeoDataFrameDemos.regularGridOfPlots(nlines=3, ncols=3)
d = 1e-1
gdf = GeoDataFrame([
    # {"gid": 1, "geometry": MultiPolygon([box(0,0,1,2), box(2+d,0,4,2)])},
    {"gid": 1, "geometry": MultiPolygon([box(0,0,1,2)])},
    {"gid": 2, "geometry": Polygon([(1+d,1), (2,0), (2,2)])},
    {"gid": 3, "geometry": MultiPolygon([box(2+d,0,4,2)])},
])
vor = STVoronoiPartition2(gdf, max_segment_length=0.1).run()
_plot(gdf, vor)
"""

"""
from t4gpd.demos.GeoDataFrameDemosA import GeoDataFrameDemosA
from geopandas import read_file

def _plot(gdf, vor):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
    gdf.plot(ax=ax, color="grey", edgecolor="dimgrey",
             alpha=0.5, label="Input geoms")
    # gdf.apply(lambda x: ax.annotate(
    #     text=x.gid, xy=x.geometry.centroid.coords[0],
    #     color="black", size=12, ha="center", va="center"), axis=1)
    vor.boundary.plot(ax=ax, color="red", linewidth=0.5,
                      label="Voronoi Tessel.")
    # vor.apply(lambda x: ax.annotate(
    #     text=x.gid, xy=x.geometry.centroid.coords[0],
    #     color="red", size=12, ha="left", va="top"), axis=1)
    ax.axis("off")
    ax.legend(fontsize=14)
    fig.tight_layout()
    plt.show()
    plt.close(fig)


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

_plot(gdf, vor)
"""
