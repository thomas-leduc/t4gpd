"""
Created on 8 Sep. 2025

@author: tleduc

Copyright 2020-2026 Thomas Leduc

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
from numpy import atan2, cos, deg2rad, full, linspace, pi, rad2deg, round, sin
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
        degrees=False,
        method=1,
    ):
        """
        Constructor
        """
        if not isinstance(skymaps, GeoDataFrame):
            raise IllegalArgumentTypeException(skymaps, "skymaps GeoDataFrame")
        if anglesFieldname not in skymaps.columns:
            raise Exception(f"{anglesFieldname} is not a relevant field name!")
        if 1 != skymaps[anglesFieldname].apply(lambda t: len(t)).nunique():
            raise Exception(
                f"All {anglesFieldname} field values must have the same length!"
            )
        self.skymaps = skymaps
        self.anglesFieldname = anglesFieldname

        nrays = len(skymaps.iloc[0][anglesFieldname])
        self.dw = 1 + ncols // nrays
        self.nrows = nrows
        self.ncols = nrays * self.dw
        self.degrees = degrees

        if method not in [1, 2]:
            raise IllegalArgumentTypeException(method, "1 or 2")
        self.method = method

    @staticmethod
    def __to_equirectangular_map(nrows, ncols, dw, angles, degrees, method):
        if 1 == method:
            _angles = angles if degrees else rad2deg(angles)
            thresholds = round((nrows * _angles) / 90).astype(int)
        elif 2 == method:
            _angles = deg2rad(angles) if degrees else angles
            thresholds = round(nrows * sin(_angles)).astype(int)

        raster = full((nrows, ncols), fill_value=0, dtype=int)

        for i, nr in enumerate(thresholds):
            raster[0:nr, i * dw : (i + 1) * dw] = 1

        raster = raster[::-1, :]  # flip vertically
        return raster

    def run(self):
        equirectangul = self.skymaps.copy(deep=True)
        equirectangul["equirectangular_map"] = equirectangul.apply(
            lambda row: self.__to_equirectangular_map(
                self.nrows,
                self.ncols,
                self.dw,
                row[self.anglesFieldname],
                self.degrees,
                self.method,
            ),
            axis=1,
        )
        return equirectangul

    def test(method=1, ofile=None):
        import matplotlib.pyplot as plt
        from shapely import Point
        from t4gpd.commons.encoding.EncodingIndices import EncodingIndices
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        dw = 10
        h0 = 0
        buildings = GeoDataFrameDemos.regularGridOfPlots(2, 2, dw=dw)
        buildings = buildings.head(3)
        buildings["HAUTEUR"] = dw
        viewpoints = GeoDataFrame(
            [{"gid": 1, "geometry": Point(0, 0, h0)}], crs=buildings.crs
        )

        rayLength = 100.0
        nRays = 360
        osensors = SensorBasedEncodingLib.encode25D(
            viewpoints, buildings, "HAUTEUR", h0, rayLength, nRays
        )

        osensors = EncodingIndices.svf_indices(osensors, angles="angles")

        equirectangul = STFromSkyMapToEquirectangularMap(
            osensors,
            anglesFieldname="angles",
            ncols=1024,
            nrows=768,
            degrees=False,
            method=method,
        ).run()

        projectionName = "Stereographic"
        size = dw
        smaps = SkymapBuilder.build(
            osensors, "angles", proj=projectionName, size=size, copy=True
        )

        equirectangular_map = equirectangul.loc[0, "equirectangular_map"]

        fig, axes = plt.subplots(
            nrows=1, ncols=2, figsize=(1.5 * 8.26, 0.5 * 8.26), squeeze=False
        )
        fig.suptitle(f"h0 = {h0} m", fontsize=20)

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
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)

        return osensors

    def test2(method=1, ofile=None):
        import matplotlib.pyplot as plt
        from shapely import Point
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        dw = 10
        h0 = 0
        buildings = GeoDataFrameDemos.regularGridOfPlots(2, 2, dw=dw)
        buildings = buildings.head(3)
        buildings["HAUTEUR"] = dw
        viewpoints = GeoDataFrame(
            [{"gid": 1, "geometry": Point(0, 0, h0)}], crs=buildings.crs
        )

        rayLength = 100.0
        nRays = 360
        projectionName = "Stereographic"
        size = dw

        smaps = STSkyMap25D(
            buildings,
            viewpoints,
            nRays=nRays,
            rayLength=rayLength,
            elevationFieldname="HAUTEUR",
            h0=h0,
            size=size,
            epsilon=1e-1,
            projectionName=projectionName,
            withIndices=True,
            withAngles=True,
        ).run()

        equirectangul = STFromSkyMapToEquirectangularMap(
            smaps,
            anglesFieldname="angles",
            ncols=1024,
            nrows=768,
            degrees=True,
            method=method,
        ).run()
        equirectangular_map = equirectangul.loc[0, "equirectangular_map"]

        fig, axes = plt.subplots(
            nrows=1, ncols=2, figsize=(1.5 * 8.26, 0.5 * 8.26), squeeze=False
        )
        fig.suptitle(f"h0 = {h0} m", fontsize=20)

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
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)

        return smaps

    def test3(method=1, ofile=None):
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar
        from rasterio import Affine
        from shapely import Point, Polygon
        from t4gpd.commons.encoding.EncodingIndices import EncodingIndices
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
        from t4gpd.commons.raster.RasterLib import RasterLib

        d, h0 = 2, 1.1
        buildings = GeoDataFrame(
            [
                {
                    "gid": 1,
                    "HAUTEUR": d,
                    "geometry": Polygon(
                        [
                            (d, d, d),
                            (2 * d, d, d),
                            (2 * d, 2 * d, d),
                            (3 * d, 2 * d, d),
                            (3 * d, 3 * d, d),
                            (d, 3 * d, d),
                            (d, d, d),
                        ]
                    ).normalize(),
                }
            ],
            crs="epsg:2154",
        )
        eps = 1e-2
        viewpoints = GeoDataFrame(
            [
                {"gid": 0, "geometry": Point(d - eps, 2 * d, h0)},
                {"gid": 1, "geometry": Point(2 * d + eps, 2 * d - eps, h0)},
            ],
            crs=buildings.crs,
        )

        rayLength = 100.0
        nRays = 360
        osensors = SensorBasedEncodingLib.encode25D(
            viewpoints, buildings, "HAUTEUR", h0, rayLength, nRays
        )

        osensors = EncodingIndices.svf_indices(osensors, angles="angles")

        ncols, nrows = 1024, 768
        equirectangul = STFromSkyMapToEquirectangularMap(
            osensors,
            anglesFieldname="angles",
            ncols=ncols,
            nrows=nrows,
            degrees=False,
            method=method,
        ).run()

        projectionName = "Stereographic"
        size = d / 2
        smaps = SkymapBuilder.build(
            osensors, "angles", proj=projectionName, size=size, copy=True
        )

        fig, axes = plt.subplots(
            nrows=2, ncols=2, figsize=(1.5 * 8.26, 1.65 * 8.26), squeeze=False
        )
        fig.suptitle(
            f"method #{method} --- h0 = {h0} m --- $\\epsilon$={eps}", fontsize=20
        )

        for i, gid in enumerate(viewpoints.gid):
            ax = axes[i, 0]
            svf_geom = smaps.query("gid == @gid").svf_geom.iat[0]
            svf_rad = smaps.query("gid == @gid").svf_rad.iat[0]
            ax.set_title(
                f"svf_geom={svf_geom:.3f} --- svf_rad={svf_rad:.3f}", fontsize=16
            )
            smaps.query("gid == @gid").plot(ax=ax, color="black", linewidth=2)
            buildings.boundary.plot(ax=ax, color=None, hatch="...")
            buildings.apply(
                lambda x: ax.annotate(
                    text=f"H={x.HAUTEUR}",
                    xy=x.geometry.centroid.coords[0],
                    color="red",
                    size=18,
                    ha="center",
                ),
                axis=1,
            )
            viewpoints.query("gid == @gid").plot(ax=ax, color="red", markersize=50)
            ax.axis("off")
            scalebar = ScaleBar(
                dx=1.0,
                units="m",
                length_fraction=None,
                width_fraction=0.005,
                location="lower left",
                frameon=True,
            )
            ax.add_artist(scalebar)

            ax = axes[i, 1]
            equirectangular_map = equirectangul.query(
                "gid == @gid"
            ).equirectangular_map.iat[0]
            ax.imshow(equirectangular_map, cmap="viridis")

            # SERIALIZATION
            _rd = equirectangular_map.copy().astype("uint8")
            _rd[_rd > 0] = 255
            _rp = {
                "driver": "PNG",
                "dtype": "uint8",
                "nodata": None,
                "width": ncols,
                "height": nrows,
                "count": 1,
                "crs": None,
                "transform": Affine.identity(),
                "blockxsize": 1,
                "blockysize": 1,
                "tiled": False,
            }
            RasterLib.write(
                _rd,
                _rp,
                f"/tmp/{gid}_equirect_t4gpd.png",
            )

            ax.axis("off")

        # fig.tight_layout()
        if ofile:
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)

        return osensors

    def test4(method=1, ofile=None):
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar
        from rasterio import Affine
        from shapely import Point, Polygon
        from t4gpd.commons.encoding.EncodingIndices import EncodingIndices
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
        from t4gpd.commons.raster.RasterLib import RasterLib

        h0 = 0.0
        viewpoint = GeoDataFrame(
            [
                {"gid": 0, "geometry": Point(0, 0, h0)},
            ],
            crs="epsg:2154",
        )

        npts = 360
        W = 10
        for H in [W // 2, W, 2 * W, 4 * W, 8 * W]:
            Wpp = W + 1
            exterior = [
                (Wpp * cos(theta), Wpp * sin(theta), H)
                for theta in linspace(0, 2 * pi, num=npts)
            ]
            interior = [
                (W * cos(theta), W * sin(theta), H)
                for theta in linspace(0, 2 * pi, num=npts)
            ]
            buildings = GeoDataFrame(
                [
                    {
                        "gid": 1,
                        "HAUTEUR": H,
                        "geometry": Polygon(exterior, holes=[interior]).normalize(),
                    }
                ],
                crs=viewpoint.crs,
            )

            rayLength = 2 * W
            nRays = 360
            osensors = SensorBasedEncodingLib.encode25D(
                viewpoint, buildings, "HAUTEUR", h0, rayLength, nRays
            )
            osensors = EncodingIndices.svf_indices(osensors, angles="angles")

            ncols, nrows = 1024, 768
            equirectangul = STFromSkyMapToEquirectangularMap(
                osensors,
                anglesFieldname="angles",
                ncols=ncols,
                nrows=nrows,
                degrees=False,
                method=method,
            ).run()

            projectionName = "Stereographic"
            projectionName = "Orthogonal"
            size = W / 2
            smaps = SkymapBuilder.build(
                osensors, "angles", proj=projectionName, size=size, copy=True
            )

            # MAPPING
            fig, axes = plt.subplots(
                nrows=1, ncols=2, figsize=(1.5 * 8.26, 0.9 * 8.26), squeeze=False
            )
            fig.suptitle(
                f"""method #{method}, H={H} m, W={W} m
cos(atan(H/W))={cos(atan2(H, W)):.3f}, cos$^2$(atan(H/W))={cos(atan2(H, W))**2:.3f}""",
                fontsize=20,
            )

            ax = axes[0, 0]
            svf_geom = smaps.svf_geom.iat[0]
            svf_rad = smaps.svf_rad.iat[0]
            ax.set_title(
                f"svf_geom={svf_geom:.3f} --- svf_rad={svf_rad:.3f}", fontsize=16
            )
            smaps.plot(ax=ax, color="yellow", alpha=0.7)
            buildings.plot(ax=ax, color="grey", hatch="...")
            buildings.apply(
                lambda x: ax.annotate(
                    text=f"H={x.HAUTEUR}",
                    xy=x.geometry.exterior.coords[0][:2],
                    color="red",
                    size=18,
                    ha="right",
                ),
                axis=1,
            )
            viewpoint.plot(ax=ax, color="red", marker="+", markersize=50)
            ax.axis("off")
            scalebar = ScaleBar(
                dx=1.0,
                units="m",
                length_fraction=None,
                width_fraction=0.005,
                location="lower left",
                frameon=True,
            )
            ax.add_artist(scalebar)

            ax = axes[0, 1]
            equirectangular_map = equirectangul.equirectangular_map.iat[0]
            ax.imshow(equirectangular_map, cmap="viridis")

            # SERIALIZATION
            _rd = equirectangular_map.copy().astype("uint8")
            _rd[_rd > 0] = 255
            _rp = {
                "driver": "PNG",
                "dtype": "uint8",
                "nodata": None,
                "width": ncols,
                "height": nrows,
                "count": 1,
                "crs": None,
                "transform": Affine.identity(),
                "blockxsize": 1,
                "blockysize": 1,
                "tiled": False,
            }
            RasterLib.write(
                _rd,
                _rp,
                f"/tmp/equirect_t4gpd_H{H}_W{W}_raw.png",
            )

            ax.axis("off")

            fig.tight_layout()
            if ofile is None:
                plt.show()
            else:
                plt.savefig(f"/tmp/equirect_t4gpd_H{H}_W{W}.png", bbox_inches="tight")
            plt.close(fig)

        return osensors


"""
for method in [1, 2]:
    osensors = STFromSkyMapToEquirectangularMap.test(
        method=method,
        ofile=None,
        # ofile=f"/tmp/equirectangular_map_{method}.png",
    )
"""

"""
for method in [1, 2]:
    smaps = STFromSkyMapToEquirectangularMap.test2(
        method=method,
        ofile=None,
        # ofile=f"/tmp/equirectangular_map_{method}.png",
    )
"""

"""
for method in [1, 2]:
    osensors = STFromSkyMapToEquirectangularMap.test3(
        method=method,
        ofile=None,
        # ofile=f"/tmp/equirectangular_map_{method}.png",
    )
"""

"""
for method in [1]:
    STFromSkyMapToEquirectangularMap.test4(
        method=method,
        ofile=None,
        # ofile=True,
    )
"""
