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
import warnings

from geopandas import GeoDataFrame
from pandas import read_csv
from shapely.geometry import LineString, Point
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.io.AbstractReader import AbstractReader


class UClimTrackWaypointsReader(AbstractReader):
    '''
    classdocs
    '''

    def __init__(self, inputFile, icrs="epsg:4326", ocrs="epsg:2154"):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning_alt
        self.inputFile = inputFile
        self.icrs = icrs
        self.ocrs = ocrs

    def __getVersion(self):
        return 1

    def __postpcs(self, df):
        df["geometry"] = df.apply(lambda row: Point((row.long, row.lat)), axis=1)
        gdf = GeoDataFrame(df, crs=self.icrs).to_crs(self.ocrs)
        assert gdf.ptid.is_monotonic_increasing, "ptid must be monotonic increasing!"

        track_geom = LineString(gdf.geometry.apply(lambda g: g.coords[0:2][0]))
        tracks = GeoDataFrame([{"length": track_geom.length, "geometry": track_geom}], crs=self.ocrs)

        waypoints = gdf.loc[gdf.waypoint == 1 , ["ptid", "geometry"]]
        waypoints.reset_index(drop=True, inplace=True)
        waypoints["curv_absc"] = waypoints.geometry.apply(lambda g: track_geom.project(g, normalized=False))
        waypoints["sect_len"] = waypoints.curv_absc.diff(periods=-1).abs()
        waypoints.rename(columns={"ptid": "id"}, inplace=True)

        return tracks, waypoints

    def __readV1(self):
        df = read_csv(UClimTrackWaypointsReader.opener(self.inputFile), sep=";")
        return self.__postpcs(df)

    def run(self):
        version = self.__getVersion()
        if (1 == version):
            warnings.warn("UClimTrackWaypointsReader (v1)")
            return self.__readV1()
        raise Exception("Unreachable instruction!")

"""
import matplotlib.pyplot as plt

ifile = "/home/tleduc/prj/uclim/data/nantes_commerce_feydeau/nantes_commerce_feydeau_track1.csv"
tracks, waypoints = UClimTrackWaypointsReader(ifile).run()

gdf.to_csv("/tmp/a.csv", index=False, sep=";")
print(gdf.head(3))

ax=waypoints.plot(); tracks.plot(ax=ax); plt.show()
"""
