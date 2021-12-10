'''
Created on 19 mars 2021

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
import geopandas
from geopandas.geodataframe import GeoDataFrame
from matplotlib.colors import ListedColormap
from shapely.affinity import scale, translate
from shapely.geometry.multipolygon import MultiPolygon
from shapely.ops import unary_union, triangulate
from shapely.wkt import loads
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.morph.STPointsDensifier import STPointsDensifier

import matplotlib.pyplot as plt 


class Logos(object):
    '''
    classdocs
    '''

    @staticmethod
    def logoAsMultiLineString(_deltaX=50.0, _scaleX=0.9):
        _t = loads('MULTILINESTRING ((0 100, 0 0, 50 0), (0 50, 50 50))')

        _4 = loads('LINESTRING (50 50, 0 50, 30 100, 30 0)')
        _4 = translate(_4, xoff=_deltaX)

        _g = loads('LINESTRING (50 0, 0 0, 0 50, 50 50, 50 -50, 0 -50)')
        _g = translate(_g, xoff=2 * _deltaX)

        _p = loads('LINESTRING (0 -50, 0 50, 50 50, 50 0, 0 0)')
        _p = translate(_p, xoff=3 * _deltaX)

        _d = loads('LINESTRING (50 50, 0 50, 0 0, 50 0, 50 100)')
        _d = translate(_d, xoff=4 * _deltaX)

        _t4gpd = [_t, _4, _g, _p, _d]
        _t4gpd = [scale(letter, xfact=_scaleX) for letter in _t4gpd]
        _t4gpd = unary_union(_t4gpd)

        return _t4gpd

    @staticmethod
    def logoAsMultiPolygon(_deltaX=50.0, _scaleX=0.75, _buffDist=5.0):
        _mls = Logos.logoAsMultiLineString(_deltaX, _scaleX)
        return _mls.buffer(_buffDist)

    @staticmethod
    def logoAsMesh():
        gdf = GeoDataFrame([{'geometry':Logos.logoAsMultiPolygon()}])

        _gdf = STPointsDensifier(gdf, distance=45.0, pathidFieldname=None, adjustableDist=True, removeDuplicate=True).run()
        _tin = triangulate(unary_union(GeomLib.getListOfShapelyPoints(unary_union(_gdf.geometry))))
        _gdf = GeoDataFrame([{'geometry': MultiPolygon(_tin)}]).explode(ignore_index=True)
        gdf.geometry = gdf.geometry.apply(lambda g: g.buffer(1e-3))

        _gdf = geopandas.overlay(_gdf, gdf, how='intersection', keep_geom_type=True)
        _gdf['gid'] = range(len(_gdf))
        _gdf['gid'] = _gdf.gid % 4

        return _gdf

    @staticmethod
    def logoAsPdf(filename=None, greyscaled=False):
        _gdf = Logos.logoAsMesh()

        fig, _basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))

        if greyscaled:
            my_rgb_cmap = ListedColormap(['lightgrey', 'grey', 'darkgrey', 'dimgrey', 'black'])
            my_rgb_cmap = ListedColormap(['grey', 'darkgrey', 'dimgrey'])
            _gdf.plot(ax=_basemap, column='gid', edgecolor='grey', linewidth=0.1, cmap=my_rgb_cmap)
        else:
            _gdf.plot(ax=_basemap, color='dimgrey', edgecolor='lightgrey', linewidth=0.1)

        _basemap.axis('off')
        if filename is None:
            plt.show()
        else:
            fig.savefig(filename, bbox_inches='tight')
