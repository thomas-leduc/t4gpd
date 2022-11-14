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
from warnings import warn

from geopandas.geodataframe import GeoDataFrame
from numpy import arcsin, array_equal, asarray, ceil, cos, dot, linspace, \
    meshgrid, multiply, ones, pi, resize, sin, sqrt, sum, vstack, where
from numpy.linalg import norm
from numpy.random import uniform
from pyvista import Sphere
from shapely.geometry.linestring import LineString
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RotationLib import RotationLib
from t4gpd.commons.SphericalCartesianCoordinates import SphericalCartesianCoordinates
from t4gpd.pyvista.GeodeCiel import GeodeCiel
from t4gpd.pyvista.Icosahedron import Icosahedron


class RayCasting3DLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def fromThetaPhiToNCells(theta, phi): 
        if (3 <= theta) and (3 <= phi):
            # ~ return theta * ((phi - 1 - 2) * 2 + 2)
            return 2 * theta * (phi - 2)
        return 6

    @staticmethod
    def fromNCellsToThetaPhi(n_cells): 
        theta = ceil(sqrt(n_cells))
        phi = ceil(theta / 2) + 2
        return theta.astype(int), phi.astype(int), RayCasting3DLib.fromThetaPhiToNCells(theta, phi)

    @staticmethod
    def preparePanopticRays(nrays, method='geodeciel'):
        if ('pyvista' == method):
            theta, phi, _ = RayCasting3DLib.fromNCellsToThetaPhi(nrays)
            sphere = Sphere(radius=1.0, center=(0, 0, 0), direction=(0, 0, 1),
                            theta_resolution=theta, phi_resolution=phi)
            shootingDirs = asarray(sphere.cell_centers().points)
        elif ('geodeciel' == method):
            norecursions = GeodeCiel.fromNRaysToNRecursions(nrays)
            shootingDirs = asarray(GeodeCiel(norecursions).getRays())
        elif ('icosahedron' == method):
            norecursions = Icosahedron.fromNRaysToNRecursions(nrays)
            shootingDirs = asarray(Icosahedron(norecursions).getRays())
        elif ('basic' == method):
            angles = linspace(0, pi / 2, ceil(sqrt(nrays)).astype(int))
            lat, lon = meshgrid(angles, angles)
            lat, lon = lat.reshape(-1), lon.reshape(-1)
            cosLat = cos(lat) 
            x, y, z = cosLat * cos(lon), cosLat * sin(lon), sin(lat)
            xyz = vstack([x, y, z]).T
            shootingDirs = vstack([
                multiply(sign, xyz)
                for sign in [
                    (1, 1, 1), (-1, 1, 1), (1, -1, 1), (-1, -1, 1),
                    (1, 1, -1), (-1, 1, -1), (1, -1, -1), (-1, -1, -1)
                    ]
                ])
        elif ('MonteCarlo' == method):
            shootingDirs = RayCasting3DLib.preparePanopticRandomRays(nrays)
        else:
            raise IllegalArgumentTypeException(method, "'geodeciel', 'icosahedron', 'pyvista', 'MonteCarlo' or 'basic'")
        print(f"{method}:: Let's prepare {len(shootingDirs)} rays!")
        return shootingDirs

    @staticmethod
    def preparePanopticRaysAndWeights(nrays, method='geodeciel'):
        if ('pyvista' == method):
            theta, phi, _ = RayCasting3DLib.fromNCellsToThetaPhi(nrays)
            sphere = Sphere(radius=1.0, center=(0, 0, 0), direction=(0, 0, 1),
                            theta_resolution=theta, phi_resolution=phi)
            shootingDirs = asarray(sphere.cell_centers().points)
            _areas = sphere.compute_cell_sizes(length=False, area=True, volume=False)
            _areas = _areas.cell_data.get_array('Area').tolist()
            _sumOfAreas = sum(_areas)
            weights = [_area / _sumOfAreas for _area in _areas]

        elif ('geodeciel' == method):
            norecursions = GeodeCiel.fromNRaysToNRecursions(nrays)
            shootingDirs, weights = GeodeCiel(norecursions).getRaysAndWeights()

        elif ('icosahedron' == method):
            norecursions = Icosahedron.fromNRaysToNRecursions(nrays)
            shootingDirs, weights = Icosahedron(norecursions).getRaysAndWeights()

        elif ('basic' == method):
            angles = linspace(0, pi / 2, ceil(sqrt(nrays)).astype(int))
            lat, lon = meshgrid(angles, angles)
            lat, lon = lat.reshape(-1), lon.reshape(-1)
            cosLat = cos(lat) 
            x, y, z = cosLat * cos(lon), cosLat * sin(lon), sin(lat)
            xyz = vstack([x, y, z]).T
            shootingDirs = vstack([
                multiply(sign, xyz)
                for sign in [
                    (1, 1, 1), (-1, 1, 1), (1, -1, 1), (-1, -1, 1),
                    (1, 1, -1), (-1, 1, -1), (1, -1, -1), (-1, -1, -1)
                    ]
                ])
            weights = ones(shape=len(shootingDirs)) / len(shootingDirs)

        elif ('MonteCarlo' == method):
            shootingDirs = RayCasting3DLib.preparePanopticRandomRays(nrays)
            weights = ones(shape=len(shootingDirs)) / len(shootingDirs)

        else:
            raise IllegalArgumentTypeException(method, "'geodeciel', 'icosahedron', 'pyvista', 'MonteCarlo' or 'basic'")
        print(f"{method}:: Let's prepare {len(shootingDirs)} rays and weights!")
        return asarray(shootingDirs), asarray(weights)

    @staticmethod
    def prepareOrientedRandomRays2(nrays, main_direction, openness=20):
        _, lon_n, lat_n = SphericalCartesianCoordinates.fromCartesianToSphericalCoordinates(*main_direction)
        openness = (pi * openness) / 180

        u = sqrt(uniform(low=0, high=1, size=nrays))
        v = uniform(low=0, high=2 * pi, size=nrays)

        # LONGITUDE, LATITUDE
        lon, lat = lon_n + openness * u * cos(v), lat_n + openness * u * sin(v)

        # FROM LONGITUDE AND LATITUDE TO CARTESIAN COORDINATES
        cosLat = cos(lat)
        x, y, z = cos(lon) * cosLat, sin(lon) * cosLat, sin(lat)

        return vstack([x, y, z]).T 

    @staticmethod
    def prepareOrientedRandomRays(nrays, main_direction, openness=20, method='MonteCarlo'):
        openness = (pi * openness) / 180
        cosOpenness = cos(openness)
        main_direction = main_direction / norm(main_direction)

        if ('MonteCarlo' == method):
            safetyFactor = 1.6
            nrays2 = int(safetyFactor * 2 * nrays / (1 - cos(openness)))
            rays = RayCasting3DLib.preparePanopticRandomRays(nrays2)
            dotProducts = dot(rays, main_direction)
            indices = where(dotProducts >= cosOpenness)[0]
            if (nrays > len(indices)):
                warn(f'In the Monte Carlo approach, safetyFactor should be greater than {safetyFactor}!')
            return resize(rays[indices,:], (nrays, 3))

        else:
            u = sqrt(uniform(low=0, high=1, size=nrays))
            v = uniform(low=0, high=2 * pi, size=nrays)

            # LONGITUDE, LATITUDE
            lon, lat = openness * u * cos(v), openness * u * sin(v)

            # FROM LONGITUDE AND LATITUDE TO CARTESIAN COORDINATES
            cosLat = cos(lat)
            x, y, z = cos(lon) * cosLat, sin(lon) * cosLat, sin(lat)

            inCoords = vstack([x, y, z]).T

            if array_equal([1, 0, 0], main_direction):
                outCoords = inCoords
            else:
                R = RotationLib.makeRotationMatrix([1, 0, 0], main_direction)
                outCoords = asarray([dot(R, inCoord) for inCoord in inCoords])
            return outCoords

    @staticmethod
    def preparePanopticRandomRays(nrays):
        # INSPIRED BY:
        # https://mathworld.wolfram.com/SpherePointPicking.html
        u, v = uniform(low=0, high=1, size=[2, nrays])

        # LONGITUDE, LATITUDE
        lon, lat = 2 * pi * u, arcsin(2 * v - 1)

        # FROM LONGITUDE AND LATITUDE TO CARTESIAN COORDINATES
        cosLat = cos(lat)
        x, y, z = cos(lon) * cosLat, sin(lon) * cosLat, sin(lat)

        return vstack([x, y, z]).T 

    @staticmethod
    def intoGeoDataFrame(rays, origin=[0, 0, 0]):
        rows = []
        for xyz in rays:
            rows.append({'geometry': LineString([
                origin,
                [origin[0] + xyz[0], origin[1] + xyz[1], origin[2] + xyz[2]]
                ])})
        return GeoDataFrame(rows)
