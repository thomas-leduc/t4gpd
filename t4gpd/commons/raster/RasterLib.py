"""
Created on 30 Sep. 2025

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

import json
import numpy as np
import rasterio as rio
import warnings
from contextlib import closing
from geopandas import GeoDataFrame
from os import path
from os.path import basename
from py7zr import SevenZipFile
from rasterio.features import geometry_mask, rasterize
from rasterio.io import MemoryFile
from rasterio.mask import mask
from rasterio.merge import merge
from rasterio.transform import array_bounds, from_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely import STRtree, box
from shapely.geometry import mapping
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import confusion_matrix, normalized_mutual_info_score
from sklearn.preprocessing import StandardScaler
from tempfile import TemporaryDirectory
from typing import Optional
from zipfile import ZipFile
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
        # features = [json.loads(roi[["geometry"]].to_json())["features"][0]["geometry"]]
        features = [mapping(roi.geometry.iloc[0])]
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
        if (roi is not None) and (not isinstance(roi, GeoDataFrame)):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")
        if (attr is not None) and (attr not in gdf):
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
        if attr is not None:
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
        if (roi is not None) and (not isinstance(roi, GeoDataFrame)):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")
        if (attr is not None) and (attr not in gdf):
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
    def archive_load(iArchive: str, ifile: str) -> tuple:
        """
        Load a raster file from a ZIP or 7z archive.

        Parameters
        ----------
        iArchive : str
            Path to the archive.
        ifile : str
            Filename suffix to search for inside the archive.

        Returns
        -------
        tuple
            (raster_data, raster_profile)

        Raises
        ------
        ValueError
            If the archive format is unsupported or if the target file
            cannot be uniquely identified.
        """

        def __open_archive(iArchive):
            archive_openers = (
                lambda p: ZipFile(p, "r"),
                lambda p: SevenZipFile(p, mode="r"),
            )
            for opener in archive_openers:
                try:
                    return opener(iArchive)
                except Exception:
                    continue
            raise ValueError("Unsupported archive format (ZIP / 7z only).")

        with __open_archive(iArchive) as archive:
            is_zip = isinstance(archive, ZipFile)
            with TemporaryDirectory() as tmp:
                if is_zip:
                    archive.extractall(path=tmp)
                    members = archive.namelist()
                else:
                    archive.extract(path=tmp, targets=archive.getnames())
                    members = archive.getnames()

                candidates = [f for f in members if f.endswith(ifile)]
                if 1 != len(candidates):
                    raise ValueError(
                        f"Expected exactly one matching file for '{ifile}', "
                        f"found {len(candidates)}."
                    )
                candidate = path.join(tmp, candidates[0])
                return RasterLib.load(candidate)
        raise Exception("Unreachable instruction!")

    @staticmethod
    def archive_load_merge(iArchive: str, ifiles: list[str]) -> tuple:
        """
        Load and merge a list of raster files from a ZIP or 7z archive.

        Parameters
        ----------
        iArchive : str
            Path to the archive.
        ifiles : list[str]
            Filenames to extract and merge.

        Returns
        -------
        tuple
            (raster_data, raster_profile)

        Raises
        ------
        ValueError
            If the archive format is unsupported or if no matching files
            are found.
        """

        def __open_archive(iArchive):
            archive_openers = (
                lambda p: ZipFile(p, "r"),
                lambda p: SevenZipFile(p, mode="r"),
            )
            for opener in archive_openers:
                try:
                    return opener(iArchive)
                except Exception:
                    continue
            raise ValueError("Unsupported archive format (ZIP / 7z only).")

        with __open_archive(iArchive) as archive:
            is_zip = isinstance(archive, ZipFile)
            with TemporaryDirectory() as tmp:
                if is_zip:
                    archive.extractall(path=tmp)
                    members = archive.namelist()
                else:
                    archive.extract(path=tmp, targets=archive.getnames())
                    members = archive.getnames()

                candidates = [
                    path.join(tmp, f) for f in members if basename(f) in ifiles
                ]
                if not candidates:
                    raise ValueError("No matching raster files found in archive.")

                with closing(rio.open(f) for f in candidates):
                    srcs = [rio.open(f) for f in candidates]

                    mosaic_data, out_transform = merge(srcs)

                    mosaic_profile = srcs[0].profile.copy()
                    mosaic_profile.update(
                        {
                            "driver": "GTiff",
                            "height": mosaic_data.shape[1],
                            "width": mosaic_data.shape[2],
                            "transform": out_transform,
                        }
                    )

                    for src in srcs:
                        src.close()
                return mosaic_data, mosaic_profile
        raise Exception("Unreachable instruction!")

    @staticmethod
    def bounding_box(raster_data: np.ndarray, raster_profile: dict) -> GeoDataFrame:
        """
        Convert raster bounds to a GeoDataFrame.

        Parameters
        ----------
        raster_data : np.ndarray
            Raster array.
        raster_profile : dict
            Rasterio profile.

        Returns
        -------
        geopandas.GeoDataFrame
            Bounding box polygon as GeoDataFrame.
        """
        xmin, ymin, xmax, ymax = array_bounds(
            raster_profile.get("height"),
            raster_profile.get("width"),
            raster_profile.get("transform"),
        )
        geom = box(xmin, ymin, xmax, ymax)

        return GeoDataFrame(
            geometry=[geom],
            crs=raster_profile.get("crs"),
        )

    @staticmethod
    def calc(
        raster_data_a: np.ndarray,
        raster_profile_a: dict,
        raster_data_b: np.ndarray,
        raster_profile_b: dict,
        expr: callable,
        ndv: float = -9999,
    ) -> tuple:
        """
        Apply a binary raster operation while preserving nodata handling.

        Parameters
        ----------
        raster_data_a : np.ndarray
            First raster array.
        raster_profile_a : dict
            Rasterio profile associated with raster_data_a.
        raster_data_b : np.ndarray
            Second raster array.
        raster_profile_b : dict
            Rasterio profile associated with raster_data_b.
        expr : callable
            Function applied as expr(data_a, data_b).
            e.g.: lambda a, b: (a + b)
        ndv : float, default=-9999.0
            Output nodata value.

        Returns
        -------
        tuple[np.ndarray, dict]
            Output raster and updated raster profile.
        """
        data_a = raster_data_a.astype(np.float64)
        data_b = raster_data_b.astype(np.float64)
        ndv_a = raster_profile_a.get("nodata")
        ndv_b = raster_profile_b.get("nodata")

        mask = np.zeros(data_a.shape, dtype=bool)
        if ndv_a is not None:
            mask |= data_a == ndv_a
        if ndv_b is not None:
            mask |= data_b == ndv_b

        raster_data = expr(data_a, data_b)
        # raster_data[mask] = ndv
        raster_data = np.where(mask, ndv, raster_data)

        raster_profile = raster_profile_a.copy()
        raster_profile.update(dtype=rio.float64, nodata=ndv)
        return raster_data, raster_profile

    @staticmethod
    def fill_in_nodata_values(
        raster_data: np.ndarray,
        raster_profile: dict,
        fill_value: float,
    ) -> tuple[np.ndarray, dict]:
        """
        Replace nodata and NaN values by a given fill value.

        Parameters
        ----------
        raster_data : np.ndarray
            Input raster array.
        raster_profile : dict
            Rasterio profile containing optional 'nodata'.
        fill_value : float
            Value used to replace invalid pixels.

        Returns
        -------
        tuple[np.ndarray, dict]
            Updated raster and profile.
        """
        data = raster_data.astype(np.float64, copy=True)
        nodata = raster_profile.get("nodata")
        mask = np.isnan(data)

        if nodata is not None:
            mask = np.logical_or(mask, data == nodata)

        if mask.any():
            data[mask] = fill_value

        profile = {**raster_profile}
        profile.update(dtype=data.dtype)
        if "nodata" in profile:
            del profile["nodata"]

        return data, profile

    @staticmethod
    def load(ifile: str) -> tuple:
        """
        Load a raster file into a numpy array and get its profile
        :param ifile: input raster file path
        :return: raster_data, raster_profile
        """
        with rio.open(ifile) as src:
            raster_data = src.read()
            raster_profile = src.profile
        return raster_data, raster_profile

    @staticmethod
    def min_max_scaling(raster_data, raster_profile, vmin=None):
        if raster_data.ndim == 3 and 1 != raster_data.shape[0]:
            raise Exception(" A grayscale image was expected, not an RGB image!")

        ndv = raster_profile.get("nodata")
        if ndv is not None:
            mask = raster_data != ndv
        else:
            mask = np.ones_like(raster_data, dtype=bool)

        vmin = raster_data[mask].min() if vmin is None else vmin
        vmax = raster_data[mask].max()
        if vmin >= vmax:
            raise ValueError(f"Invalid scaling range: vmin={vmin}, vmax={vmax}")

        uint8_data = np.zeros_like(raster_data, dtype=np.uint8)
        tmp = (255.0 * (raster_data[mask].astype(np.float32) - vmin)) / (vmax - vmin)
        uint8_data[mask] = np.clip(tmp.round(), 0, 255).astype(np.uint8)

        uint8_profile = raster_profile.copy()
        uint8_profile.update(dtype=rio.uint8)
        return uint8_data, uint8_profile

    @staticmethod
    def raster_data_profile_2_memory_raster(raster_data, raster_profile):
        # Delete all unnecessary size 1 dimensions
        _raster_data = np.squeeze(raster_data)

        # Check shape after the squeeze
        if _raster_data.ndim not in [2, 3]:
            raise ValueError(
                f"raster_data has an unexpected shape after squeeze: {_raster_data.shape}"
            )

        raster = MemoryFile()
        with raster.open(**raster_profile) as dataset:
            if _raster_data.ndim == 2:
                dataset.write(_raster_data, 1)
            else:
                dataset.write(_raster_data)
        return raster

    @staticmethod
    def rasterize(
        gdf: GeoDataFrame,
        dx: float,
        dy: Optional[float] = None,
        roi: Optional[GeoDataFrame] = None,
        attr: Optional[str] = None,
        ndv: float = 0,
    ):
        """
        Rasterize a GeoDataFrame.

        Parameters
        ----------
        gdf:  Source GeoDataFrame.
        dx:   Pixel width  (CRS units).
        dy:   Pixel height (CRS units); defaults to *dx*.
        roi:  Region of interest GeoDataFrame; defaults to *gdf*.
        attr: Attribute column to burn as pixel values; burns 1 if None.
        ndv:  No-data / background value.

        Returns
        -------
        (raster_data, raster_profile)
        """
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if (roi is not None) and (not isinstance(roi, GeoDataFrame)):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")
        if (attr is not None) and (attr not in gdf):
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
    def kmeans_clustering(
        raster_data,
        raster_profile,
        nclusters,
        mode="labels",
        band_index=None,
        seed=None,
    ):
        """
        mode:
            "labels"  arbitrary label
            "mean"    average pixel value for the class
            "median"  median value of the pixels in the class
            "ranked"  sorted by descending average score (0 = highest-scoring class)
        band_index:
            band index to use for calculating stats and sorting (None = average across all bands)
        seed:
            use an int to make the randomness deterministic
        """
        modes = ("labels", "mean", "median", "ranked")
        if mode not in modes:
            raise IllegalArgumentTypeException(mode, f"value from the set {modes}")

        bands, height, width = raster_data.shape
        X = raster_data.reshape(bands, -1).T

        # MASK NODATA VALUES
        nodata = raster_profile.get("nodata")
        mask = np.any(X == nodata, axis=1)
        X_valid = X[~mask]  # original, unnormalized values

        # NORMALIZATION FOR CLUSTERING ONLY
        X_scaled = StandardScaler().fit_transform(X_valid)

        # CLUSTERING
        # kmeans = KMeans(n_clusters=nclusters, random_state=0, n_init="auto", random_state=seed)
        kmeans = MiniBatchKMeans(
            n_clusters=nclusters, batch_size=10000, random_state=seed
        )
        # Add +1: To avoid confusing cluster 0 with pixels for which nodata is 0
        cluster_labels = kmeans.fit_predict(X_scaled) + 1

        # BAND SELECTION FOR SCALAR STATISTICS
        X_stat = (
            X_valid[:, band_index] if band_index is not None else X_valid.mean(axis=1)
        )

        match mode:
            case "labels":
                # BY DEFAULT
                pixel_values = cluster_labels.astype(np.float32)
                out_bands = 1
                out_dtype = rio.uint8

            case "mean":
                # STATISTICS BY CLASS BASED ON ORIGINAL VALUES (MULTI-BAND)
                # Extract pixels from each class using Boolean masks;
                # then apply the average
                class_stats = np.array(
                    [
                        np.mean(X_valid[cluster_labels == k], axis=0)
                        for k in range(1, nclusters + 1)
                    ]
                )
                # Array indexing. Each pixel is assigned the statistical vector
                # for its class, without a loop
                pixel_values = class_stats[cluster_labels - 1]
                out_bands = bands
                out_dtype = rio.float32

            case "median":
                # STATISTICS BY CLASS BASED ON ORIGINAL VALUES (MULTI-BAND)
                # Extract pixels from each class using Boolean masks;
                # then apply the median
                class_stats = np.array(
                    [
                        np.median(X_valid[cluster_labels == k], axis=0)
                        for k in range(1, nclusters + 1)
                    ]
                )
                # Array indexing. Each pixel is assigned the statistical vector
                # for its class, without a loop
                pixel_values = class_stats[cluster_labels - 1]
                out_bands = bands
                out_dtype = rio.float32

            case "ranked":
                # Class-wise scalar average => descending sort => new label
                class_means = np.array(
                    [
                        X_stat[cluster_labels == k].mean()
                        for k in range(1, nclusters + 1)
                    ]
                )
                # rank[k] = position in descending order (1 = highest value)
                rank = np.empty(nclusters, dtype=np.int32)
                rank[np.argsort(class_means)[::-1]] = np.arange(1, nclusters + 1)
                pixel_values = rank[cluster_labels - 1].astype(np.uint8)
                out_bands = 1
                out_dtype = rio.uint8

        # RASTER RECONSTRUCTION
        nodata = nodata if nodata is not None else 0

        if out_bands == 1:
            result = np.full(X.shape[0], nodata, dtype=pixel_values.dtype)
            result[~mask] = pixel_values.ravel()
            classified_data = result.reshape(height, width)[np.newaxis, :]  # (1, H, W)
        else:
            result = np.full(
                (X.shape[0], bands),
                nodata,
                dtype=np.float32,
            )
            result[~mask] = pixel_values
            classified_data = result.T.reshape(bands, height, width)  # (bands, H, W)

        classified_profile = raster_profile.copy()
        classified_profile.update(
            {"count": out_bands, "dtype": out_dtype, "nodata": nodata}
        )

        return classified_data, classified_profile

    @staticmethod
    def quantile_clustering(
        raster_data,
        raster_profile,
        nclusters,
        mode="labels",
        band_index=None,
    ):
        """
        Quantile-based classification.

        mode:
            "labels"  arbitrary label
            "mean"    average pixel value for the class
            "median"  median value of the pixels in the class
            "ranked"  quantiles ranked from highest values (1) to lowest values

        band_index:
            band index used to compute quantiles
            (None = average across all bands)
        """
        modes = ("labels", "mean", "median", "ranked")
        if mode not in modes:
            raise ValueError(f"mode must be one of {modes}")

        bands, height, width = raster_data.shape
        X = raster_data.reshape(bands, -1).T

        # MASK NODATA
        nodata = raster_profile.get("nodata")
        mask = np.any(X == nodata, axis=1)

        X_valid = X[~mask]

        # SCALAR VARIABLE USED FOR QUANTILES
        X_stat = (
            X_valid[:, band_index] if band_index is not None else X_valid.mean(axis=1)
        )

        # QUANTILE THRESHOLDS
        q = np.linspace(0, 100, nclusters + 1)
        thresholds = np.percentile(X_stat, q)

        # Remove possible duplicates caused by ties
        thresholds[0] = -np.inf
        thresholds[-1] = np.inf

        # labels in [1, nclusters]
        cluster_labels = (
            np.digitize(
                X_stat,
                thresholds[1:-1],
                right=False,
            )
            + 1
        )
        counts = np.bincount(cluster_labels, minlength=nclusters)

        match mode:

            case "labels":
                pixel_values = cluster_labels.astype(np.uint8)
                out_bands = 1
                out_dtype = rio.uint8

            case "mean":
                class_stats = np.array(
                    [
                        X_valid[cluster_labels == k].mean(axis=0)
                        for k in range(1, nclusters + 1)
                    ]
                )

                pixel_values = class_stats[cluster_labels - 1]

                out_bands = bands
                out_dtype = rio.float32

            case "median":
                class_stats = np.array(
                    [
                        np.median(X_valid[cluster_labels == k], axis=0)
                        for k in range(1, nclusters + 1)
                    ]
                )

                pixel_values = class_stats[cluster_labels - 1]

                out_bands = bands
                out_dtype = rio.float32

            case "ranked":
                # Highest quantile = rank 1
                pixel_values = (nclusters - cluster_labels + 1).astype(np.uint8)

                out_bands = 1
                out_dtype = rio.uint8

        # RECONSTRUCT RASTER
        nodata = nodata if nodata is not None else 0

        if out_bands == 1:
            result = np.full(
                X.shape[0],
                nodata,
                dtype=pixel_values.dtype,
            )
            result[~mask] = pixel_values.ravel()

            classified_data = result.reshape(height, width)[np.newaxis, :]

        else:
            result = np.full(
                (X.shape[0], bands),
                nodata,
                dtype=np.float32,
            )

            result[~mask] = pixel_values

            classified_data = result.T.reshape(bands, height, width)

        classified_profile = raster_profile.copy()
        classified_profile.update(
            {
                "count": out_bands,
                "dtype": out_dtype,
                "nodata": nodata,
            }
        )

        return classified_data, classified_profile, thresholds, counts[1:]

    @staticmethod
    def iou(
        raster_data1: np.ndarray,
        raster_profile1: dict,
        raster_data2: np.ndarray,
        raster_profile2: dict,
    ) -> dict:
        """
        Compute per-class IoU and mean IoU between two categorical rasters,
        excluding nodata pixels as defined in their respective profiles.

        Parameters
        ----------
        raster_data1 : np.ndarray
            Ground-truth raster array, shape (bands, rows, cols).
        raster_profile1 : dict
            Rasterio profile of raster_data1 (must contain 'nodata' key).
        raster_data2 : np.ndarray
            Predicted raster array, shape (bands, rows, cols).
        raster_profile2 : dict
            Rasterio profile of raster_data2 (must contain 'nodata' key).

        Returns
        -------
        dict with keys:
            'iou_per_class' : dict {class_label: iou_value}
            'miou'          : float
            'n_valid'       : int  — number of pixels used
            'n_masked'      : int  — number of pixels excluded
        """
        # Flatten to 1-D (take band 0 if multi-band)
        y_true = raster_data1[0].flatten()
        y_pred = raster_data2[0].flatten()

        # Extract nodata values from profiles (may be None if absent)
        nd_true = raster_profile1.get("nodata", None)
        nd_pred = raster_profile2.get("nodata", None)

        # Build validity mask — exclude pixels where either raster is nodata
        valid_mask = np.ones(len(y_true), dtype=bool)
        if nd_true is not None:
            valid_mask &= y_true != nd_true
        if nd_pred is not None:
            valid_mask &= y_pred != nd_pred

        n_masked = int((~valid_mask).sum())
        y_true = y_true[valid_mask]
        y_pred = y_pred[valid_mask]

        if len(y_true) == 0:
            raise ValueError("No valid pixels remain after nodata masking.")

        # Compute confusion matrix and derive per-class IoU
        classes = np.unique(np.concatenate([y_true, y_pred]))
        cm = confusion_matrix(y_true, y_pred, labels=classes)

        iou_per_class = {}
        for idx, cls in enumerate(classes):
            tp = cm[idx, idx]
            fp = cm[:, idx].sum() - tp
            fn = cm[idx, :].sum() - tp
            denom = tp + fp + fn
            iou_per_class[cls] = float(tp / denom) if denom > 0 else float("nan")

        miou = float(np.nanmean(list(iou_per_class.values())))

        return {
            "iou_per_class": iou_per_class,
            "miou": miou,
            "n_valid": int(valid_mask.sum()),
            "n_masked": n_masked,
        }

    @staticmethod
    def mask(
        raster_data: np.ndarray,
        raster_profile: dict,
        gdf: GeoDataFrame,
        ndv: float = None,
    ) -> tuple[np.ndarray, dict]:
        """
        Assigns the value `ndv` to the pixels of `raster_data` that fall
        inside the polygon geometries of `gdf`.

        Parameters
        ----------
        raster_data : np.ndarray
            Raster array, shaped (rows, cols) or (bands, rows, cols).
        raster_profile : dict
            Raster metadata (in rasterio format), must contain at least
            'transform', 'crs', 'height', 'width'.
        gdf : GeoDataFrame
            GeoDataFrame containing the polygons defining the areas to mask out.
        ndv : float, optional
            Value to assign to the masked pixels. If None, the value from
            `raster_profile['nodata']` is used.

        Returns
        -------
        tuple[np.ndarray, dict]
            The modified raster (a copy) and the updated profile (with the
            nodata value set if needed).
        """
        profile = raster_profile.copy()

        # Determine which nodata value to use
        if ndv is None:
            ndv = profile.get("nodata")
            if ndv is None:
                raise ValueError(
                    "No `ndv` value provided and no 'nodata' value "
                    "found in raster_profile."
                )

        # If the GeoDataFrame is empty, do nothing
        if gdf.empty:
            return raster_data.copy(), profile

        # Reproject the GeoDataFrame to the raster's CRS if needed
        raster_crs = profile.get("crs")
        if raster_crs is not None and gdf.crs is not None and gdf.crs != raster_crs:
            gdf = gdf.to_crs(raster_crs)

        transform = profile["transform"]
        out_shape = raster_data.shape[-2:]  # (rows, cols), works for both 2D and 3D

        # geometry_mask: by default pixel inside the polygons
        # invert=True flips this behavior => pixel outside the polygons.
        inside_mask = geometry_mask(
            gdf.geometry,
            out_shape=out_shape,
            transform=transform,
            all_touched=True,
            invert=False,
        )

        result = raster_data.copy()

        if result.ndim == 2:
            result[inside_mask] = ndv
        elif result.ndim == 3:
            # (bands, rows, cols): apply the mask to each band
            result[:, inside_mask] = ndv
        else:
            raise ValueError(f"raster_data must be 2D or 3D, got {result.ndim}D.")

        profile["nodata"] = ndv

        return result, profile

    @staticmethod
    def nmi(
        raster_data1: np.ndarray,
        raster_profile1: dict,
        raster_data2: np.ndarray,
        raster_profile2: dict,
        average_method: str = "arithmetic",
    ) -> dict:
        """
        Compute the Normalized Mutual Information (NMI) between two categorical
        rasters, excluding nodata pixels as defined in their respective profiles.

        Parameters
        ----------
        raster_data1 : np.ndarray
            Ground-truth raster array, shape (bands, rows, cols).
        raster_profile1 : dict
            Rasterio profile of raster_data1 (must contain 'nodata' key).
        raster_data2 : np.ndarray
            Predicted raster array, shape (bands, rows, cols).
        raster_profile2 : dict
            Rasterio profile of raster_data2 (must contain 'nodata' key).
        average_method : str, optional
            Averaging method passed to normalized_mutual_info_score.
            One of {'arithmetic', 'geometric', 'min', 'max'}.
            Default is 'arithmetic'.

        Returns
        -------
        dict with keys:
            'nmi'       : float  — Normalized Mutual Information in [0, 1]
            'n_valid'   : int    — number of pixels used
            'n_masked'  : int    — number of pixels excluded
        """
        # Flatten to 1-D (take band 0 if multi-band)
        y_true = raster_data1[0].flatten()
        y_pred = raster_data2[0].flatten()

        # Extract nodata values from profiles (may be None if absent)
        nd_true = raster_profile1.get("nodata", None)
        nd_pred = raster_profile2.get("nodata", None)

        # Build validity mask — exclude pixels where either raster is nodata
        valid_mask = np.ones(len(y_true), dtype=bool)
        if nd_true is not None:
            valid_mask &= y_true != nd_true
        if nd_pred is not None:
            valid_mask &= y_pred != nd_pred

        n_masked = int((~valid_mask).sum())
        y_true = y_true[valid_mask]
        y_pred = y_pred[valid_mask]

        if len(y_true) == 0:
            raise ValueError("No valid pixels remain after nodata masking.")

        nmi_score = normalized_mutual_info_score(
            y_true,
            y_pred,
            average_method=average_method,
        )

        return {
            "nmi": float(nmi_score),
            "n_valid": int(valid_mask.sum()),
            "n_masked": n_masked,
        }

    @staticmethod
    def to_crs(
        raster_data: np.ndarray, raster_profile: dict, dst_crs: str
    ) -> tuple[np.ndarray, dict]:
        """
        Reproject a raster to another CRS.

        Parameters
        ----------
        raster_data : np.ndarray
            Raster array of shape (bands, rows, cols) or (rows, cols).
        raster_profile : dict
            Rasterio profile.
        dst_crs : str
            Destination CRS.

        Returns
        -------
        dst_data : np.ndarray
            Reprojected raster.
        dst_profile : dict
            Updated rasterio profile.
        """
        # Create a virtual raster in memory based on the data and profile
        with RasterLib.raster_data_profile_2_memory_raster(
            raster_data, raster_profile
        ) as memraster:
            with memraster.open() as src:
                # Calculate the transformation and dimensions for the target CRS
                transform, width, height = calculate_default_transform(
                    src.crs,
                    dst_crs,
                    src.width,
                    src.height,
                    *src.bounds,
                )

                # Update the profile for the new CRS
                dst_profile = raster_profile.copy()
                dst_profile.update(
                    crs=dst_crs,
                    transform=transform,
                    width=width,
                    height=height,
                )

                bands = src.count
                dst_shape = (bands, height, width)

                # Create an in-memory raster to store the result
                dst_data = np.empty((src.count, height, width), dtype=src.dtypes[0])

                reproject(
                    source=rio.band(src, list(range(1, src.count + 1))),
                    destination=dst_data,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest,
                )

        return dst_data, dst_profile

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
    def _test():
        from matplotlib import pyplot as plt
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
        # memraster2 = RasterLib.raster_data_profile_2_memory_raster(
        #     raster_data2, raster_profile2
        # )

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
    def _test2():
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
    def _test3():
        from matplotlib import pyplot as plt
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

    @staticmethod
    def _test4():
        from matplotlib import pyplot as plt
        from pandas import cut
        from rasterio.plot import show
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        cut_result, bin_edges = cut(buildings["HAUTEUR"], bins=3, retbins=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        buildings["HAUTEUR"] = cut(
            buildings["HAUTEUR"], bins=bin_edges, labels=bin_centers
        ).astype(float)

        raster_data, raster_profile = RasterLib.rasterize(
            buildings,
            dx=1,
            attr="HAUTEUR",
            roi=None,
            ndv=0,
        )
        memraster = RasterLib.raster_data_profile_2_memory_raster(
            raster_data, raster_profile
        )

        raster_data2, raster_profile2 = RasterLib.min_max_scaling(
            raster_data, raster_profile, vmin=0
        )
        memraster2 = RasterLib.raster_data_profile_2_memory_raster(
            raster_data2, raster_profile2
        )

        # PLOTTING
        fig, axes = plt.subplots(ncols=2, figsize=(12, 6), squeeze=False)

        ax = axes[0, 0]
        with memraster.open() as dataset:
            img = show(dataset, ax=ax, cmap="Blues_r", alpha=0.8)
            cbar = fig.colorbar(img.get_images()[0], ax=ax)
            cbar.set_label("Valeurs des pixels")

        buildings.boundary.plot(ax=ax, edgecolor="red")
        buildings.apply(
            lambda x: ax.annotate(
                text=f"{x.HAUTEUR:.1f}",
                xy=x.geometry.centroid.coords[0],
                color="black",
                size=12,
                ha="left",
            ),
            axis=1,
        )
        ax.axis("off")
        # =====
        ax = axes[0, 1]
        with memraster2.open() as dataset:
            img = show(dataset, ax=ax, cmap="Greens", alpha=0.8, vmin=0, vmax=255)
            cbar = fig.colorbar(img.get_images()[0], ax=ax)
            cbar.set_label("Valeurs des pixels")

        buildings.boundary.plot(ax=ax, edgecolor="red")
        buildings.apply(
            lambda x: ax.annotate(
                text=f"{x.HAUTEUR:.1f}",
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
    def _test5():
        rootdir = "/home/tleduc/prj/anr_lunne_2022-2026/article_1/figshare"
        ifile = f"{rootdir}/output_data/meth1.tif"
        # ifile = f"{rootdir}/input_data/PNL_patrimoine.tif"
        # ifile = f"{rootdir}/input_data/ground_truth.tif"
        rd, rp = RasterLib.load(ifile)
        nclusters = 4
        rd2, rp2 = RasterLib.kmeans_clustering(rd, rp, nclusters, mode="ranked")
        RasterLib.write(rd2, rp2, "./kmeans_meth1_ranked.tif")

    @staticmethod
    def _test6():
        rootdir = "/home/tleduc/prj/anr_lunne_2022-2026/article_1/figshare"
        ifile = f"{rootdir}/output_data/meth1.tif"
        # ifile = f"{rootdir}/input_data/PNL_patrimoine.tif"
        # ifile = f"{rootdir}/input_data/ground_truth.tif"
        rd, rp = RasterLib.load(ifile)
        nclusters = 4
        rd2, rp2, thresholds, counts = RasterLib.quantile_clustering(
            rd, rp, nclusters, mode="ranked"
        )
        RasterLib.write(rd2, rp2, "./quantile_meth1_ranked.tif")
        print(f"{thresholds=}\n{counts=}")

    @staticmethod
    def _test7():
        from matplotlib import pyplot as plt
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

        _buildings = buildings.query("HAUTEUR != 20.6")
        raster_data2, raster_profile2 = RasterLib.mask(
            raster_data, raster_profile, _buildings, ndv=None
        )
        memraster2 = RasterLib.raster_data_profile_2_memory_raster(
            raster_data2, raster_profile2
        )

        # PLOTTING
        fig, axes = plt.subplots(ncols=2, figsize=(12, 6), squeeze=False)

        ax = axes[0, 0]
        with memraster.open() as dataset:
            img = show(dataset, ax=ax, cmap="Reds", alpha=0.8)
            cbar = fig.colorbar(img.get_images()[0], ax=ax)
            cbar.set_label("Valeurs des pixels")

        buildings.boundary.plot(ax=ax, edgecolor="red")
        buildings.apply(
            lambda x: ax.annotate(
                text=f"{x.HAUTEUR:.1f}",
                xy=x.geometry.centroid.coords[0],
                color="black",
                size=12,
                ha="left",
            ),
            axis=1,
        )
        ax.axis("off")
        # =====
        ax = axes[0, 1]
        with memraster2.open() as dataset:
            img = show(dataset, ax=ax, cmap="Reds", alpha=0.8)
            cbar = fig.colorbar(img.get_images()[0], ax=ax)
            cbar.set_label("Valeurs des pixels")

        buildings.boundary.plot(ax=ax, edgecolor="red")
        buildings.apply(
            lambda x: ax.annotate(
                text=f"{x.HAUTEUR:.1f}",
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


# RasterLib._test()
# RasterLib._test2()
# RasterLib._test3()
# RasterLib._test4()
# RasterLib._test5()
# RasterLib._test6()
# RasterLib._test7()
"""
rd1, rp1 = RasterLib.archive_load(
    "/home/tleduc/data/mnt_asc/RGEALTI_2-0_5M_ASC_LAMB93-IGN69_D092_2020-07-30.7z",
    "RGEALTI_FXX_0640_6865_MNT_LAMB93_IGN69.asc",
)

rd2, rp2 = RasterLib.archive_load_merge(
    "/home/tleduc/data/mnt_asc/RGEALTI_2-0_5M_ASC_LAMB93-IGN69_D092_2020-07-30.7z",
    [
        "RGEALTI_FXX_0640_6865_MNT_LAMB93_IGN69.asc",
        "RGEALTI_FXX_0640_6870_MNT_LAMB93_IGN69.asc",
        "RGEALTI_FXX_0645_6865_MNT_LAMB93_IGN69.asc",
        "RGEALTI_FXX_0645_6870_MNT_LAMB93_IGN69.asc",
    ],
)
rp2["crs"] = "epsg:2154"
RasterLib.write(
    rd2,
    rp2,
    ofile="/home/tleduc/prj/anr_resilientgaia_2024-2028/prez-20260629/dev/data/1.tif",
)
"""
