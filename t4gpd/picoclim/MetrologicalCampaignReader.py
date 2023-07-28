'''
Created on 15 sept. 2022

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
from glob import glob
from os.path import basename, exists
from sys import stderr
import warnings

from geopandas import GeoDataFrame
from pandas import concat
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.picoclim.CampbellSciReader import CampbellSciReader
from t4gpd.picoclim.ExtraProcessing import ExtraProcessing
from t4gpd.picoclim.InertialMeasureReader import InertialMeasureReader
from t4gpd.picoclim.JoinByTimeDistance import JoinByTimeDistance
from t4gpd.picoclim.KestrelReader import KestrelReader
from t4gpd.picoclim.MeteoFranceReader import MeteoFranceReader
from t4gpd.picoclim.SensirionReader import SensirionReader
from t4gpd.picoclim.SnapImuOnTrackUsingWaypoints import SnapImuOnTrackUsingWaypoints
from t4gpd.picoclim.SnapUclimOnTrackUsingWaypoints import SnapUclimOnTrackUsingWaypoints
from t4gpd.picoclim.TracksWaypointsReader import TracksWaypointsReader
from t4gpd.picoclim.UClimGuidingReader import UClimGuidingReader
from t4gpd.picoclim.UClimTrackWaypointsReader import UClimTrackWaypointsReader


class MetrologicalCampaignReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, dirName, dirMeteoFr=None, dirUclimTrack=None):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning_alt

        if not exists(dirName):
            raise IllegalArgumentTypeException(dirName, "valid directory name")
        self.dirName = dirName

        if not ((dirMeteoFr is None) or exists(dirMeteoFr)):
            raise IllegalArgumentTypeException(
                dirMeteoFr, "valid directory name")
        self.dirMeteoFr = dirMeteoFr

        if not ((dirUclimTrack is None) or exists(dirUclimTrack)):
            raise IllegalArgumentTypeException(
                dirUclimTrack, "valid directory name")
        self.dirUclimTrack = dirUclimTrack

        self.performance = None, None, None, None, None, None

    def getVersion(self):
        uclimLOC = glob(f"{self.dirName}/uclimLOC_*_[0-9]*T[0-9]*.txt")
        if (0 == len(uclimLOC)):
            # OLD LOCATION SYSTEM BASED ON INERTIAL SENSOR
            return 1
        elif (1 == len(uclimLOC)):
            # NEW LOCATION SYSTEM BASED ON UCLIM GUIDING SOLUTION
            return 2
        raise NotImplementedError(
            f'\n\n\t*** MetrologicalCampaignReader:: unknown format version! ***')

    def getPerformance(self):
        return self.performance

    def __loader(self, filenameFilter, Reader):
        dfs = []
        for filename in glob(filenameFilter):
            print(f"*** {basename(filename)}", file=stderr)
            df = Reader(filename).run()
            dfs.append(df)
        return None if (0 == len(dfs)) else concat(dfs, ignore_index=True)

    def __readSig(self):
        filename = f"{self.dirName}/sig.gpkg"
        print(f"*** {basename(filename)}", file=stderr)
        dfStatic, tracks, waypoints = TracksWaypointsReader(filename).run()
        return dfStatic, tracks, waypoints

    def __readUclimGuiding(self):
        filenameFilter = f"{self.dirName}/uclimLOC_*_[0-9]*T[0-9]*.txt"
        # dfUclim = self.__loader(filenameFilter, UClimGuidingReader)
        reader = UClimGuidingReader(glob(filenameFilter)[0])
        dfUclim = reader.run()
        dt0, dt1, deltaTotal, deltaActual, performance = reader.getPerformance()

        trackid = dfUclim.track_id.unique().astype(int)
        if (1 != len(trackid)):
            raise Exception(
                "There must be exactly one and only one track in the uclimLOC file!")
        trackid = trackid[0]

        if self.dirUclimTrack is None:
            raise Exception("dirUclimTrack must not be None!")

        uclimTrack = glob(f"{self.dirUclimTrack}/*_track{trackid}.csv")
        if (1 == len(uclimTrack)):
            tracks, waypoints = UClimTrackWaypointsReader(uclimTrack[0]).run()
        else:
            raise Exception(
                f"There's no file: {self.dirUclimTrack}/*_track{trackid}.csv")

        self.performance = dt0, dt1, deltaTotal, deltaActual, \
            tracks.geometry.squeeze().length / deltaActual, performance
        return dfUclim, tracks, waypoints

    def __readImu(self):
        filenameFilter = f"{self.dirName}/LOG_FILE_????????_*.txt"
        dfImu = self.__loader(filenameFilter, InertialMeasureReader)
        if dfImu is not None:
            dfImu.sort_values(by="timestamp", inplace=True, ignore_index=True)
        return dfImu

    def __readMob(self):
        filenameFilter = f"{self.dirName}/CR1000XSeries_TwoSec.dat"
        dfMob = self.__loader(filenameFilter, CampbellSciReader)
        if dfMob is not None:
            dfMob.sort_values(by="timestamp", inplace=True, ignore_index=True)
        return dfMob

    def __readOther(self, dfStatic=None):
        filenameFilter = f"{self.dirName}/*HEAT*.csv"
        dfStat1 = self.__loader(filenameFilter, KestrelReader)
        if dfStat1 is not None:
            dfStat1.sort_values(
                by="timestamp", inplace=True, ignore_index=True)

        filenameFilter = f"{self.dirName}/Sensirion_*.edf"
        dfStat2 = self.__loader(filenameFilter, SensirionReader)
        if dfStat2 is not None:
            dfStat2.sort_values(
                by="timestamp", inplace=True, ignore_index=True)
            if dfStatic is not None:
                dfStat2 = dfStat2.merge(dfStatic, on="station")
                dfStat2 = GeoDataFrame(dfStat2, crs=dfStatic.crs)

        filenameFilter = f"{self.dirMeteoFr}/meteo-france-*.txt"
        dfMeteoFr = self.__loader(filenameFilter, MeteoFranceReader)
        if dfMeteoFr is not None:
            dfMeteoFr.sort_values(
                by="timestamp", inplace=True, ignore_index=True)

        return dfStat1, dfStat2, dfMeteoFr

    def __readV1(self):
        warnings.warn("MetrologicalCampaignReader (v1)")

        dfImu = self.__readImu()
        dfMob = self.__readMob()
        dfStatic, tracks, waypoints = self.__readSig()

        if dfImu is None:
            raise Exception("dfImu must not be None!")
        dfImu = dfImu.to_crs(tracks.crs)
        dfImu = SnapImuOnTrackUsingWaypoints(dfImu, tracks, waypoints).run()
        dfImuMob = JoinByTimeDistance(
            dfImu, dfMob, left_on="timestamp", right_on="timestamp").run()
        dfImuMob = ExtraProcessing(dfImuMob, inplace=False).run()

        dfStat1, dfStat2, dfMeteoFr = self.__readOther(dfStatic)

        return dfStatic, tracks, waypoints, dfImuMob, dfMob, dfStat1, dfStat2, dfMeteoFr

    def __readV2(self):
        warnings.warn("MetrologicalCampaignReader (v2)")

        dfMob = self.__readMob()

        dfUclim, tracks, waypoints = self.__readUclimGuiding()
        dfUclim = SnapUclimOnTrackUsingWaypoints(
            dfUclim, dfMob, tracks, waypoints).run()

        dfUclimMob = dfUclim.merge(dfMob, how="inner", on="timestamp")
        dfUclimMob = ExtraProcessing(dfUclimMob, inplace=False).run()

        dfStat1, dfStat2, dfMeteoFr = self.__readOther()

        return None, tracks, waypoints, dfUclimMob, dfMob, dfStat1, dfStat2, dfMeteoFr

    def run(self):
        version = self.getVersion()

        if (1 == version):
            return self.__readV1()
        elif (2 == version):
            return self.__readV2()

        raise Exception("Unreachable instruction!")


'''
version = 2
if (1 == version):
    dirName1 = "/home/tleduc/prj/nm-ilots-frais/terrain/220711"
    # dirName1 = "/home/tleduc/prj/nm-ilots-frais/terrain/220713"
    dirName2 = "/home/tleduc/prj/nm-ilots-frais/information"

    dfStatic, tracks, waypoints, dfImuMob, dfMob, dfStat1, dfStat2, dfMeteoFr = \
        MetrologicalCampaignReader(dirName1, dirMeteoFr=dirName2).run()
else:
    dirName1 = "/home/tleduc/prj/uclim/data/nantes_commerce_feydeau/nantes_commerce_feydeau_20230607_track1_093626/raw_data"
    dirName2 = None
    dirName3 = "/home/tleduc/prj/uclim/data/nantes_commerce_feydeau"

    mcr = MetrologicalCampaignReader(dirName1, dirMeteoFr=dirName2, dirUclimTrack=dirName3)
    _, tracks, waypoints, dfUclimMob, dfMob, dfStat1, dfStat2, dfMeteoFr = mcr.run()
    print(mcr.getPerformance())
'''
