"""
Created on 30 Sep. 2025

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

import json
import numpy as np
import rasterio as rio
import warnings
from geopandas import GeoDataFrame
from rasterio.features import rasterize
from rasterio.io import MemoryFile
from rasterio.mask import mask
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from shapely import STRtree, box
from t4gpd.commons.ArrayLib import ArrayLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils


class RasterLib(object):
    """
    classdocs
    """

    pd2rio_dtypes = {
        "int8": rio.int8,
        "int16": rio.int16,
        "int32": rio.int32,
        "int64": rio.int64,
        "uint8": rio.uint8,
        "uint16": rio.uint16,
        "uint32": rio.uint32,
        "uint64": rio.uint64,
        "float32": rio.float32,
        "float64": rio.float64,
        "bool": rio.uint8,  # No boolean type in rasterio, using uint8 instead
        "object": rio.float32,  # Defaulting object to float32, may need adjustment based on actual data
    }

    @staticmethod
    def clip(raster_data, raster_profile, roi, ndv=None):
        warnings.formatwarning = WarnUtils.format_Warning_alt
        features = [json.loads(roi.to_json())["features"][0]["geometry"]]
        with MemoryFile() as memfile:
            with memfile.open(**raster_profile) as raster:
                raster.write(raster_data)  # Écriture du tableau numpy dans le dataset

                data_cropped, transform_cropped = mask(
                    dataset=raster, shapes=features, crop=True
                )

                ndv = raster_profile.get("nodata", None) if ndv is None else ndv

                profile_cropped = raster_profile.copy()
                profile_cropped.update(
                    {
                        "height": data_cropped.shape[1],
                        "nodata": ndv,
                        "transform": transform_cropped,
                        "width": data_cropped.shape[2],
                    }
                )
        warnings.warn(
            f"Clipping raster from {raster_data.shape[2]}x{raster_data.shape[1]} to {data_cropped.shape[2]}x{data_cropped.shape[1]}"
        )
        return data_cropped, profile_cropped

    @staticmethod
    def fast_rasterize(gdf, dx, dy=None, roi=None, attr=None, ndv=0):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if (not roi is None) and (not isinstance(roi, GeoDataFrame)):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")
        if (not attr is None) and (not attr in gdf):
            raise IllegalArgumentTypeException(
                attr, "must be a valid field name of the GeoDataFrame"
            )
        dy = dx if (dy is None) else dy
        roi = gdf if (roi is None) else roi
        minx, miny, maxx, maxy = roi.total_bounds
        ncols = int(np.ceil((maxx - minx) / dx))
        nrows = int(np.ceil((maxy - miny) / dy))
        xOffset = ((ncols * dx) - (maxx - minx)) / 2.0
        yOffset = ((nrows * dy) - (maxy - miny)) / 2.0

        minx, miny = minx - xOffset, miny - yOffset
        maxx, maxy = minx + ncols * dx, miny + nrows * dy
        transform = from_bounds(minx, miny, maxx, maxy, ncols, nrows)

        if attr:
            dtype = RasterLib.pd2rio_dtypes[str(gdf[attr].dtype)]
        else:
            dtype = RasterLib.pd2rio_dtypes["uint8"]

        # Create pixels grid
        x = np.linspace(minx, minx + ncols * dx, ncols, endpoint=False)
        y = np.linspace(miny, miny + nrows * dy, nrows, endpoint=False)
        X, Y = np.meshgrid(x, y)
        __foo = lambda x, y: box(x, y, x + dx, y + dy)
        pixels = np.vectorize(__foo)(X, Y).ravel()

        # Build the spatial index on the input geometries
        tree = STRtree(gdf.geometry)
        geom_values = gdf.geometry.values
        if not attr is None:
            attr_values = gdf[attr].values

        # Initialize raster data with no data value
        raster_data = np.full((nrows, ncols), ndv, dtype=dtype)

        # Check intersections
        if attr:
            for k, pix in enumerate(pixels):
                hits = tree.query(pix)
                if 0 < hits.size:
                    for hit in hits:
                        if pix.intersects(geom_values[hit]):  # .within()
                            row, col = divmod(k, ncols)
                            row = nrows - 1 - row
                            raster_data[row, col] = attr_values[hits[0]]
        else:
            for k, pix in enumerate(pixels):
                hits = tree.query(pix)
                if 0 < hits.size:
                    for hit in hits:
                        if pix.intersects(geom_values[hit]):  # .within()
                            row, col = divmod(k, ncols)
                            row = nrows - 1 - row
                            raster_data[row, col] = 1

        with MemoryFile() as memfile:
            raster_profile = {
                "driver": "GTiff",
                "height": nrows,
                "width": ncols,
                "count": 1,
                "dtype": dtype,
                "crs": gdf.crs,
                "transform": transform,
                "nodata": ndv,
            }
            with memfile.open(**raster_profile) as raster:
                raster.write(raster_data, 1)

        return raster_data, raster_profile

    @staticmethod
    def from_grid_to_raster(
        gdf, attr, rowAttr="row", colAttr="column", roi=None, ndv=0
    ):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if (not roi is None) and (not isinstance(roi, GeoDataFrame)):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")
        if (not attr is None) and (not attr in gdf):
            raise IllegalArgumentTypeException(
                attr, "must be a valid field name of the GeoDataFrame"
            )

        dtype = ArrayLib.get_compact_dtype(gdf[attr].values)

        # WITHOUT DUPLICATES
        # raster_data = gdf.pivot(index=rowAttr, columns=colAttr, values=attr).fillna(ndv).to_numpy()
        # WITH DUPLICATES
        raster_data = (
            gdf.pivot_table(index=rowAttr, columns=colAttr, values=attr, aggfunc="mean")
            .fillna(ndv)
            .to_numpy(dtype)
        )

        raster_data = raster_data[::-1, :]  # Flip vertically to match raster origin

        nrows, ncols = raster_data.shape
        dtype = RasterLib.pd2rio_dtypes[str(raster_data.dtype)]

        roi = gdf if (roi is None) else roi
        minx, miny, maxx, maxy = roi.total_bounds
        transform = from_bounds(minx, miny, maxx, maxy, ncols, nrows)

        with MemoryFile() as memfile:
            raster_profile = {
                "driver": "GTiff",
                "height": nrows,
                "width": ncols,
                "count": 1,
                "dtype": dtype,
                "crs": gdf.crs,
                "transform": transform,
                "nodata": ndv,
            }
            with memfile.open(**raster_profile) as raster:
                raster.write(raster_data, 1)

        return raster_data, raster_profile

    @staticmethod
    def from_uint16_to_uint8(raster_data, raster_profile):
        ndv = raster_profile.get("nodata")
        if ndv:
            mask = raster_data != ndv
        else:
            mask = np.ones_like(raster_data, dtype=bool)

        uint8_data = np.zeros_like(raster_data, dtype=np.uint8)
        for b in range(raster_data.shape[0]):  # boucle sur les bandes
            band = raster_data[b]
            band_mask = mask[b]
            if np.any(band_mask):
                min_val = band[band_mask].min()
                max_val = band[band_mask].max()
                # Normalisation seulement sur les pixels valides
                uint8_data[b, band_mask] = (
                    (band[band_mask] - min_val) / (max_val - min_val) * 255
                ).astype(np.uint8)

        uint8_profile = raster_profile.copy()
        uint8_profile.update(dtype=rio.uint8)
        return uint8_data, uint8_profile

    @staticmethod
    def load(ifile: str) -> tuple:
        """
        Load a raster file into a numpy array and get its profile
        :param ifile: input raster file path
        :return: raster_data, raster_profile"""
        with rio.open(ifile) as src:
            raster_data = src.read()
            raster_profile = src.profile
        return raster_data, raster_profile

    @staticmethod
    def raster_data_profile_2_memory_raster(raster_data, raster_profile):
        raster = MemoryFile()
        with raster.open(**raster_profile) as dataset:
            dataset.write(raster_data, 1)
        return raster

    @staticmethod
    def rasterize(gdf, dx, dy=None, roi=None, attr=None, ndv=0):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if (not roi is None) and (not isinstance(roi, GeoDataFrame)):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")
        if (not attr is None) and (not attr in gdf):
            raise IllegalArgumentTypeException(
                attr, "must be a valid field name of the GeoDataFrame"
            )
        dy = dx if (dy is None) else dy
        roi = gdf if (roi is None) else roi
        minx, miny, maxx, maxy = roi.total_bounds
        ncols = int(np.ceil((maxx - minx) / dx))
        nrows = int(np.ceil((maxy - miny) / dy))
        xOffset = ((ncols * dx) - (maxx - minx)) / 2.0
        yOffset = ((nrows * dy) - (maxy - miny)) / 2.0

        minx, miny = minx - xOffset, miny - yOffset
        maxx, maxy = minx + ncols * dx, miny + nrows * dy
        transform = from_bounds(minx, miny, maxx, maxy, ncols, nrows)

        if attr:
            shapes = ((geom, value) for geom, value in zip(gdf.geometry, gdf[attr]))
            dtype = RasterLib.pd2rio_dtypes[str(gdf[attr].dtype)]
        else:
            shapes = ((geom, 1) for geom in gdf.geometry)
            dtype = RasterLib.pd2rio_dtypes["uint8"]

        with MemoryFile() as memfile:
            raster_profile = {
                "driver": "GTiff",
                "height": nrows,
                "width": ncols,
                "count": 1,
                "dtype": dtype,
                "crs": gdf.crs,
                "transform": transform,
                "nodata": ndv,
            }
            with memfile.open(**raster_profile) as raster:
                raster_data = rasterize(
                    shapes=shapes,
                    out_shape=(nrows, ncols),
                    transform=transform,
                    fill=ndv,  # background value
                    dtype=dtype,
                )
                raster.write(raster_data, 1)

        return raster_data, raster_profile

    @staticmethod
    def resize(raster_data, raster_profile, nrows, ncols):
        warnings.formatwarning = WarnUtils.format_Warning_alt
        o_raster_data = np.empty(
            (raster_data.shape[0], nrows, ncols), dtype=raster_data.dtype
        )
        for band in range(raster_data.shape[0]):
            reproject(
                source=raster_data[band],
                destination=o_raster_data[band],
                src_transform=raster_profile["transform"],
                dst_transform=raster_profile["transform"]
                * raster_profile["transform"].scale(
                    (raster_data.shape[2] / ncols), (raster_data.shape[1] / nrows)
                ),
                src_crs=raster_profile["crs"],
                dst_crs=raster_profile["crs"],
                resampling=Resampling.average,  # Pixel averaging
            )
        o_raster_profile = raster_profile.copy()
        o_raster_profile.update(
            width=ncols,
            height=nrows,
            transform=raster_profile["transform"]
            * raster_profile["transform"].scale(
                (raster_data.shape[2] / ncols), (raster_data.shape[1] / nrows)
            ),
        )
        warnings.warn(
            f"Resizing raster from {raster_data.shape[2]}x{raster_data.shape[1]} to {ncols}x{nrows}"
        )
        return o_raster_data, o_raster_profile

    @staticmethod
    def rgb2luminance(raster_data, raster_profile):
        rgb, gray_profile = raster_data, raster_profile.copy()
        if gray_profile["dtype"] == rio.uint8:
            gray = (0.2989 * rgb[0] + 0.5870 * rgb[1] + 0.1140 * rgb[2]).astype(
                np.uint8
            )
        elif gray_profile["dtype"] in [rio.float32, rio.float64]:
            gray = (255 * (0.2989 * rgb[0] + 0.5870 * rgb[1] + 0.1140 * rgb[2])).astype(
                np.uint8
            )
        else:
            raise ValueError("RGB data must be of type uint8 or float32/float64")
        gray_data = gray.reshape(1, *gray.shape)
        gray_profile.update({"count": 1, "dtype": rio.uint8})
        return gray_data, gray_profile

    @staticmethod
    def write(raster_data, raster_profile, ofile):
        with rio.open(ofile, "w", **raster_profile) as dst:
            if raster_data.ndim == 2:
                dst.write(raster_data, 1)
            elif raster_data.ndim == 3:
                # write each band individually
                for band in range(raster_data.shape[0]):
                    # write raster_data, band # (starting from 1)
                    dst.write(raster_data[band, :, :], band + 1)

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from rasterio.plot import show
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        raster_data, raster_profile = RasterLib.rasterize(
            # buildings, dx=1, attr=None, roi=None, ndv=0
            buildings,
            dx=1,
            attr="HAUTEUR",
            roi=None,
            ndv=0,
        )
        # RasterLib.write(raster_data, raster_profile, "/tmp/output.tif")
        memraster = RasterLib.raster_data_profile_2_memory_raster(
            raster_data, raster_profile
        )

        raster_data2, raster_profile2 = RasterLib.fast_rasterize(
            # buildings, dx=1, attr="HAUTEUR", roi=None, ndv=0
            buildings,
            dx=1,
            attr=None,
            roi=None,
            ndv=0,
        )
        memraster2 = RasterLib.raster_data_profile_2_memory_raster(
            raster_data2, raster_profile2
        )

        # PLOTTING
        fig, ax = plt.subplots(figsize=(10, 10))
        with memraster.open() as dataset:
            show(dataset, ax=ax, cmap="Blues_r", alpha=0.8)
        # with memraster2.open() as dataset:
        #     show(dataset, ax=ax, cmap="Greens_r", alpha=0.8)
        buildings.boundary.plot(ax=ax, edgecolor="red")
        buildings.apply(
            lambda x: ax.annotate(
                text=x.HAUTEUR,
                xy=x.geometry.centroid.coords[0],
                color="black",
                size=12,
                ha="left",
            ),
            axis=1,
        )
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    @staticmethod
    def test2():
        from t4gpd.commons.ArrayCoding import ArrayCoding
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STPointsDensifier import STPointsDensifier
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        paths = GeoDataFrameDemos.districtRoyaleInNantesPaths()
        paths = paths.query("gid == 2").reset_index(drop=True)
        sensors = STPointsDensifier(paths, distance=50).run()
        sensors.gid = sensors.node_id.apply(
            lambda t: ArrayCoding.decode(t, outputType=int)[2]
        )
        smaps = STSkyMap25D(
            buildings,
            sensors,
            nRays=64,
            rayLength=100,
            elevationFieldname="HAUTEUR",
            h0=0,
            size=4,
        ).run()
        smaps["raster"] = smaps.apply(
            lambda row: RasterLib.rasterize(
                GeoDataFrame(row.to_frame().T), dx=0.1, attr=None, roi=None, ndv=0
            ),
            axis=1,
        )

        # SERIALIZATION
        # buildings.to_file("/tmp/abc.gpkg", driver="GPKG", layer="buildings")
        # paths.to_file("/tmp/abc.gpkg", driver="GPKG", layer="paths")
        # sensors.to_file("/tmp/abc.gpkg", driver="GPKG", layer="sensors")
        # smaps.drop(columns=["viewpoint", "raster"]).to_file(
        #     "/tmp/abc.gpkg", driver="GPKG", layer="smaps"
        # )
        for _, row in smaps.iterrows():
            raster_data, raster_profile = row["raster"]
            RasterLib.write(raster_data, raster_profile, f"/tmp/output_{row.gid}.tif")

    @staticmethod
    def test3():
        import matplotlib.pyplot as plt
        from geopandas import overlay
        from rasterio.plot import show
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        sensors = FastGridLib.grid(buildings, dx=1, intoPoint=True, withRowsCols=True)
        sensors = overlay(
            sensors,
            buildings[["geometry", "HAUTEUR"]],
            how="intersection",
        )

        raster_data, raster_profile = RasterLib.from_grid_to_raster(
            sensors, "HAUTEUR", rowAttr="row", colAttr="column", roi=None, ndv=0
        )
        memraster = RasterLib.raster_data_profile_2_memory_raster(
            raster_data, raster_profile
        )

        # PLOTTING
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        with memraster.open() as dataset:
            show(dataset, ax=ax, cmap="Blues_r", alpha=0.8)
        buildings.boundary.plot(ax=ax, color="red")
        buildings.apply(
            lambda x: ax.annotate(
                text=x.HAUTEUR,
                xy=x.geometry.centroid.coords[0],
                color="black",
                size=12,
                ha="left",
            ),
            axis=1,
        )
        sensors.plot(ax=ax, column="HAUTEUR", marker=".", legend=True)
        ax.axis("off")
        plt.tight_layout()
        plt.show()
        plt.close(fig)


# RasterLib.test()
# RasterLib.test2()
# RasterLib.test3()
