'''
Created on 17 juin 2020

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
from numpy import sqrt
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.crossroads_generation.SequenceRadii import SequenceRadii
from t4gpd.commons.crossroads_generation.SequencesGeneration import SequencesGeneration


class STCrossroadsGeneration(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, nbranchs, length, width, mirror=False, withBranchs=True, withSectors=True,
                 crs='EPSG:2154', magnitude=2.5, varLength=None):
        '''
        Constructor
        '''
        if not((varLength is None) or (0 <= varLength <= 1.0)):
            raise IllegalArgumentTypeException(varLength, "Float value between 0.0 and 1.0 or None")

        self.nbranchs = nbranchs
        self.sequenceRadii = SequenceRadii(nbranchs, width, length, varLength)
        self.dictOfSequences = SequencesGeneration(nbranchs, mirror, withBranchs, withSectors).run()
        self.width = width
        self.offset = magnitude * length

        nseq = len(self.dictOfSequences)
        sqrt_nseq = int(sqrt(nseq))
        if (abs(nseq - sqrt_nseq * sqrt_nseq) < abs(nseq - (sqrt_nseq + 1) * (sqrt_nseq + 1))):
            self.ncols = sqrt_nseq
        else:
            self.ncols = sqrt_nseq + 1

        self.crs = crs

    def run(self):
        rows = list()
        for i, (gid, seq) in enumerate(self.dictOfSequences.items()):
            xoffset = self.offset * (i % self.ncols)
            yoffset = -self.offset * int(i / self.ncols)
            geom = seq.asPolygon(self.sequenceRadii, [xoffset, yoffset])
            row = dict({'gid': gid,
                        'vpoint_x': xoffset,
                        'vpoint_y': yoffset,
                        'model': seq.getMinModel(),
                        'sequence': str(seq),
                        'geometry': geom})
            rows.append(row)

        return GeoDataFrame(rows, crs=self.crs)
