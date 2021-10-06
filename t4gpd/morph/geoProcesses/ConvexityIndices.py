'''
Created on 18 dec. 2020

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
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class ConvexityIndices(AbstractGeoprocess):
    '''
    classdocs
    '''

    @staticmethod
    def runWithArgs(row):
        geom = row.geometry
        geomArea = geom.area
        geomPerim = geom.length

        chull = geom.convex_hull
        chullArea = chull.area
        chullPerim = chull.length

        connectedComponents = chull.difference(geom).geoms

        nConnectedComponents = len(connectedComponents)
        areaConvexityDefect = geomArea / chullArea if (0.0 < chullArea) else None
        perimConvexityDefect = chullPerim / geomPerim if (0.0 < geomPerim) else None

        bigConcavities = sum([g.area ** 2 for g in connectedComponents]) / nConnectedComponents
        smallConcavities = sum([g.area ** (-2) 
                                for g in connectedComponents
                                if (0.0 < g.area)]) / nConnectedComponents

        return {
            'n_con_comp': nConnectedComponents,
            'a_conv_def': areaConvexityDefect,
            'p_conv_def': perimConvexityDefect,
            'big_concav': bigConcavities,
            'small_conc': smallConcavities
            }        
