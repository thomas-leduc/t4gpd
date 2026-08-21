"""
Created on 4 Nov. 2025

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

from zipfile import ZipFile
from geopandas import GeoDataFrame
from pandas import read_csv
from shapely import LineString, Point
from t4gpd.commons.GeoProcess import GeoProcess


class GTFSReader(GeoProcess):
    """
    classdocs
    """

    def __init__(self, inputFile, dstEpsgCode=None):
        """
        Constructor
        """
        self.inputFile = inputFile
        self.dstEpsgCode = dstEpsgCode

    @staticmethod
    def __read_gtfs(inputFile):
        def __read_archive(archive, fileName):
            if fileName in archive.namelist():
                return read_csv(archive.open(fileName))
            return None

        with ZipFile(inputFile, "r") as archive:
            routes = __read_archive(archive, "routes.txt")
            trips = __read_archive(archive, "trips.txt")
            stops = __read_archive(archive, "stops.txt")
            stop_times = __read_archive(archive, "stop_times.txt")
            shapes = __read_archive(archive, "shapes.txt")

        stop_times = stop_times.merge(
            trips[["trip_id", "route_id"]], on="trip_id", how="left"
        )

        # -------------------------------
        # STEP 1: CREATE LINESTRINGS
        # -------------------------------
        if shapes is not None:
            #  shapes.txt exists => official trajectories

            # Ensure that points are sorted according to sequence
            shapes = shapes.sort_values(["shape_id", "shape_pt_sequence"])

            # Group points with the same shape_id and create LineStrings
            # between successive stops
            lines = shapes.groupby("shape_id")[["shape_pt_lon", "shape_pt_lat"]].apply(
                lambda x: LineString(zip(x.shape_pt_lon, x.shape_pt_lat))
            )
            gdf_lines = GeoDataFrame({"geometry": lines}, crs="EPSG:4326").reset_index()

            # Merge trips + routes + shapes
            gdf_lines = gdf_lines.merge(
                trips[["shape_id", "route_id"]].drop_duplicates(),
                on="shape_id",
                how="left",
            )

        else:
            # No shapes.txt => rebuild by connecting the stops

            # Merge to get line and stop information
            stop_times = stop_times.merge(
                stops[["stop_id", "stop_lat", "stop_lon"]], on="stop_id", how="left"
            )
            #  Sort by trip_id and stop_sequence
            stop_times = stop_times.sort_values(["trip_id", "stop_sequence"])

            # Create LineStrings between successive stops
            lines = stop_times.groupby("trip_id")[["stop_lon", "stop_lat"]].apply(
                lambda x: LineString(zip(x.stop_lon, x.stop_lat))
            )
            gdf_lines = GeoDataFrame({"geometry": lines}, crs="EPSG:4326").reset_index()
            gdf_lines = gdf_lines.merge(
                trips[["trip_id", "route_id"]], on="trip_id", how="left"
            )

        # Add route information
        gdf_lines = gdf_lines.merge(
            routes[["route_id", "route_short_name", "route_long_name"]],
            on="route_id",
            how="left",
        )

        # -------------------------------
        # STEP 2: CREATE POINTS (STATIONS)
        # -------------------------------
        # stop_times => trips => routes
        df = df = stop_times.copy()  # stop_times already contains route_id
        df = df.merge(
            routes[["route_id", "route_short_name", "route_long_name"]],
            on="route_id",
            how="left",
        )
        # aggregation: each station => all serving lines
        agg = (
            df.groupby("stop_id")
            .agg(
                {
                    "route_id": lambda s: sorted(set(s.dropna())),
                    "route_short_name": lambda s: sorted(set(s.dropna())),
                    "route_long_name": lambda s: sorted(set(s.dropna())),
                }
            )
            .reset_index()
        )
        # merging coordinates + geometry
        stops_geom = stops.merge(agg, on="stop_id", how="left")
        stops_geom["geometry"] = stops_geom.apply(
            lambda r: Point(r["stop_lon"], r["stop_lat"]), axis=1
        )
        gdf_stops = GeoDataFrame(stops_geom, geometry="geometry", crs="EPSG:4326")

        return gdf_lines, gdf_stops

    @staticmethod
    def read(inputFile, dstEpsgCode=None):
        gdf_lines, gdf_stops = GTFSReader.__read_gtfs(inputFile)

        nighttime_indices = gdf_lines[
            gdf_lines["route_short_name"].str.startswith("N", na=False)
        ].index
        night = gdf_lines.loc[nighttime_indices]
        day = gdf_lines.drop(index=nighttime_indices)

        if dstEpsgCode:
            gdf_lines = gdf_lines.to_crs(dstEpsgCode)
            day = day.to_crs(dstEpsgCode)
            night = night.to_crs(dstEpsgCode)
            gdf_stops = gdf_stops.to_crs(dstEpsgCode)

        return gdf_lines, day, night, gdf_stops

    def run(self):
        gdf_lines, _ = GTFSReader.__read_gtfs(self.inputFile)
        if self.dstEpsgCode:
            gdf_lines = gdf_lines.to_crs(self.dstEpsgCode)
        return gdf_lines
