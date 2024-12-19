'''
Created on 30 oct. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from numpy import asarray, deg2rad, ndarray, r_
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.SVFLib import SVFLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class OrientedSVF(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, skymaps, anglesFieldname="angles", method="quadrants", svf=2018):
        '''
        Constructor
        '''
        if not isinstance(skymaps, GeoDataFrame):
            raise IllegalArgumentTypeException(skymaps, "GeoDataFrame")
        self.skymaps = skymaps

        if anglesFieldname not in skymaps:
            raise Exception(f"{anglesFieldname} is not a relevant field name!")
        self.anglesFieldname = anglesFieldname

        method = method.lower()
        if ("quadrants" == method):
            offset = 8
        elif ("octants" == method):
            offset = 16
        elif ("duodecants" == method):
            offset = 24
        else:
            raise IllegalArgumentTypeException(
                method, "'quadrants', 'octants', or 'duodecants'")

        for angles in self.skymaps[self.anglesFieldname]:
            if (isinstance(angles, (list, ndarray, tuple)) and (0 == len(angles) % offset)):
                n = len(angles) // offset
                break
            raise Exception(
                f"\n{angles}\n\nmust be a collection of angles whose length is a multiple of {offset}.")

        if (1981 == svf):
            print(
                f"SVF calculation method: Oke (1981)")
            self.svf = SVFLib.svfAngles1981
        else:
            print(
                f"SVF calculation method: Bernard et al. (2018)")
            self.svf = SVFLib.svfAngles2018

        if (8 == offset):
            self.quadrants = [
                slice(n, 3*n),  # north
                r_[slice(7*n, 8*n), slice(0, n)],  # east
                slice(5*n, 7*n),  # south
                slice(3*n, 5*n),  # west
            ]
            self.method = self.__quadrants
        elif (16 == offset):
            self.octants = [
                slice(3*n, 5*n),  # north
                slice(n, 3*n),  # northeast
                r_[slice(15*n, 16*n), slice(0, n)],  # east
                slice(13*n, 15*n),  # southeast
                slice(11*n, 13*n),  # south
                slice(9*n, 11*n),  # southwest
                slice(7*n, 9*n),  # west
                slice(5*n, 7*n),  # northwest
            ]
            self.method = self.__octants
        elif (24 == offset):
            self.duodecants = [
                slice(5*n, 7*n),  # north
                slice(3*n, 5*n),  # north-northeast
                slice(n, 3*n),  # east-northeast
                r_[slice(23*n, 24*n), slice(0, n)],  # east
                slice(21*n, 23*n),  # east-southeast
                slice(19*n, 21*n),  # south-southeast
                slice(17*n, 19*n),  # south
                slice(15*n, 17*n),  # south-southwest
                slice(13*n, 15*n),  # west-southwest
                slice(11*n, 13*n),  # west
                slice(9*n, 11*n),  # west-northwest
                slice(7*n, 9*n),  # north-northwest
            ]
            self.method = self.__duodecants
        else:
            raise Exception("Unreachable instruction!")

    def __quadrants(self, angles):
        north, east, south, west = self.quadrants
        north = self.svf(deg2rad(angles[north]))
        east = self.svf(deg2rad(angles[east]))
        south = self.svf(deg2rad(angles[south]))
        west = self.svf(deg2rad(angles[west]))
        return {
            "svf4_north": north,
            "svf4_east": east,
            "svf4_south": south,
            "svf4_west": west,
        }

    def __octants(self, angles):
        north, northeast, east, southeast, south, southwest, west, northwest = self.octants
        north = self.svf(deg2rad(angles[north]))
        northeast = self.svf(deg2rad(angles[northeast]))
        east = self.svf(deg2rad(angles[east]))
        southeast = self.svf(deg2rad(angles[southeast]))
        south = self.svf(deg2rad(angles[south]))
        southwest = self.svf(deg2rad(angles[southwest]))
        west = self.svf(deg2rad(angles[west]))
        northwest = self.svf(deg2rad(angles[northwest]))

        return {
            "svf8_north": north,
            "svf8_northeast": northeast,
            "svf8_east": east,
            "svf8_southeast": southeast,
            "svf8_south": south,
            "svf8_southwest": southwest,
            "svf8_west": west,
            "svf8_northwest": northwest,
        }

    def __duodecants(self, angles):
        n, nne, ene, e, ese, sse, s, ssw, wsw, w, wnw, nnw = self.duodecants
        n = self.svf(deg2rad(angles[n]))
        nne = self.svf(deg2rad(angles[nne]))
        ene = self.svf(deg2rad(angles[ene]))
        e = self.svf(deg2rad(angles[e]))
        ese = self.svf(deg2rad(angles[ese]))
        sse = self.svf(deg2rad(angles[sse]))
        s = self.svf(deg2rad(angles[s]))
        ssw = self.svf(deg2rad(angles[ssw]))
        wsw = self.svf(deg2rad(angles[wsw]))
        w = self.svf(deg2rad(angles[w]))
        wnw = self.svf(deg2rad(angles[wnw]))
        nnw = self.svf(deg2rad(angles[nnw]))

        return {
            "svf12_n": n,
            "svf12_nne": nne,
            "svf12_ene": ene,
            "svf12_e": e,
            "svf12_ese": ese,
            "svf12_sse": sse,
            "svf12_s": s,
            "svf12_ssw": ssw,
            "svf12_wsw": wsw,
            "svf12_w": w,
            "svf12_wnw": wnw,
            "svf12_nnw": nnw,
        }

    def runWithArgs(self, row):
        angles = asarray(row[self.anglesFieldname])
        if not isinstance(angles, (list, ndarray, tuple)):
            raise IllegalArgumentTypeException(
                angles, "list, ndarray or tuple")

        return self.method(angles)

    @staticmethod
    def test(method="octants"):
        import matplotlib.pyplot as plt
        from numpy import sqrt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STGrid import STGrid
        from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
        from t4gpd.morph.geoProcesses.Translation import Translation
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        viewpoints = STGrid(buildings, dx=80, indoor=False,
                            intoPoint=True).run()
        viewpoints.sort_values(by="gid", inplace=True)
        viewpoints.drop(
            columns=["row", "column", "neighbors4", "neighbors8", "indoor"], inplace=True)
        # viewpoints = viewpoints.loc[viewpoints[viewpoints.gid == 8].index]

        nRays = 48 # 96
        skymaps = STSkyMap25D(
            buildings, viewpoints, nRays=nRays, rayLength=100,
            elevationFieldname="HAUTEUR", h0=0, size=4,
            withIndices=True, withAngles=True, encode=False).run()

        op = OrientedSVF(skymaps, "angles", method=method, svf=2018)
        skymaps2 = STGeoProcess(op, skymaps).run()

        # PLOTTING
        vmin, vmax = 0, 1.0

        fig, ax = plt.subplots(figsize=(1.5*8.26, 1.15*8.26))
        buildings.plot(ax=ax, color="grey")
        viewpoints.plot(ax=ax, color="red", marker="P")
        skymaps.set_geometry("viewpoint").plot(
            ax=ax, alpha=0.5, column="svf", cmap="viridis",
            vmin=vmin, vmax=vmax, legend=True,
            legend_kwds={"label": "svf*"})
        skymaps.apply(lambda x: ax.annotate(
            text=f"{x['svf']:.2f}", xy=x.geometry.centroid.coords[0],
            color="red", size=12, ha="center"), axis=1)

        if ("quadrants" == method):
            dxy = 10
            trios = [
                ("svf4_north", 0, dxy), ("svf4_east", dxy, 0),
                ("svf4_south", 0, -dxy), ("svf4_west", -dxy, 0),
            ]
        elif ("octants" == method):
            dxy = 10
            trios = [
                ("svf8_north", 0, dxy), ("svf8_northeast", dxy, dxy),
                ("svf8_east", dxy, 0), ("svf8_southeast", dxy, -dxy),
                ("svf8_south", 0, -dxy), ("svf8_southwest", -dxy, -dxy),
                ("svf8_west", -dxy, 0), ("svf8_northwest", -dxy, dxy),
            ]
        elif ("duodecants" == method):
            dxy = 15
            da, db = 0.5 * dxy, (dxy * sqrt(3))/2
            trios = [
                ("svf12_n", 0, dxy), ("svf12_nne", da, db),
                ("svf12_ene", db, da), ("svf12_e", dxy, 0),
                ("svf12_ese", db, -da), ("svf12_sse", da, -db),
                ("svf12_s", 0, -dxy), ("svf12_ssw", -da, -db),
                ("svf12_wsw", -db, -da), ("svf12_w", -dxy, 0),
                ("svf12_wnw", -db, da), ("svf12_nnw", -da, db),
            ]
        for indic, dx, dy in trios:
            op = Translation((dx, dy))
            skymaps3 = STGeoProcess(op, skymaps2).run()
            skymaps3.plot(ax=ax, alpha=0.5, column=indic,
                          cmap="viridis", vmin=vmin,
                          vmax=vmax)
            skymaps3.apply(lambda x: ax.annotate(
                text=f"{x[indic]:.2f}", xy=x.geometry.centroid.coords[0],
                color="black", size=12, ha="center"), axis=1)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return viewpoints, skymaps, skymaps2


# viewpoints, skymaps, skymaps2 = OrientedSVF.test()
