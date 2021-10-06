'''
Created on 29 sept. 2020

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
from geopandas.geodataframe import GeoDataFrame
from numpy import mean
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCastingLib import RayCastingLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class AspectRatio(AbstractGeoprocess):
    '''
    classdocs
    '''
    DIRECTIONAL = 'Directional'
    PANOPTIC = 'Panoptic'
    MIXED = 'Mixed'

    def __init__(self, sensorsGdf, buildingsGdf, nRays=64, maxRayLen=100.0, modality='Panoptic',
                 elevationFieldname='HAUTEUR', canyonFieldName=None):
        '''
        Constructor
        '''
        if modality in (self.DIRECTIONAL, self.PANOPTIC, self.MIXED):
            if not isinstance(sensorsGdf, GeoDataFrame):
                raise IllegalArgumentTypeException(sensorsGdf, 'GeoDataFrame')

            if not isinstance(buildingsGdf, GeoDataFrame):
                raise IllegalArgumentTypeException(buildingsGdf, 'GeoDataFrame')
            self.buildingsGdf = buildingsGdf
            self.spatialIndex = buildingsGdf.sindex
    
            if (2 > nRays):
                raise IllegalArgumentTypeException(nRays, 'nRays must be greater than 2!')
            self.shootingDirs = RayCastingLib.preparePanopticRays(nRays)
            self.maxRayLen = maxRayLen

            self.modality = modality
            if (self.MIXED == modality) and (
                (canyonFieldName is None) or (canyonFieldName not in sensorsGdf)):
                raise Exception('If you chose the "mixed" modality, you must set "canyonFieldName"!')

            if elevationFieldname not in buildingsGdf:
                raise Exception('%s is not a relevant field name!' % elevationFieldname)
            self.elevationFieldname = elevationFieldname

            self.canyonFieldName = canyonFieldName
        else:
            raise Exception('Illegal argument: modality must be chosen in {%s, %s, %s}!' % 
                            (self.DIRECTIONAL, self.PANOPTIC, self.MIXED))

    def runWithArgs(self, row):
        viewPoint = row.geometry.centroid

        if GeomLib.isAnIndoorPoint(viewPoint, self.buildingsGdf, self.spatialIndex):
            return { 'svf': 0.0 }

        _shootingDirs = self.shootingDirs

        if (self.DIRECTIONAL == self.modality):
            _shootingDirs = RayCastingLib.prepareOrientedRays(
                self.buildingsGdf, self.spatialIndex, viewPoint)
        elif ((self.MIXED == self.modality) and
              ((1 == row[self.canyonFieldName]) or row[self.canyonFieldName])):
            _shootingDirs = RayCastingLib.prepareOrientedRays(
                self.buildingsGdf, self.spatialIndex, viewPoint)

        _, _, hitDists, hitMasks, _ = RayCastingLib.multipleRayCast25D(
            self.buildingsGdf, self.spatialIndex, viewPoint, _shootingDirs,
            self.maxRayLen, self.elevationFieldname, background=False)

        hitHeights = [0.0 if f is None else f[self.elevationFieldname] for f in hitMasks]

        # When the length is infinite, fix it by default at the distance to the artificial horizon
        hitDists = [x if (float('inf') != x) else self.maxRayLen for x in hitDists]

        return {
            # 'geometry': rays,
            # 'hit_dists': ArrayCoding.encode(hitDists),
            'h_over_w': float(mean(hitHeights) / (2 * mean(hitDists)))
            }
