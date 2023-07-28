'''
Created on 11 oct. 2022

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
from numpy import isnan, nan
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class SnapImuOnTrackUsingWaypoints(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, dfImu, tracks, waypoints):
        '''
        Constructor
        '''
        if not isinstance(dfImu, GeoDataFrame):
            raise IllegalArgumentTypeException(dfImu, "GeoDataFrame")
        for fieldname in ["timestamp", "TagName"]:
            if fieldname not in dfImu:
                raise Exception(f"{fieldname} is not a relevant field name!")
        assert dfImu.timestamp.is_monotonic_increasing, "dfImu.timestamp must be increasing!"
        assert dfImu.timestamp.is_unique, "dfImu.timestamp must be strictly increasing!"
        self.dfImu = dfImu

        if not isinstance(tracks, GeoDataFrame):
            raise IllegalArgumentTypeException(tracks, "GeoDataFrame")
        if "id" not in tracks:
            raise Exception(f"'id' is not a relevant field name!")
        self.tracks = tracks

        if not isinstance(waypoints, GeoDataFrame):
            raise IllegalArgumentTypeException(waypoints, "GeoDataFrame")
        if "id" not in waypoints:
            raise Exception(f"'id' is not a relevant field name!")
        self.waypoints = waypoints

        assert GeoDataFrameLib.shareTheSameCrs(dfImu, tracks), "dfImu and tracks must share the same crs!"
        assert GeoDataFrameLib.shareTheSameCrs(tracks, waypoints), "tracks and waypoints must share the same crs!"
        self.crs = tracks.crs

    def run(self):
        maxTagNames = self.waypoints.maxTagName.unique()
        imu = self.dfImu.copy(deep=True)
        imu.to_crs(self.crs, inplace=True)

        # ==============================================================
        # 1st STEP: IDENTIFY THE TRACK TO PROJECT ON
        imu["track"], imu["curv_absc"], imu["n_curv_absc"] = None, None, None

        prev, cnt1, rows, cnts = nan, nan, [], []
        for cnt2, (_, row) in enumerate(imu.iterrows()):
            curr = row.TagName
            if isnan(prev):
                prev, cnt1 = (nan, nan) if isnan(curr) else (curr, 0)
                row.track, row.curv_absc = prev, cnt1
                if not isnan(curr):
                    cnts.append(cnt2)

            else:
                if isnan(curr):
                    cnts.append(cnt2)
                    cnt1 += 1
                    row.track, row.curv_absc = prev, cnt1
                else:

                    row.track, row.curv_absc = curr, 0
                    row.n_curv_absc = cnt1 + 1
                    for _cnt in cnts:
                        rows[_cnt].n_curv_absc = cnt1 + 1
                    cnts = []

                    if curr in maxTagNames:
                        prev, cnt1 = nan, nan
                    else:
                        prev, cnt1 = curr, 0

            rows.append(row)
        imu = GeoDataFrame(rows, crs=self.crs)

        # ==============================================================
        # 2nd STEP: ASSESS THE CURVILINEAR ABSCISSA OF THE PROJECTED POINT
        wpDict = self.waypoints.set_index("id").to_dict(orient="index")

        imu.curv_absc = imu.apply(lambda row: None
                                  if isnan(row.track)
                                  else wpDict[row.track]["curv_absc"] + (row.curv_absc * wpDict[row.track]["delta_curv_absc"]) / row.n_curv_absc,
                                  axis=1)
        for tn in maxTagNames:
            imu.loc[ imu[imu.TagName == tn].index, "curv_absc" ] = 1.0

        # ==============================================================
        # 3rd STEP: ASSESS THE COORDINATES OF THE PROJECTED POINT
        trDict = {row.id: row.geometry for _, row in self.tracks.iterrows()}

        imu.track = imu.track.apply(lambda v: v if isnan(v) else int(v // 100))
        imu["snap_geometry"] = imu.apply(lambda row: None
                                         if isnan(row.track)
                                         else trDict[row.track].interpolate(row.curv_absc, normalized=True),
                                         axis=1)
 
        # ==============================================================
        # 4th STEP: ASSESS THE DISTANCE (DRIFT) BETWEEN THE GNSS POINT AND 
        # ITS CORRESPONDING PROJECTED POINT
        imu.rename(columns={"geometry": "gnss_geom", "snap_geometry": "geometry"}, inplace=True)
        imu.drop(columns=["n_curv_absc"], inplace=True)

        imu["drift"] = imu.apply(lambda row: nan 
                                 if ((row.gnss_geom is None) or (row.geometry is None))
                                 else row.gnss_geom.distance(row.geometry),
                                 axis=1)
        imu.gnss_geom = imu.gnss_geom.apply(lambda g: g.wkt)
        imu.set_crs(self.crs, inplace=True)

        imu.drop(index=imu[imu.geometry.isna()].index, inplace=True)
        imu.reset_index(drop=True, inplace=True)

        return imu

'''
import matplotlib.pyplot as plt
from t4gpd.picoclim.MetrologicalCampaignReader import MetrologicalCampaignReader

# dirName = "/home/tleduc/prj/nm-ilots-frais/terrain/220711"
dirName = "/home/tleduc/prj/nm-ilots-frais/terrain/220713"
static, tracks, waypoints, dfImu, dfMob, dfStat1, dfStat2, dfMeteoFr = MetrologicalCampaignReader(dirName).run()
dfImu.to_crs(crs=tracks.crs, inplace=True)

imu = SnapImuOnTrackUsingWaypoints(dfImu, tracks, waypoints).run()

# imu.drop(columns=["timestamp", "X", "Y", "Z", "Distance", "degree", "latitude",
#                   "longitude", "GpsAccuracy", "indoor_outdoor_flag"], inplace=True)
# imu.to_csv("/home/tleduc/prj/nm-ilots-frais/a.csv", index=False)
# imu.to_file("/tmp/imu.gpkg")
imu.plot()
plt.show()

'''
