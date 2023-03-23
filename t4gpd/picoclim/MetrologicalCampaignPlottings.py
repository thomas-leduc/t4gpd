'''
Created on 14 oct. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
from datetime import datetime, timezone
from locale import LC_ALL, setlocale
from os import mkdir
from os.path import isdir

from geopandas import clip, GeoDataFrame
from matplotlib_scalebar.scalebar import ScaleBar
from numpy import isnan
from pandas import DataFrame
from shapely.geometry import box
from t4gpd.comfort.indices.PET import PET
from t4gpd.comfort.indices.UTCI import UTCI
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.misc.STCompass import STCompass
from t4gpd.morph.STSquaredBBox import STSquaredBBox
from t4gpd.sun.STHardShadow import STHardShadow
from t4gpd.sun.STTreeHardShadow import STTreeHardShadow
from t4gpd.sun.STTreeHardShadow2 import STTreeHardShadow2

import matplotlib.pyplot as plt
from t4gpd.commons.DataFrameLib import DataFrameLib


class MetrologicalCampaignPlottings(GeoProcess):
    '''
    classdocs
    '''
    COLORS = ['black', 'blue', 'green']

    def __init__(self, tracks, waypoints, dfImuMob, dfStat1=None, dfStat2=None,
                 dfStat3=None, buildings=None, sidewalks=None, trees=None,
                 dstDir='.', ext='pdf'):
        '''
        Constructor
        '''
        if not isinstance(tracks, GeoDataFrame):
            raise IllegalArgumentTypeException(tracks, 'GeoDataFrame')
        self.tracks = tracks

        if not isinstance(waypoints, GeoDataFrame):
            raise IllegalArgumentTypeException(waypoints, 'GeoDataFrame')
        self.waypoints = waypoints

        if not isinstance(dfImuMob, GeoDataFrame):
            raise IllegalArgumentTypeException(dfImuMob, 'GeoDataFrame')
        self.dfImuMob = dfImuMob

        if not (dfStat1 is None or isinstance(dfStat1, DataFrame)):
            raise IllegalArgumentTypeException(dfStat1, 'DataFrame or None')
        self.dfStat1 = dfStat1

        if not (dfStat2 is None or isinstance(dfStat2, DataFrame)):
            raise IllegalArgumentTypeException(dfStat2, 'DataFrame or None')
        self.dfStat2 = dfStat2

        if not (dfStat3 is None or isinstance(dfStat3, DataFrame)):
            raise IllegalArgumentTypeException(dfStat3, 'DataFrame or None')
        self.dfStat3 = dfStat3

        if not (buildings is None or isinstance(buildings, GeoDataFrame)):
            raise IllegalArgumentTypeException(buildings, 'GeoDataFrame or None')
        self.buildings = buildings

        if not (sidewalks is None or isinstance(sidewalks, GeoDataFrame)):
            raise IllegalArgumentTypeException(sidewalks, 'GeoDataFrame or None')
        self.sidewalks = sidewalks

        if not (trees is None or isinstance(trees, GeoDataFrame)):
            raise IllegalArgumentTypeException(trees, 'GeoDataFrame or None')
        self.trees = trees

        if not isdir(dstDir):
            mkdir(dstDir)
        self.dstDir = dstDir

        if not (ext in ['pdf', 'png']):
            raise IllegalArgumentTypeException(ext, '"pdf" or "png"')
        self.ext = ext

    def __graphicBoard(self, imuMob):
        trackId = int(imuMob.track.tolist()[0])
        tracks = self.tracks[self.tracks.id == trackId].copy(deep=True)
        waypoints = self.waypoints[(self.waypoints.id // 100) == trackId].copy(deep=True)

        t0, t1 = imuMob.timestamp.min(), imuMob.timestamp.max()

        nrows, ncols, magn = 3, 3, 0.5
        fig, axes = plt.subplots(nrows, ncols, squeeze=False,
                                 figsize=(ncols * magn * 8.26, nrows * magn * 8.26))
        setlocale(LC_ALL, 'en_US.UTF8')
        fig.suptitle(f'''Track #{trackId} --- {t0.strftime('%b. %d %Y')}
From {t0.strftime('%X')} to {t1.strftime('%X')}''', size=24)
        # -----
        roi = self.__map(axes, 0, 0, t0, t1, tracks, waypoints)
        self.__subplot(axes, 0, 1, waypoints, imuMob,
                       ['AirTC_Avg', 'Temp_C_Avg(1)', 'Temp_C_Avg(2)'],
                       '$^\circ$C')
        self.__subplot(axes, 0, 2, waypoints, imuMob, ['RH_Avg'], '%', minmax=[15, 85])

        self.__subplot2(axes, 1, 0, roi, t0, t1, self.dfStat1, self.dfStat2, self.dfStat3)
        self.__subplot(axes, 1, 1, waypoints, imuMob, ['SR01Up_3_Avg', 'IR01DnCo_3_Avg'],
                       'W.m$^{_2}$')
        self.__subplot(axes, 1, 2, waypoints, imuMob, ['WS_ms_Avg'], 'm.s$^{-1}$')

        self.__subplot(axes, 2, 0, waypoints, imuMob, ['T_mrt'], '$^\circ$C')
        self.__subplot(axes, 2, 1, waypoints, imuMob, ['PET'], '$^\circ$C',
                       thermalPerceptionRanges=PET.thermalPerceptionRanges)
        self.__subplot(axes, 2, 2, waypoints, imuMob, ['UTCI'], '$^\circ$C',
                       thermalPerceptionRanges=UTCI.thermalPerceptionRanges)
        # -----
        plt.savefig(f'{self.dstDir}/{trackId}_{t0.strftime("%Y%m%d_%H%M")}.{self.ext}', bbox_inches='tight')
        # plt.show()
        plt.close(fig)

    @staticmethod
    def __shadows_1(t0, t1, buildings):
        t0 = datetime(*t0.timetuple()[:6], tzinfo=timezone.utc)
        sob = STHardShadow(buildings, t0, occludersElevationFieldname='HAUTEUR',
                           altitudeOfShadowPlane=0, aggregate=True,
                           tz=timezone.utc, model='pysolar').run()
        return sob

    @staticmethod
    def __shadows_2(t0, t1, trees):
        t0 = datetime(*t0.timetuple()[:6], tzinfo=timezone.utc)
        # sot = STTreeHardShadow(
        #     trees, t0, treeHeightFieldname='h_arbre',
        #     treeCrownRadiusFieldname='r_houppier', altitudeOfShadowPlane=0.0,
        #     aggregate=True, tz=timezone.utc, model='pysolar', npoints=32).run() 
        sot = STTreeHardShadow2(trees, t0, treeHeightFieldname='h_arbre',
            treeCrownHeightFieldname='h_houppier',
            treeUpperCrownRadiusFieldname='up_rad',
            treeLowerCrownRadiusFieldname='down_rad',
            altitudeOfShadowPlane=0.0, aggregate=False, tz=timezone.utc,
            model='pysolar', npoints=32).run() 
        return sot

    def __map(self, axes, nr, nc, t0, t1, tracks, waypoints):
        ax = axes[nr, nc]

        roi = STSquaredBBox(tracks, buffDist=10.0).run()
        minx, miny, maxx, maxy = roi.total_bounds

        if not self.buildings is None:
            # SHADOWS
            buildings = clip(self.buildings, roi)
            sob = MetrologicalCampaignPlottings.__shadows_1(t0, t1, buildings)
            sob.plot(ax=ax, color='lightgrey', linewidth=0, alpha=0.5)

            self.buildings.plot(ax=ax, color='darkgrey', linewidth=0)

        if not self.trees is None:
            # SHADOWS
            trees = clip(self.trees, roi)
            if (0 < len(trees)):
                sot = MetrologicalCampaignPlottings.__shadows_2(t0, t1, trees)
                sot.plot(ax=ax, color='lightgreen', linewidth=0, alpha=0.5)

                self.trees.plot(ax=ax, color='green', marker='.')
            
        if not self.sidewalks is None:
            self.sidewalks.plot(ax=ax, color='lightgrey', linewidth=0.4)

        tracks.plot(ax=ax, color='black', linewidth=0.8)
        waypoints.plot(ax=ax, color='black', marker='+')
        waypoints[waypoints.id % 4 == 0].apply(lambda x: ax.annotate(
            text=x.id, xy=x.geometry.coords[0],
            color='blue', size=10, ha='center'), axis=1);

        scalebar = ScaleBar(dx=1.0, units='m', length_fraction=None, width_fraction=0.015,
                            location='lower left', frameon=True)
        ax.add_artist(scalebar)
        STCompass(ax, roi.total_bounds, tracks.crs).run()
        ax.axis('off')
        ax.axis([minx, maxx, miny, maxy])
        return box(*roi.total_bounds)

    def __subplot(self, axes, nr, nc, waypoints, df, indics, unit,
                  minmax=None, thermalPerceptionRanges=None):
        indics = [indic for indic in indics if indic in df]

        ax = axes[nr, nc]

        if minmax is None:
            # ymin = min([df[indic].min() for indic in indics])
            # ymax = max([df[indic].max() for indic in indics])
            ymin = min([self.dfImuMob[indic].min() for indic in indics])
            ymax = max([self.dfImuMob[indic].max() for indic in indics])
        else:
            ymin, ymax = minmax
        deltaY = ymax - ymin

        if not isnan(deltaY):
            _ymin, _ymax = ymin, ymax
            for i, indic in enumerate(indics):
                ax.plot(100 * df.curv_absc, df[indic], color=self.COLORS[i],
                        label=f'{indic}')

                if not thermalPerceptionRanges is None:
                    tpr = thermalPerceptionRanges()
                    _ymin = min(ymin, tpr['Comfortable']['max'])
                    _ymax = max(ymax, tpr['Comfortable']['min'])
                    for lbl, v in tpr.items():
                        if (_ymin <= v['min'] <= _ymax) or (_ymin <= v['max'] <= _ymax):
                            vMin, vMax = max(v['min'], _ymin), min(v['max'], _ymax)
                            ax.axhspan(vMin, vMax, alpha=0.25, color=v['color'],
                                       linewidth=0, label=lbl)

            ax.vlines(100 * waypoints.curv_absc, _ymin, _ymax, linestyles='dotted',
                      linewidth=0.1, color='grey')
            for gid, x in zip(waypoints.id, 100 * waypoints.curv_absc):
                ax.text(x, _ymax + 0.02 * deltaY, gid, ha='center', va='bottom',
                        rotation='vertical', color='grey', size=8)
            ax.set_ylim(_ymin - 0.2 * deltaY, _ymax + 0.2 * deltaY)

            if (2 == nr):
                ax.set_xlabel('Curvilinear Abscissa [%]', size=8)
            ax.set_ylabel(f'[{unit}]', size=8)
            ax.legend(loc='lower center', ncols=2, prop={'size': 8})

            return False
        return True

    def __subplot2(self, axes, nr, nc, roi, t0, t1, dfStat1, dfStat2, dfStat3):
        ax = axes[nr, nc]
        ymin, ymax = float('inf'), -float('inf')

        if dfStat1 is not None:
            ymin, ymax = min(ymin, dfStat1.Tair.min()), max(ymax, dfStat1.Tair.max())
            df1 = dfStat1[ (t0 <= dfStat1.timestamp) & (dfStat1.timestamp <= t1)].copy(deep=True)
            for label in df1.sensorFamily.unique():
                _df1 = df1[ df1.sensorFamily == label]
                X = _df1.timestamp.apply(lambda t: (t - t0).seconds)
                ax.plot(X, _df1.Tair, label=label, linestyle='-.', color='black')

        if dfStat2 is not None:
            ymin, ymax = min(ymin, dfStat2.Tair.min()), max(ymax, dfStat2.Tair.max())
            df2 = dfStat2[ (t0 <= dfStat2.timestamp) & (dfStat2.timestamp <= t1)].copy(deep=True)
            df2 = df2[ df2.geometry.apply(lambda g: g.within(roi)) ].copy(deep=True)
            for label2a in df2.sensorFamily.unique():
                for label2b in df2.sensorId.unique():
                    _df2 = df2[ (df2.sensorFamily == label2a) & (df2.sensorId == label2b)]
                    X = _df2.timestamp.apply(lambda t: (t - t0).seconds)
                    ax.plot(X, _df2.Tair, label=f'{label2a}-{label2b}', linestyle='-', color='red')

        if dfStat3 is not None:
            df3 = dfStat3[ dfStat3.timestamp.apply(lambda dt: dt.date() == t0.date()) ]
            ymin, ymax = min(ymin, df3.Tair.min()), max(ymax, df3.Tair.max())
            for label in df3.sensorFamily.unique():
                _df3 = df3[ df3.sensorFamily == label ]
                T0 = DataFrameLib.interpolate(_df3, 'timestamp', 'Tair', t0)
                T1 = DataFrameLib.interpolate(_df3, 'timestamp', 'Tair', t1)
                ax.plot([0, (t1 - t0).seconds], [T0, T1], label=label, linestyle=':')

        deltaY = ymax - ymin
        ax.set_ylim(ymin - 0.2 * deltaY, ymax + 0.2 * deltaY)

        ax.set_xlabel('Timestamp [s]', size=8)
        ax.set_ylabel('[$^\circ$C]', size=8)
        ax.legend(loc='lower center', ncols=2, prop={'size': 8})

    def run(self):
        subtracks = self.dfImuMob.subtrack.unique().tolist()
        for subtrack in subtracks:
            df = self.dfImuMob[self.dfImuMob.subtrack == subtrack].copy(deep=True)
            self.__graphicBoard(df)
            # break

'''
from datetime import datetime, timezone
from geopandas import read_file
from os import path

from t4gpd.comfort.indices.TmrtRadiometer import TmrtRadiometer
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.picoclim.JoinByTimeDistance import JoinByTimeDistance
from t4gpd.picoclim.MetrologicalCampaignReader import MetrologicalCampaignReader
from t4gpd.picoclim.SnapImuOnTrackUsingWaypoints import SnapImuOnTrackUsingWaypoints
from t4gpd.sun.STHardShadow import STHardShadow

#~ ======================================================================
if path.exists('c:/Users/tleduc'):
    HOMEDIR = 'c:/Users/tleduc'
elif path.exists('/home/tleduc'):
    HOMEDIR = '/home/tleduc'

BDTDIR = f'{HOMEDIR}/data/bdtopo/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_D044_2021-12-15/\
BDTOPO/1_DONNEES_LIVRAISON_2021-12-00166/BDT_3-0_SHP_LAMB93_D044-ED2021-12-15'

dirName1 = '/home/tleduc/prj/nm-ilots-frais/terrain/220711'
# dirName1 = '/home/tleduc/prj/nm-ilots-frais/terrain/220713'
dirName2 = '/home/tleduc/prj/nm-ilots-frais/information'

#~ -----
static, tracks, waypoints, dfImu, dfMob, dfStat1, dfStat2, dfMeteoFr = \
    MetrologicalCampaignReader(dirName1, dirName2).run()
dfImu = dfImu.to_crs(tracks.crs)
imu = SnapImuOnTrackUsingWaypoints(dfImu, tracks, waypoints).run()
dfImuMob = JoinByTimeDistance(imu, dfMob, left_on='timestamp', right_on='timestamp').run()

op1 = TmrtRadiometer(dfImuMob)
dfImuMob1 = STGeoProcess([op1], dfImuMob).run()

op2 = PET(dfImuMob1, 'AirTC_Avg', 'RH_Avg', 'WS_ms_Avg', 'T_mrt')
op3 = UTCI(dfImuMob1, 'AirTC_Avg', 'RH_Avg', 'WS_ms_Avg', 'T_mrt')
dfImuMob123 = STGeoProcess([op2, op3], dfImuMob1).run()

#~ -----
bigroi = STSquaredBBox(tracks, buffDist=100.0).run()
buildings = read_file(f'{BDTDIR}/BATI/BATIMENT.shp', mask=bigroi)
sidewalks = read_file(f'{HOMEDIR}/data/nantes_metropole/VOIE_LIM_CHAUSSEE_L.shp', mask=bigroi)

#~ -----
# t0 = datetime(2022, 7, 13, 10, 43, 34)
# sob = STHardShadow(buildings, [t0], occludersElevationFieldname='HAUTEUR',
#                    altitudeOfShadowPlane=0, aggregate=True, tz=timezone.utc, model='pysolar').run()

MetrologicalCampaignPlottings(tracks, waypoints, dfImuMob123, dfStat1, dfStat2,
                              dfMeteoFr, buildings, sidewalks, ext='png').run()
'''
