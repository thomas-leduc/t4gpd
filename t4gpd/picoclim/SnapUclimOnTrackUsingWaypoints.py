'''
Created on 8 juin 2023

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
from geopandas import GeoDataFrame
from pandas import DataFrame, Interval, IntervalIndex
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class SnapUclimOnTrackUsingWaypoints(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, dfUclim, dfMob, tracks, waypoints):
        '''
        Constructor
        '''
        if not isinstance(dfUclim, DataFrame):
            raise IllegalArgumentTypeException(dfUclim, "DataFrame")
        for fieldname in ["wp1", "wp2", "timestamps"]:
            if fieldname not in dfUclim:
                raise Exception(f"{fieldname} is not a relevant field name!")
        assert dfUclim.wp1.is_monotonic_increasing, "dfImu.wp1 must be increasing!"
        assert dfUclim.wp1.is_unique, "dfImu.wp1 must be strictly increasing!"
        assert dfUclim.wp2.is_monotonic_increasing, "dfImu.wp2 must be increasing!"
        assert dfUclim.wp2.is_unique, "dfImu.wp2 must be strictly increasing!"
        self.dfUclim = dfUclim

        if not isinstance(dfMob, DataFrame):
            raise IllegalArgumentTypeException(dfMob, "DataFrame")
        self.dfMob = dfMob

        if not isinstance(tracks, GeoDataFrame):
            raise IllegalArgumentTypeException(tracks, "GeoDataFrame")
        self.track_geom = tracks.geometry.squeeze()

        if not isinstance(waypoints, GeoDataFrame):
            raise IllegalArgumentTypeException(waypoints, "GeoDataFrame")
        if "id" not in waypoints:
            raise Exception(f"'id' is not a relevant field name!")
        self.waypoints = waypoints

        assert GeoDataFrameLib.shareTheSameCrs(
            tracks, waypoints), "tracks and waypoints must share the same crs!"
        self.crs = tracks.crs

    def _buildIntervalIndex(self):
        intervals, rows = [], []
        for _, row in self.dfUclim.iterrows():
            wp1, dts = row.wp1, row.timestamps
            for idx2 in range(0, len(dts), 2):
                intervals.append(
                    Interval(left=dts[idx2], right=dts[idx2 + 1], closed="right"))
                rows.append(wp1)
        return DataFrame(data=rows, columns=["wp1"], index=IntervalIndex(intervals))

    def _getWps(self, intervals, dt):
        idx = intervals.index.get_loc(dt)
        row = intervals.iloc[idx]
        return row.wp1

    def run(self):
        intervals = self._buildIntervalIndex()

        def _isInIntervalIndex(intervals, dt): return any(
            intervals.index.contains(dt))

        # SELECTION FROM THE SET OF MEASUREMENTS OF THOSE THAT FALL WITHIN THE INTERVALS
        measures1 = self.dfMob[self.dfMob.timestamp.apply(
            lambda dt: _isInIntervalIndex(intervals, dt))]
        measures1 = measures1[["timestamp"]]
        measures1["wp1"] = measures1.timestamp.apply(
            lambda dt: self._getWps(intervals, dt))
        measures1["inc"] = 1

        measures2 = measures1.groupby(by="wp1").\
            inc.expanding().sum().reset_index(level=[0])
        measures2.inc = measures2.inc.astype(int)
        measures2 = measures2.merge(measures2.groupby(by="wp1").transform("max"),
                                    how="inner", left_index=True, right_index=True)

        # ATTRIBUTE JOIN BETWEEN THE GIVEN TRACK AND ALL WAYPOINTS
        wp = self.dfUclim[["warning", "actual_elapsed_time"]].merge(
            self.waypoints[["id", "curv_absc", "sect_len"]],
            how="left", left_index=True, right_index=True)
        wp["sect_speed"] = wp.apply(
            lambda row: row.sect_len/row.actual_elapsed_time, axis=1)

        # ATTRIBUTE JOIN BETWEEN SELECTED MEASUREMENTS AND ALL WAYPOINTS
        measures2 = measures2.merge(wp[["curv_absc", "sect_len", "actual_elapsed_time", "sect_speed", "warning"]],
                                    how="inner", left_on="wp1", right_index=True)
        measures2.rename(columns={"inc_x": "inc", "inc_y": "total", "curv_absc": "curv_absc0"},
                         inplace=True)

        # DISTRIBUTION OF MEASUREMENTS ON THE POLYLINE ACCORDING TO THEIR CURVILINEAR ABSCISSA VALUE
        measures2["track"] = 1
        measures2["curv_absc"] = measures2.apply(
            lambda row: row.curv_absc0 + (row.inc * row.sect_len) / row.total,
            axis=1)
        measures2["geometry"] = measures2.curv_absc.apply(
            lambda x: self.track_geom.interpolate(x, normalized=False))

        # ADD COLUMNS "ptid" AND "timestamp" TO THE MEASUREMENTS DATAFRAME
        measures3 = measures2[["track", "inc", "curv_absc", "sect_len",
                               "actual_elapsed_time", "sect_speed", "warning", "geometry"]].merge(
            measures1[["timestamp"]], how="inner", left_index=True, right_index=True)
        measures3 = measures3.merge(
            self.waypoints[["id", "curv_absc"]], how="left", on="curv_absc")
        measures3.rename(columns={"id": "ptid"}, inplace=True)

        measures3.at[0, "ptid"] = 1
        measures3 = GeoDataFrame(measures3, crs=self.crs)

        assert measures3.curv_absc.is_monotonic_increasing, "measures3.curv_absc must be increasing!"
        assert measures3.curv_absc.is_unique, "measures3.curv_absc must be strictly increasing!"

        # return intervals, measures1, measures2, measures3
        return measures3


"""
from t4gpd.picoclim.CampbellSciReader import CampbellSciReader
from t4gpd.picoclim.UClimGuidingReader import UClimGuidingReader
from t4gpd.picoclim.UClimTrackWaypointsReader import UClimTrackWaypointsReader

dir1 = "/home/tleduc/prj/uclim/flask/static/uploads/1686227346623113409"
dir2 = "/home/tleduc/prj/uclim/data/nantes_commerce_feydeau"
dfUclim = UClimGuidingReader(f"{dir1}/uclimLOC_nantes_commerce_feydeau_20230607T1228.txt").run()
tracks, waypoints = UClimTrackWaypointsReader(f"{dir2}/nantes_commerce_feydeau_track1.csv").run()
dfMob = CampbellSciReader(f"{dir1}/CR1000XSeries_TwoSec.dat").run() 
# r0, r1, r2, r3 = SnapUclimOnTrackUsingWaypoints(dfUclim, dfMob, tracks, waypoints).run()
r3 = SnapUclimOnTrackUsingWaypoints(dfUclim, dfMob, tracks, waypoints).run()

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
waypoints.plot(ax=ax, marker="P", color="red")
r3.plot(ax=ax, marker="+", color="black")
tracks.plot(ax=ax, color="red", linewidth=0.3)
ax.axis("off")
fig.tight_layout()
plt.show()

waypoints.to_file("/tmp/1.gpkg", layer="waypoints")
tracks.to_file("/tmp/1.gpkg", layer="tracks")
r3.to_file("/tmp/1.gpkg", layer="measures")
"""
