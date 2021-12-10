'''
Created on 12 feb. 2021

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
from geopandas import GeoDataFrame, overlay
from pandas import concat
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STPolygonize import STPolygonize


class STMakeBlocks(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, roads, roi=None):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'GeoDataFrame')
        self.buildings = buildings

        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, 'GeoDataFrame')
        self.roads = roads

        if not((roi is None) or isinstance(roi, GeoDataFrame)):
            raise IllegalArgumentTypeException(roi, 'GeoDataFrame or None')
        self.roi = roi

    @staticmethod
    def __mkBlocks(buildings, roads, roi):
        # POLYGONIZE ROADS
        if not roi is None:
            _roads = GeoDataFrame(concat([roads[['geometry']], roi[['geometry']]]), crs=roads.crs)
        else:
            _roads = roads
        _polygons = STPolygonize(_roads).run()

        # GROUP BUILDINGS PER URBAN BLOCKS
        _buildings = overlay(buildings[['geometry']], _polygons, how='intersection')
        _blocks = _buildings.dissolve(by='gid', as_index=False)

        # TRY TO REMOVE CONCAVITIES IN EACH BLOCK
        roadsIdx = roads.sindex
        _blocks.geometry = _blocks.geometry.apply(lambda g: STMakeBlocks.__deleteConcavities(g, roads, roadsIdx))

        return _blocks

    @staticmethod
    def __deleteConcavities(block, roads, roadsIdx):
        _block = block.convex_hull
        _subsetOfRoads = roads.loc[roadsIdx.intersection(_block.bounds)]

        if (0 == len(list(filter(_block.intersects, _subsetOfRoads.geometry)))):
            return _block

        _concavities = _block.difference(block)
        if isinstance(_concavities, Polygon):
            _concavities = MultiPolygon([_concavities])
        result = [block]
        for _concavity in _concavities.geoms:
            if (0 == len(list(filter(_concavity.intersects, _subsetOfRoads.geometry)))):
                result.append(_concavity)
        # return unary_union(result)
        result = unary_union(result)
        '''
        for buffDist in [60, 50, 40, 30, 20, 10]:
            _tmp = result.buffer(buffDist, join_style=JOIN_STYLE.round).buffer(-buffDist, join_style=JOIN_STYLE.bevel)
            if (0 == len(list(filter(_tmp.intersects, _subsetOfRoads.geometry)))):
                result = _tmp
                print(buffDist)
                break
        '''
        return result

    def run(self):
        return STMakeBlocks.__mkBlocks(self.buildings, self.roads, self.roi)

'''
rootdir = '/home/tleduc/Dropbox/crenau/2_papiers_a_ecrire/2021_wavelet/dev/data-p9'
roads = gpd.read_file(rootdir + '/roads.shp')
roi = gpd.read_file(rootdir + '/roi.shp')
buildings = gpd.read_file(rootdir + '/buildings.shp')

# buildings = GeoDataFrameDemos.singleBuildingInNantes()
# print(buildings.geometry.squeeze().wkt)
# roads = gpd.GeoDataFrame([{'geometry': loads('LINESTRING (353880 6695040, 353905 6695040)')}], crs=buildings.crs)
# roads = gpd.GeoDataFrame([{'geometry': loads('LINESTRING (353935 6695030, 353949 6695030)')}], crs=buildings.crs)
# roads = gpd.GeoDataFrame([{'geometry': loads('LINESTRING (353942 6695020, 353950 6695015)')}], crs=buildings.crs)
# roads.to_file('/home/tleduc/Dropbox/crenau/2_papiers_a_ecrire/2021_wavelet/dev/data-p9/roads3.shp')

blocks = STMakeBlocks(buildings, roads, roi).run()
blocks.to_file(rootdir + '/_blocks2.shp')

print('THE END')
'''
