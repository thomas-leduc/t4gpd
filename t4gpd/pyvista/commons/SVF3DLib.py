'''
Created on 5 sept. 2022

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
from numpy import asarray, ceil, mean, pi, sum
from shapely.geometry import LineString, Polygon
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.commons.RayCasting3DLib import RayCasting3DLib
from t4gpd.pyvista.commons.RayCastingIn3DLib import RayCastingIn3DLib

from t4gpd.pyvista.commons.Diameter3DLib import Diameter3DLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class SVF3DLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def isFiveTimeRuleTrue(f1, f2):
        '''
        Wang, F. (2020). Modelling of urban micro-climates for building applications: a 
        non-transparent radiative transfer approach [Univ. de Lyon]. 
        https://tel.archives-ouvertes.fr/tel-03358937
        
        Excerpt from Section 2.2.2.4:
        a finite-area Lambertian emitter should be modeled as a point source only when 
        the distance to the receiving surface is greater than five times the maximum 
        projected width of the emitter
        '''
        assert isinstance(f1, Polygon), 'f1 is expected to be a Shapely Polygon!'
        assert isinstance(f2, Polygon), 'f2 is expected to be a Shapely Polygon!'

        _, diam1 = Diameter3DLib.diameter3D(f1)
        dist12 = GeomLib3D.distFromTo(GeomLib3D.centroid(f1).coords[0], GeomLib3D.centroid(f2).coords[0])
        return (dist12 >= 5 * diam1)

    @staticmethod
    def isa(f1, f2, optim=None):
        if optim is None:
            return SVF3DLib.__infinitesimalSurfaceApproximation(f1, f2)

        if ('left' == optim.lower()):
            F1 = SVF3DLib.subdivideLeft(f1, f2)
            # print(f'\t{len(F1)} sub-faces (left)')
            vfs = [
                SVF3DLib.__infinitesimalSurfaceApproximation(_f1, f2)
                for _f1 in F1
                ]
            return mean(vfs)

        if ('right' == optim.lower()):
            F2 = SVF3DLib.subdivideLeft(f2, f1)
            # print(f'\t{len(F2)} sub-faces (right)')
            vfs = [
                SVF3DLib.__infinitesimalSurfaceApproximation(f1, _f2)
                for _f2 in F2
                ]
            return sum(vfs)

        if ('both' == optim.lower()):
            F1 = SVF3DLib.subdivideLeft(f1, f2)
            F2 = SVF3DLib.subdivideLeft(f2, f1)
            # print(f'\t{len(F1) * len(F2)} sub-faces (both)')
            vfs = [sum([SVF3DLib.__infinitesimalSurfaceApproximation(_f1, _f2)
                for _f2 in F2]) for _f1 in F1]
            return mean(vfs)

        raise IllegalArgumentTypeException(optim, 'None, "left", "right" or "both"')

    @staticmethod
    def __infinitesimalSurfaceApproximation(f1, f2):
        '''
        View Factor from f1 to f2: diffuse energy leaving f1 directly toward and intercepted by f2

        Based on Section 4.2 "Definition of View Factors", (Modest and Mazumder, 2022, p. 150)
        Modest, M. F., and Mazumder, S. (2022). Radiative Heat Transfer. In Academic Press (Ed.), 
        Radiative Heat Transfer (4th Edition). Elsevier. https://doi.org/10.1016/c2018-0-03206-5

        Based on Section 2.2.2.3 of (Wang, 2020)
        Wang, F. (2020). Modelling of urban micro-climates for building applications: a 
        non-transparent radiative transfer approach [Univ. de Lyon]. 
        https://tel.archives-ouvertes.fr/tel-03358937
        '''
        a2 = GeomLib3D.getArea(f2)
        n1, n2 = GeomLib3D.getFaceNormalVector(f1), GeomLib3D.getFaceNormalVector(f2)
        f1Tof2 = GeomLib3D.vector_to(GeomLib3D.centroid(f1).coords[0], GeomLib3D.centroid(f2).coords[0])
        R = GeomLib3D.norm3D(f1Tof2)

        return (-a2 * GeomLib3D.dotProduct(n1, f1Tof2) * GeomLib3D.dotProduct(n2, f1Tof2)) / (pi * R ** 4)

    @staticmethod
    def monteCarlo(f1, f2, nrays, optim=False):
        if not optim:
            return SVF3DLib.__monteCarlo(f1, f2, nrays)

        if optim:
            vfs = [ SVF3DLib.__monteCarlo(f1, f2, nrays) for _ in range(5) ]
            return mean(vfs)
            
        raise IllegalArgumentTypeException(optim, 'True or False')

    @staticmethod
    def __monteCarlo(f1, f2, nrays):
        '''
        View Factor from f1 to f2: diffuse energy leaving f1 directly toward and intercepted by f2
        '''
        masks = [ GeoDataFrame([ {'geometry': f1}, {'geometry': f2} ]) ]
        ugrid = ToUnstructuredGrid(masks).run()
        obbTree = RayCastingIn3DLib.prepareVtkOBBTree(ugrid)
        maxRayLen = 2 * ugrid.length

        n1 = asarray(GeomLib3D.getFaceNormalVector(f1))
        rays = RayCasting3DLib.prepareOrientedRandomRays(nrays, n1, openness=90, method='MonteCarlo')
        shootingDirs = maxRayLen * rays

        epsilon = 1e-6
        srcPt = asarray(GeomLib3D.centroid(f1).coords[0]) + epsilon * n1
        dstPts = srcPt + shootingDirs
        srcPts = srcPt.reshape(1, -1).repeat(len(dstPts), axis=0)

        rays, _, hitDists, _ = RayCastingIn3DLib.mraycastObbTree(obbTree, srcPts, dstPts)

        '''
        # DEBUG
        rows = []
        for i in range(len(rays)):
            if (hitDists[i] != RayCastingIn3DLib.INFINITY):
                row = {
                    'hit': 1 if (hitDists[i] == RayCastingIn3DLib.INFINITY) else 2,
                    'geometry': LineString(rays[i]),
                    }
                rows.append(row)
        gdf1 = GeoDataFrame(data=[ {'gid':1, 'geometry': f1}, {'gid':2, 'geometry': f2} ])
        gdf2 = GeoDataFrame(data=rows)
        scene = ToUnstructuredGrid([gdf1, gdf2], fieldname='gid').run()
        scene.plot(show_edges=True)
        '''

        return len([d for d in hitDists if (d != RayCastingIn3DLib.INFINITY)]) / len(hitDists)

    @staticmethod
    def nusseltUnitSphere(f1, f2):
        '''
        Based on Section 4.9 "The Unit Sphere Method", (Modest and Mazumder, 2022, p. 150)

        Modest, M. F., and Mazumder, S. (2022). Radiative Heat Transfer. In Academic Press (Ed.), 
        Radiative Heat Transfer (4th Edition). Elsevier. https://doi.org/10.1016/c2018-0-03206-5
        '''
        return SVF3DLib.__infinitesimalSurfaceApproximation(f1, f2)

    @staticmethod
    def __subdivide(f1, n):
        coords = list(f1.exterior.coords)
        if (coords[0] == coords[-1]):
            coords = coords[0:-1]
        
        result = []
        if (3 == len(coords)):
            a, b, c = coords
            u = asarray(GeomLib3D.vector_to(a, b)) / n
            v = asarray(GeomLib3D.vector_to(a, c)) / n
            a = asarray(a)
            for l in range(n):
                for c in range(n - l):
                    p = Polygon([
                        a + c * u + l * v,
                        a + (c + 1) * u + l * v,
                        a + c * u + (l + 1) * v,
                        ])
                    result.append(p)
                    if (c + 1) < (n - l):
                        p = Polygon([
                            a + (c + 1) * u + l * v,
                            a + (c + 1) * u + (l + 1) * v,
                            a + c * u + (l + 1) * v,
                            ])
                        result.append(p)
            return result

        elif(4 == len(coords)):
            a, b, c, d = coords
            u = asarray(GeomLib3D.vector_to(a, b)) / n
            v = asarray(GeomLib3D.vector_to(a, d)) / n
            a = asarray(a)
            for l in range(n):
                for c in range(n):
                    p = Polygon([
                        a + c * u + l * v,
                        a + (c + 1) * u + l * v,
                        a + (c + 1) * u + (l + 1) * v,
                        a + c * u + (l + 1) * v,
                        ])
                    result.append(p)
            return result
        raise 'The subdivide(...) method expects a triangle or a rectangle!'

    @staticmethod
    def subdivideLeft(f1, f2):
        if SVF3DLib.isFiveTimeRuleTrue(f1, f2):
            return [f1]
        else:
            _, diam1 = Diameter3DLib.diameter3D(f1)
            dist12 = GeomLib3D.distFromTo(GeomLib3D.centroid(f1).coords[0], GeomLib3D.centroid(f2).coords[0])

            n = int(ceil((5 * diam1) / (dist12)))
            return SVF3DLib.__subdivide(f1, n)
