'''
Created on 3 mars 2021

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
from numpy import arctan
from shapely.geometry import LineString, Point
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.sun.geoProcesses.AbstractSunshineDuration import AbstractSunshineDuration


class SunshineDurationOnTopOfRoof(AbstractSunshineDuration):
    '''
    classdocs
    '''

    def __init__(self, masksGdf, maskElevationFieldname, datetimes, model='pysolar'):
        '''
        Constructor
        '''
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        self.masksGdf = masksGdf
        self.masksSIdx = masksGdf.sindex

        if maskElevationFieldname not in masksGdf:
            raise Exception('%s is not a relevant field name!' % (maskElevationFieldname))
        self.maskElevationFieldname = maskElevationFieldname
        maxElevation = max(self.masksGdf[self.maskElevationFieldname])  #===========

        self.sunModel = SunLib(masksGdf, model)
        self.sunPositions = self._getAllSunPositions(datetimes, maxElevation)
        self.nSunPositions = len(self.sunPositions)
 
    @staticmethod
    def __beingInTheSunOnTheRooftop(masksGdf, masksSIdx, maskElevationFieldname, viewpoint,
                                    h0, radDir, rayLen, sunAlti):
        # To avoid: "Inconsistent coordinate dimensionality"
        viewpoint = Point((viewpoint.x, viewpoint.y))
        remotePoint = Point((viewpoint.x + rayLen * radDir[0], viewpoint.y + rayLen * radDir[1]))
        sunRay = LineString([viewpoint, remotePoint])

        masksIds = list(masksSIdx.intersection(sunRay.bounds))
        for maskId in masksIds:
            mask = masksGdf.loc[maskId]
            maskGeom = mask.geometry
            maskElevation = mask[maskElevationFieldname]

            if sunRay.crosses(maskGeom):
                tmpGeom = maskGeom.intersection(sunRay)
                gc = tmpGeom.geoms if GeomLib.isMultipart(tmpGeom) else [tmpGeom]

                for geom in gc:
                    for vertex in geom.coords:
                        hitPoint = Point(vertex)
                        _dist = viewpoint.distance(hitPoint)
                        if (h0 < maskElevation):
                            _angle = arctan((maskElevation - h0) / _dist)
                            if (_angle >= sunAlti):
                                return False

        return True

    def runWithArgs(self, row):
        # viewpoint = row.geometry.centroid
        viewpoint = row.geometry.representative_point()

        enclosingFeatures = GeomLib.getEnclosingFeatures(self.masksGdf, self.masksSIdx, viewpoint)

        if (0 == len(enclosingFeatures)):
            # OUTDOOR/STREET-LEVEL VIEWPOINT
            nbHits = 0
            for (sunAlti, radDir, rayLen) in self.sunPositions:
                if self._beingInTheSun(viewpoint, radDir, rayLen, sunAlti):
                    nbHits += 1

        else:
            # INDOOR/ROOFTOP VIEWPOINT

            # REMOVE enclosingFeatures FROM THE GeoDataFrame & SpatialIndex OF SURROUNDING MASKS
            enclosingFeaturesIndex = [f.name for f in enclosingFeatures]
            _buildings = self.masksGdf[~self.masksGdf.index.isin(enclosingFeaturesIndex)]
            _buildings.reset_index(drop=True, inplace=True)  # HANDLE POTENTIAL KeyError
            _sindex = _buildings.sindex

            # ASSESS SUN BEAM HITS
            h0 = min([f[self.maskElevationFieldname] for f in enclosingFeatures])

            nbHits = 0
            for (sunAlti, radDir, rayLen) in self.sunPositions:
                if SunshineDurationOnTopOfRoof.__beingInTheSunOnTheRooftop(
                    _buildings, _sindex, self.maskElevationFieldname, viewpoint,
                    h0, radDir, rayLen, sunAlti):
                    nbHits += 1

        return {
            'sun_hits': nbHits,
            'sun_ratio': float(nbHits) / self.nSunPositions
            }
