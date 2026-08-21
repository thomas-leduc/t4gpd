"""
Created on 13 May 2025

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

import numpy as np
import rasterio as rio
import warnings
from geopandas import GeoDataFrame
from numpy import asarray, atan2, cos, hypot, linspace, pi, sin
from pandas import Series
from typing import Optional
from t4gpd.commons.raster.RasterLib import RasterLib


class DSMLib(object):
    """
    classdocs
    """

    @staticmethod
    def add_buildings_to_dtm(
        dtm_data: np.ndarray, dtm_profile: dict, buildings: GeoDataFrame, elevation: str
    ) -> tuple[np.ndarray, dict]:
        dx = dtm_profile.get("transform").a
        dy = -dtm_profile.get("transform").e
        ndv = dtm_profile.get("nodata")
        roi = RasterLib.bounding_box(dtm_data, dtm_profile)

        rd, rp = RasterLib.rasterize(
            buildings, dx=dx, dy=dy, roi=roi, attr=elevation, ndv=ndv
        )
        rd, rp = RasterLib.fill_in_nodata_values(rd, rp, 0)

        return RasterLib.calc(
            dtm_data, dtm_profile, rd, rp, expr=lambda a, b: (a + b), ndv=-9999
        )

    @staticmethod
    def __extract_patch(
        dsm_data: np.ndarray,
        dsm_profile: dict,
        x: float,
        y: float,
        radius_m: float,
        nodata_fill: float = 0.0,
    ) -> tuple[Optional[np.ndarray], float]:
        """
        Extract a square DSM patch centered on (x, y) within a given radius.

        Parameters
        ----------
        dsm_data : np.ndarray
            Input DSM array.
        dsm_profile : dict
            Rasterio profile associated with the DSM.
        x, y : float
            Center coordinates in map units.
        radius_m : float
            Patch radius in map units.
        nodata_fill : float, default=0.0
            Value used to fill nodata and out-of-bounds pixels.

        Returns
        -------
        tuple[Optional[np.ndarray], float]
            Extracted patch and pixel size.
        """
        transform = dsm_profile["transform"]
        nodata = dsm_profile.get("nodata")
        pixel_size = abs(transform.a)

        # Support 2D and 3D rasters
        if dsm_data.ndim == 2:
            rows, cols = dsm_data.shape
            raster = dsm_data
        elif dsm_data.ndim == 3:
            _, rows, cols = dsm_data.shape
            raster = dsm_data[0]
        else:
            raise ValueError(f"Unsupported raster dimensions: {dsm_data.shape}")

        try:
            # Center pixel
            row_c, col_c = rio.transform.rowcol(
                transform,
                x,
                y,
            )

            # Radius in pixels
            radius_px = int(np.ceil(radius_m / pixel_size))

            # Window bounds
            row_min = max(0, row_c - radius_px)
            row_max = min(rows, row_c + radius_px + 1)

            col_min = max(0, col_c - radius_px)
            col_max = min(cols, col_c + radius_px + 1)

            patch = raster[
                row_min:row_max,
                col_min:col_max,
            ].astype(np.float64, copy=True)

        except Exception as exc:
            warnings.warn(f"Unable to extract patch around ({x}, {y}): {exc}")
            return None, pixel_size

        # Replace nodata values
        if nodata is not None:
            patch[patch == nodata] = nodata_fill

        # Replace NaN values
        patch[np.isnan(patch)] = nodata_fill

        return patch, pixel_size

    @staticmethod
    def __horizon_elevation_angle(
        dsm_patch: np.ndarray, pixel_size: float, azimuth_rad: float, h0: float
    ) -> float:
        """
        Compute the maximum horizon elevation angle along a given azimuth.

        The function traces a ray from the center of the DSM patch and
        evaluates the elevation angle of each intersected pixel relative
        to the center point. The maximum elevation angle encountered along
        the ray corresponds to the horizon obstruction angle for the
        specified azimuth.

        Parameters
        ----------
        dsm_patch : np.ndarray
            2D DSM patch in meters.
        pixel_size : float
            Pixel size in meters.
        azimuth_rad : float
            Azimuth angle in radians
            (0 = East, counter-clockwise rotation).

        Returns
        -------
        float
            Maximum elevation angle in degrees along the ray.
        """
        rows, cols = dsm_patch.shape

        center_col = cols // 2
        center_row = rows // 2

        # z_center = dsm_patch[center_row, center_col]
        z_observer = dsm_patch[center_row, center_col] + h0

        # Ray direction in image coordinates
        dcol = cos(azimuth_rad)
        drow = -sin(azimuth_rad)

        max_radius = hypot(center_col, center_row)

        max_elevation_angle = 0.0

        step = 1.0
        radius = step

        while radius <= max_radius:
            col = int(round(center_col + dcol * radius))
            row = int(round(center_row + drow * radius))

            # Stop if outside raster bounds
            if col < 0 or col >= cols or row < 0 or row >= rows:
                break

            horizontal_distance = radius * pixel_size

            # dz = dsm_patch[row, col] - z_center
            dz = dsm_patch[row, col] - z_observer

            elevation_angle = atan2(dz, horizontal_distance)

            max_elevation_angle = max(
                max_elevation_angle,
                elevation_angle,
            )

            radius += step

        return max_elevation_angle

    @staticmethod
    def __max_horizon_elevation_angles_from_patch(
        dsm_patch: np.ndarray,
        pixel_size: float,
        n_azimuths: int = 360,
        h0: float = 0,
    ) -> np.ndarray:
        """
        Compute the array of maximum elevation angles at the center pixel of a DSM patch.

        gamma_i is the maximum elevation angle along azimuth i.

        Parameters
        ----------
        dsm_patch : np.ndarray
            2D DSM patch centered on the target location.
        pixel_size : float
            Spatial resolution in meters.
        n_azimuths : int, default=360
            Number of azimuth directions used for angular sampling.

        Returns
        -------
        np.ndarray
            The array of maximum elevation angles in degrees.
        """
        if dsm_patch.size == 0:
            return float("nan")

        azimuths = linspace(0.0, 2 * pi, n_azimuths, endpoint=False)

        return asarray(
            [
                DSMLib.__horizon_elevation_angle(dsm_patch, pixel_size, azimuth, h0)
                for azimuth in azimuths
            ]
        )

    @staticmethod
    def encode25D(
        sensors: GeoDataFrame,
        dsm_data: np.ndarray,
        dsm_profile: dict,
        h0: float,
        raylen: list[float],
        nrays: int,
    ) -> Series:
        if sensors.crs != dsm_profile.get("crs"):
            raise Exception("sensors and DSM must share the same CRS!")
        if not sensors.crs.is_projected:
            raise Exception("sensors and DSM must share the same *projected* CRS!")

        nodata_fill = 0
        results = []
        for _, row in sensors.iterrows():
            geom = row["geometry"].centroid
            x, y = geom.x, geom.y
            patch, px_size = DSMLib.__extract_patch(
                dsm_data, dsm_profile, x, y, raylen, nodata_fill
            )
            if patch is None:
                results.append(None)
                continue
            angles = DSMLib.__max_horizon_elevation_angles_from_patch(
                patch, px_size, nrays, h0
            )
            results.append(angles)
        return results

    @staticmethod
    def elevations_of_points(
        dtm_data: np.ndarray, dtm_profile: dict, pts: GeoDataFrame
    ) -> Series:
        """
        Return the raster elevation at each point.
        Points outside the raster extent receive NaN.
        """
        # Support both 2D and 3D rasters
        raster = dtm_data[0] if dtm_data.ndim == 3 else dtm_data

        xs = pts.geometry.x.to_numpy()
        ys = pts.geometry.y.to_numpy()

        # Convert coordinates to raster indices
        rows, cols = map(
            np.asarray,
            rio.transform.rowcol(
                dtm_profile["transform"],
                xs,
                ys,
            ),
        )

        nrows = dtm_profile["height"]
        ncols = dtm_profile["width"]

        # Non-raster mask (prevents silent IndexErrors or crashes)
        valid = (0 <= rows) & (rows < nrows) & (0 <= cols) & (cols < ncols)

        # Proper initialization with NaN
        elevations = np.full(len(pts), np.nan)
        elevations[valid] = raster[rows[valid], cols[valid]]

        return Series(elevations, index=pts.index, name="altitude")

    @staticmethod
    def pixel_ids(dtm_data: np.ndarray, dtm_profile: dict, pts: GeoDataFrame) -> Series:
        """
        Return the raster pixel ID corresponding to each point.
        Points outside the raster extent receive NaN.
        """
        xs = pts.geometry.x.to_numpy()
        ys = pts.geometry.y.to_numpy()

        # Convert coordinates to raster indices
        rows, cols = map(
            np.asarray,
            rio.transform.rowcol(
                dtm_profile["transform"],
                xs,
                ys,
            ),
        )

        nrows = dtm_profile["height"]
        ncols = dtm_profile["width"]

        # Non-raster mask (prevents silent IndexErrors or crashes)
        valid = (0 <= rows) & (rows < nrows) & (0 <= cols) & (cols < ncols)

        # Proper initialization with NaN
        pixel_ids = np.full(len(pts), np.nan)
        pixel_ids[valid] = rows[valid] * ncols + cols[valid]

        return Series(pixel_ids, index=pts.index, name="pixel_id")

    # def encode25D(dsm_data, dsm_profile, pts, h0, raylen, nrays) -> Series:

    # def distance_to_the_nearest_slope():
    # def aspect_ratio_of_canyons():
    # def skymap():
    # https://grass.osgeo.org/grass-stable/manuals/r.horizon.html
    # def sky_view_factor():

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from rasterio.plot import show
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        roi = STBBox(buildings, buffDist=50).run()
        dtm_data, dtm_profile = RasterLib.archive_load(
            "/home/tleduc/data/mnt_asc/RGEALTI_2-0_5M_ASC_LAMB93-IGN69_D044_2022-12-20.7z",
            "RGEALTI_FXX_0355_6690_MNT_LAMB93_IGN69.asc",
        )
        dtm_data, dtm_profile = RasterLib.clip(dtm_data, dtm_profile, roi=roi)
        memraster = RasterLib.raster_data_profile_2_memory_raster(dtm_data, dtm_profile)

        dsm_data, dsm_profile = DSMLib.add_buildings_to_dtm(
            dtm_data, dtm_profile, buildings, "HAUTEUR"
        )
        memraster2 = RasterLib.raster_data_profile_2_memory_raster(
            dsm_data, dsm_profile
        )

        # PLOTTING
        fig, axes = plt.subplots(ncols=2, figsize=(15, 6), squeeze=False)
        # =====
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
            img = show(dataset, ax=ax, cmap="Greens", alpha=0.8)
            cbar = fig.colorbar(img.get_images()[0], ax=ax)
            cbar.set_label("Valeurs des pixels")
        buildings.boundary.plot(ax=ax, edgecolor="red")
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)

    @staticmethod
    def test2():
        import matplotlib.pyplot as plt
        from rasterio.plot import show
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
        from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        sensors = FastGridLib.grid(buildings, dx=10, dy=None, intoPoint=True)
        sensors = PointsInPolygonsLib.outdoors(sensors, buildings)
        # buildings.to_file("/tmp/123.gpkg", layer="buildings")  # DEBUG
        # sensors.to_file("/tmp/123.gpkg", layer="sensors")  # DEBUG
        sensors = sensors.query("gid in (36, 67, 206, 217, 307)")

        # ===== VECTOR =====
        h0 = 1.1
        raylen, nrays = 100, 180
        proj, size = "Stereographic", 30
        osensors_v = SensorBasedEncodingLib.encode25D(
            sensors, buildings, "HAUTEUR", h0, raylen, nrays
        )
        smaps_v = SkymapBuilder.build(
            osensors_v, "angles", proj=proj, size=size, epsilon=0.2
        )

        # ===== RASTER =====
        roi = STBBox(buildings, buffDist=50).run()
        dtm_data, dtm_profile = RasterLib.archive_load(
            "/home/tleduc/data/mnt_asc/RGEALTI_2-0_5M_ASC_LAMB93-IGN69_D044_2022-12-20.7z",
            "RGEALTI_FXX_0355_6690_MNT_LAMB93_IGN69.asc",
        )
        dtm_profile["crs"] = "epsg:2154"
        dtm_data, dtm_profile = RasterLib.clip(dtm_data, dtm_profile, roi=roi)
        dsm_data, dsm_profile = DSMLib.add_buildings_to_dtm(
            dtm_data, dtm_profile, buildings, "HAUTEUR"
        )

        dsm_profile["crs"] = "epsg:2154"
        RasterLib.write(dsm_data, dsm_profile, ofile="/tmp/dsm.tif")  # DEBUG

        X = DSMLib.encode25D(sensors, dsm_data, dsm_profile, h0, raylen, nrays)
        osensors_r = sensors.copy(deep=True)
        osensors_r["angles"] = X

        # osensors_v[["gid", "angles"]].to_csv("/tmp/vect.csv", index=False)
        # osensors_r[["gid", "angles"]].to_csv("/tmp/rast.csv", index=False)

        smaps_r = SkymapBuilder.build(
            osensors_r, "angles", proj=proj, size=size, epsilon=0.2
        )

        memraster = RasterLib.raster_data_profile_2_memory_raster(dsm_data, dsm_profile)

        minx, miny, maxx, maxy = roi.total_bounds
        minx, miny, maxx, maxy = smaps_v.total_bounds
        # ==============================
        # PLOTTING
        fig, axes = plt.subplots(ncols=2, figsize=(15, 6), squeeze=False)
        # =====
        ax = axes[0, 0]
        # roi.boundary.plot(ax=ax, color="red", linewidth=0.1)
        sensors.plot(ax=ax, marker="+", color="red")
        sensors.apply(
            lambda x: ax.annotate(
                text=x.gid,
                xy=x.geometry.coords[0],
                color="red",
                size=10,
                ha="center",
                va="top",
            ),
            axis=1,
        )
        buildings.plot(
            ax=ax,
            column="HAUTEUR",
            edgecolor="blue",
            alpha=0.5,
            cmap="Grays",
            legend=True,
        )
        smaps_v.plot(ax=ax, color="black")
        ax.axis("off")
        ax.axis([minx, maxx, miny, maxy])
        # =====
        ax = axes[0, 1]
        sensors.plot(ax=ax, marker="+", color="red")
        buildings.boundary.plot(ax=ax, edgecolor="blue", linewidth=0.4)
        with memraster.open() as dataset:
            img = show(dataset, ax=ax, cmap="Grays", alpha=0.4)
            cbar = fig.colorbar(img.get_images()[0], ax=ax)
            cbar.set_label("Elevation [m]")
        smaps_r.plot(ax=ax, color="black")
        ax.axis("off")
        ax.axis([minx, maxx, miny, maxy])

        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return osensors_v, osensors_r


# DSMLib.test()
# encv, encr = DSMLib.test2()
