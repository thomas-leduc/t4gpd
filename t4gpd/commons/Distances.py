'''
Created on 22 juin 2020

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
from numpy import array, log10, sqrt, sum


class AbstractDistance(object):
    '''
    classdocs
    '''

    def __init__(self, distName='Euclidean'):
        if ('Canberra' == distName):
            self.distTool = CanberraDistance()
        elif ('Chebyshev' == distName):
            self.distTool = ChebyshevDistance()
        elif ('EarthMovers' == distName):
            self.distTool = EarthMoversDistance()
        elif ('Euclidean' == distName):
            self.distTool = EuclideanDistance()
        elif ('Manhattan' == distName):
            self.distTool = ManhattanDistance()
        elif ('DTW' == distName):
            self.distTool = DTWDistance()
        elif ('SNR' == distName):
            self.distTool = SNRDistance()
        else:
            raise Exception('Unknown distance. Distance, if mentioned, must be ' + 
                            'chosen among: Canberra, Chebyshev, EarthMovers, ' + 
                            'Euclidean (default), Manhattan, DTW, and SNR!')
        '''
        elif ('Hausdorff' == distName):
            self.distTool = HausdorffDistance()
        '''

    def compute(self, lst1, lst2):
        if (len(lst1) != len(lst2)):
            return float('inf')
            # raise Exception('The two lists must be of the same size!')
        return self.distTool.compute(lst1, lst2)


class CanberraDistance(object):

    @staticmethod
    def compute(lst1, lst2):
        if (len(lst1) != len(lst2)):
            return float('inf')
        acc = 0.0
        for i in range(len(lst1)):
            num = abs(lst1[i] - lst2[i])
            denom = abs(lst1[i]) + abs(lst2[i])
            tmp = 0 if ((0 == num) and (0 == denom)) else num / denom
            acc += tmp
        return acc


class ChebyshevDistance(object):

    @staticmethod
    def compute(lst1, lst2):
        if (len(lst1) != len(lst2)):
            return float('inf')
        maxim = 0.0
        for i in range(len(lst1)):
            maxim = max(maxim, abs(lst1[i] - lst2[i]))
        return maxim


class EarthMoversDistance(object):

    @staticmethod
    def compute(lst1, lst2):
        if (len(lst1) != len(lst2)):
            return float('inf')
        lastDistance = 0.0
        totalDistance = 0.0
        for i in range(len(lst1)):
            currentDistance = (lst1[i] + lastDistance) - lst2[i]
            totalDistance += abs(currentDistance)
            lastDistance = currentDistance
        return totalDistance


class EuclideanDistance(object):

    @staticmethod
    def compute(lst1, lst2):
        if (len(lst1) != len(lst2)):
            return float('inf')
        acc = 0.0
        for i in range(len(lst1)):
            tmp = lst1[i] - lst2[i]
            acc += tmp * tmp
        return sqrt(acc)


class ManhattanDistance(object):

    @staticmethod
    def compute(lst1, lst2):
        if (len(lst1) != len(lst2)):
            return float('inf')
        acc = 0.0
        for i in range(len(lst1)):
            acc += abs(lst1[i] - lst2[i])
        return acc

'''
class HausdorffDistance(object):
    @staticmethod
    def compute(lst1, lst2):
        if (len(lst1) != len(lst2)):
            return float('inf')
        cartc1 = PolarCartesianCoordinates.fromRayLengthsToCartesianCoordinates(lst1)
        cartc2 = PolarCartesianCoordinates.fromRayLengthsToCartesianCoordinates(lst2)
        dists = []
        for c1 in cartc1:
            dists.append(min([EuclideanDistance.compute(c1, c2) for c2 in cartc2]))
        for c2 in cartc2:
            dists.append(min([EuclideanDistance.compute(c1, c2) for c1 in cartc1]))
        return max(dists)
        # raise NotImplementedError('HausdorffDistance must be implemented first!')
'''


class DTWDistance(object):

    @staticmethod
    def compute(lst1, lst2):
        nc = len(lst1)
        nl = len(lst2)
        dtw = [[ float('inf') for _ in range(nc + 1) ] for _ in range(nl + 1) ]
        dtw[0][0] = 0.0
        for l in range(nl):
            for c in range(nc):
                cost = abs(lst1[c] - lst2[l])
                dtw[l + 1][c + 1] = cost + min(dtw[l][c + 1], dtw[l + 1][c], dtw[l][c])
        return dtw[nl][nc]


class SNRDistance(object):

    @staticmethod
    def compute(lst1, lst2):
        '''
        To compare the performance of the recovery algorithms, the SNR (Signal to noise ratio) will be used.
        Original signal: lst1
        Restored signal: lst2
        '''
        if (len(lst1) != len(lst2)):
            return float('inf')
        t1, t2 = array(lst1), array(lst2)
        return 10 * log10(sum(t1 ** 2) / sum((t1 - t2) ** 2))

# for d in ['Canberra', 'Chebyshev', 'EarthMovers', 'Euclidean', 'Manhattan', 'DTW']:
#     print AbstractDistance(d).compute([1, 1, 1, 1], [1, 1, 1, 2])

# print CanberraDistance.compute([1, 1, 1, 1], [1, 1, 1, 2])
# print ChebyshevDistance.compute([1, 1, 1, 1], [1, 1, 1, 2])
# print EarthMoversDistance.compute([1, 1, 1, 1], [1, 1, 1, 2])
# print EuclideanDistance.compute([1, 1, 1, 1], [1, 1, 1, 2])
# print ManhattanDistance.compute([1, 1, 1, 1], [1, 1, 1, 2])
# print HausdorffDistance.compute([1, 1, 1, 1], [1, 1, 1, 2])
# print DTWDistance.compute([1, 1, 1, 1], [1, 1, 1, 2])
