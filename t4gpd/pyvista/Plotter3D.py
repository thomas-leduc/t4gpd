'''
Created on 24 juin 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
import pyvista
from datetime import datetime, timedelta
from numpy import asarray
from pyvista import Cylinder, global_theme, Light, Plane, Plotter, Sphere, themes
from t4gpd.commons.ColorTemperature import ColorTemperature
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.FootprintExtruder import FootprintExtruder
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.ToPolyData import ToPolyData
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from zoneinfo import ZoneInfo


class Plotter3D(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, window_size=(1100, 1100), ofile=None):
        '''
        Constructor
        '''
        self.ofile = ofile

        self.plotter = Plotter(off_screen=(ofile is not None), lighting="none",
                               window_size=window_size)
        self.plotter.show_axes()
        # pyvista.set_plot_theme(themes.DarkTheme())
        # pyvista.set_plot_theme(themes.DocumentTheme())
        pyvista.set_plot_theme(themes.ParaViewTheme())

    def add_mesh(self, scene, show_scalar_bar=False, show_edges=False):
        self.plotter.add_mesh(scene, show_scalar_bar=show_scalar_bar,
                              show_edges=show_edges, smooth_shading=True)

    def add_buildings(self, buildings, show_edges=True, elevationFieldname='HAUTEUR',
                      forceZCoordToZero=True, withoutBuildingFloors=False):
        _buildings = buildings.explode(ignore_index=True)

        op = FootprintExtruder(_buildings, elevationFieldname,
                               forceZCoordToZero, withoutBuildingFloors)
        buildingsIn3d = STGeoProcess(op, _buildings).run()

        # scene = ToUnstructuredGrid([buildingsIn3d], fieldname=None).run()
        scene = ToPolyData([buildingsIn3d], fieldname=None).run()
        self.add_mesh(scene, show_edges=show_edges)

    def add_ground_surface(self, length=None):
        xmin, xmax, ymin, ymax, zmin, zmax = self.plotter.bounds
        xc, yc, zc = self.plotter.center

        if length is None:
            length = self.plotter.length

        ground = Plane(center=[xc, yc, zmin],
                       i_size=length, j_size=length,
                       i_resolution=10, j_resolution=10)

        self.plotter.add_mesh(ground, show_edges=False, smooth_shading=True)

    def add_streetlights(self, streetlights, generalLighting=True,
                         color=[1.0, 0.83921, 0.6666, 1.0],
                         aperture=75.5, show_actor=False):
        # https://docs.pyvista.org/version/stable/examples/04-lights/actors.html
        # https://docs.pyvista.org/version/stable/api/core/_autosummary/pyvista.Light.html#pyvista.Light
        # https://docs.pyvista.org/version/stable/examples/04-lights/shadows.html
        for _, row in streetlights.iterrows():
            x0, y0, z0 = row.geometry.coords[0]

            if isinstance(color, str):
                color = row[color]
            if isinstance(aperture, str):
                aperture = row[aperture]

            # A positional light with a cone angle that is less than 90 degrees
            # is known as a spotlight
            light = Light(
                position=(x0, y0, z0),
                focal_point=(x0, y0, z0-1),
                color=color,
                intensity=1,  # brightness of the light (between 0 and 1)
                positional=True,
                cone_angle=aperture,
                exponent=10,
                show_actor=show_actor
            )
            self.plotter.add_light(light)

        #
        if generalLighting:
            xmin, xmax, ymin, ymax, zmin, zmax = self.plotter.bounds
            xc, yc, zc = self.plotter.center
            light = Light(
                position=(xc, yc, zmax+100),
                focal_point=(xc, yc, zc),
                color="dimgrey",  # "blue"
                intensity=0.35
            )
            self.plotter.add_light(light)

    def add_sun_shadows(self, dts, gdf=LatLonLib.NANTES, model="pysolar"):
        # color = [1.0, 1.0, 0.9843, 1.0],  # Color temp. 5400 K
        # color = [1.0, 0.83921, 0.6666, 1.0],  # Color temp. 2850 K
        self.plotter.enable_shadows()
        sunModel = SunLib(gdf, model)

        for i, dt in enumerate(dts):
            solarAlti, solarAzim = sunModel.getSolarAnglesInDegrees(dt)
            light = Light(
                color=ColorTemperature.convert_K_to_RGB(2850 + 1000*i),
                positional=False,
            )
            light.set_direction_angle(solarAlti, solarAzim)
            self.plotter.add_light(light)
            print(f"{dt}: alti={solarAlti:.1f}, azim={solarAzim:.1f}")

    def add_sun_positions(self, dts, radius=10, length=None,
                          gdf=LatLonLib.NANTES, model="pysolar"):
        xc, yc, zc = self.plotter.center

        if length is None:
            length = self.plotter.length/2

        sunModel = SunLib(gdf, model)

        for i, dt in enumerate(dts):
            x, y, z = sunModel.getRadiationDirection(dt)
            xyz = xc + length*x, yc + length*y, zc + length*z
            sun = Sphere(radius=radius, center=xyz)
            self.plotter.add_mesh(sun, show_edges=False,
                                  color="yellow",
                                  smooth_shading=True, opacity=1.0)

    def add_tree_cylinders(self):
        pass

    def add_tree_spheres(self, trees, trunk_height="trunk_height",
                         crown_radius="crown_radius"):
        for _, row in trees.iterrows():
            h, r = row[trunk_height], row[crown_radius],
            xyz = list(row.geometry.coords[0])[0:2] + [h]

            houppier = Sphere(radius=r, center=xyz)
            tronc = Cylinder(center=xyz[0:2] + [xyz[2]/2],
                             direction=(0.0, 0.0, 1.0),
                             radius=0.2, height=h)
            self.plotter.add_mesh(houppier, show_edges=False,
                                  smooth_shading=True, opacity=1.0)
            self.plotter.add_mesh(tronc, show_edges=False, smooth_shading=True)

    def my_cpos_callback(self):
        # tuple: camera location, focus point, viewup vector
        # camera_position = [(x,y,z), (fx,fy,fz,), (nx,ny,nz)]
        cpos = self.plotter.camera_position
        (x, y, z), (fx, fy, fz,), (nx, ny, nz) = \
            cpos.position, cpos.focal_point, cpos.viewup
        msg = f"""[({x:.2f}, {y:.2f}, {z:.2f})
 ({fx:.2f}, {fy:.2f}, {fz:.2f}),
 ({nx:.2f}, {ny:.2f}, {nz:.2f})]
"""
        # self.plotter.add_text(str(self.plotter.camera_position), name="cpos")
        self.plotter.add_text(msg, name="cpos")
        print(msg)
        return

    def run(self):
        self.plotter.add_key_event("p", self.my_cpos_callback)
        self.plotter.show(screenshot=self.ofile)


"""
tzinfo = ZoneInfo("Europe/Paris")

buildings = GeoDataFrameDemos.ensaNantesBuildings()
trees = GeoDataFrameDemos.ensaNantesTrees()
trees["trunk_height"] = 5.0
trees["crown_radius"] = 3.0

streetlights = GeoDataFrameDemos.ensaNantesTrees()
streetlights.geometry = streetlights.geometry.apply(
    lambda g: GeomLib.forceZCoordinateToZ0(g, 8.0))
streetlights = streetlights.head(6)

# ofile = "/tmp/test.png"
ofile = None
pl = Plotter3D(ofile)
pl.add_buildings(buildings, show_edges=False)
pl.add_tree_spheres(trees)
# pl.add_streetlights(streetlights, generalLighting=True)
pl.add_ground_surface()

dt0 = datetime(2021, 3, 21, 10, tzinfo=tzinfo)
pl.add_sun_shadows([dt0, dt0 + timedelta(hours=6)])

# dt0 = datetime(2021, 3, 21, 8, tzinfo=tzinfo)
# dts = [dt0 + timedelta(hours=i) for i in range(0, 12, 2)]
# pl.add_sun_positions(dts)
pl.run()
"""
