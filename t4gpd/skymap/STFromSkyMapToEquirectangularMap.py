"""
Created on 8 Sep. 2025

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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
"""

from geopandas import GeoDataFrame
from numpy import full
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STFromSkyMapToEquirectangularMap(GeoProcess):
    """
    classdocs
    """

    __slots__ = ("skymaps", "anglesFieldname", "ncols", "nrows")

    def __init__(
        self,
        skymaps: GeoDataFrame,
        anglesFieldname="angles",
        ncols=1024,
        nrows=768,
    ):
        """
        Constructor
        """
        if not isinstance(skymaps, GeoDataFrame):
            raise IllegalArgumentTypeException(skymaps, "skymaps GeoDataFrame")
        if not anglesFieldname in skymaps.columns:
            raise Exception(f"{anglesFieldname} is not a relevant field name!")
        if 1 != skymaps[anglesFieldname].apply(lambda t: len(t)).nunique():
            raise Exception(
                f"All {anglesFieldname} field values must have the same length!"
            )
        self.skymaps = skymaps
        self.anglesFieldname = anglesFieldname

        nrays = skymaps.iloc[0][anglesFieldname].size
        self.dw = 1 + ncols // nrays
        self.nrows = nrows
        self.ncols = nrays * self.dw

    @staticmethod
    def __to_equirectangular_map(nrows, ncols, dw, angles):
        raster = full((nrows, ncols), fill_value=0, dtype=int)

        for i, angle in enumerate(angles):
            nr = int((nrows * angle) // 90)
            raster[0:nr, i * dw : (i + 1) * dw] = 1

        raster = raster[::-1, :]  # flip vertically
        return raster

    def run(self):
        equirectangul = self.skymaps.copy(deep=True)
        equirectangul["equirectangular_map"] = equirectangul.apply(
            lambda row: self.__to_equirectangular_map(
                self.nrows, self.ncols, self.dw, row[self.anglesFieldname]
            ),
            axis=1,
        )
        return equirectangul

    def test(ofile=None):
        import matplotlib.pyplot as plt
        from shapely import Point
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        dw = 10
        buildings = GeoDataFrameDemos.regularGridOfPlots(2, 2, dw=dw)
        buildings = buildings.head(3)
        buildings["HAUTEUR"] = dw
        viewpoints = GeoDataFrame(
            [{"gid": 1, "geometry": Point(0, 0)}], crs=buildings.crs
        )
        smaps = STSkyMap25D(
            buildings,
            viewpoints,
            nRays=360,
            rayLength=100.0,
            elevationFieldname="HAUTEUR",
            h0=0.0,
            size=dw,
            epsilon=1e-1,
            projectionName="Stereographic",
            withIndices=False,
            withAngles=True,
        ).run()

        equirectangul = STFromSkyMapToEquirectangularMap(
            smaps,
            anglesFieldname="angles",
            ncols=1024,
            nrows=768,
        ).run()

        equirectangular_map = equirectangul.loc[0, "equirectangular_map"]

        fig, axes = plt.subplots(
            nrows=1, ncols=2, figsize=(1.5 * 8.26, 0.5 * 8.26), squeeze=False
        )

        ax = axes[0, 0]
        buildings.plot(ax=ax, color="dimgrey")
        smaps.plot(ax=ax, color="black", linewidth=2)
        viewpoints.plot(ax=ax, color="red", markersize=50)
        ax.axis("off")

        ax = axes[0, 1]
        ax.imshow(equirectangular_map, cmap="viridis")
        ax.axis("off")

        fig.tight_layout()
        if ofile:
            plt.savefig(
                "equirectangular_map.png", bbox_inches="tight", pad_inches=0, dpi=300
            )
        else:
            plt.show()
        plt.close(fig)

        return smaps, equirectangul


# smaps, equirectangul = STFromSkyMapToEquirectangularMap.test(
#     ofile="equirectangular_map.png"
# )
