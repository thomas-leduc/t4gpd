'''
Created on 22 juin 2022

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
from numpy import unique
from pandas import DataFrame
from t4gpd.commons.GeoProcess import GeoProcess


class STRaysToViewFactors(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, raysGdf, pkFieldname, hitGidsFieldname):
        '''
        Constructor
        '''
        assert isinstance(raysGdf, GeoDataFrame), 'raysGdf must be a GeoDataFrame'
        assert (pkFieldname in raysGdf), f'{pkFieldname} must be a GeoDataFrame field name!'
        assert (hitGidsFieldname in raysGdf), f'{hitGidsFieldname} must be a GeoDataFrame field name!'
        self.raysGdf = raysGdf
        self.pkFieldname = pkFieldname
        self.hitGidsFieldname = hitGidsFieldname

    def run(self):
        rows = []
        for _, row in self.raysGdf.iterrows():
            pk = row[self.pkFieldname]
            _hitGids = row[self.hitGidsFieldname]
            nrays = len(_hitGids)
            hitGids = [gid for gid in _hitGids if (gid is not None)]
            hitGids, hitGidsCount = unique(hitGids, return_counts=True)
            
            for i in range(len(hitGids)):
                rows.append({
                    'src': pk,
                    'dst': hitGids[i],
                    'viewfactor': hitGidsCount[i] / nrays,
                    }) 
        return DataFrame(data=rows)
