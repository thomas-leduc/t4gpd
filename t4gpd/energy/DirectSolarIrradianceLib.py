'''
Created on 26 avr. 2022

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
from numpy import dot, sqrt
from numpy.linalg import norm
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.energy.PerrinDeBrichambaut import PerrinDeBrichambaut

import matplotlib.pyplot as plt


class DirectSolarIrradianceLib(object):
    '''
    classdocs

    Irradiance is understood as instantaneous density of solar radiation incident on a given
    surface, typically expressed in W/m2.

    Irradiation is the sum of irradiance over a time period (e.g. 1 hour, day, month, etc.)
    expressed in J/m2. However, in daily routine Wh/m2 are more commonly used.
    '''

    @staticmethod
    def noMaskDI(normal, dt, gdf=LatLonLib.NANTES, model='pysolar', skyType=PerrinDeBrichambaut.STANDARD_SKY):
        '''
        Direct Irradiance (DI in [W/m2]) is the amount of instantaneous solar radiation 
        received per unit area by a surface whose normal is given as an input parameter. 
        '''
        if not isinstance(normal, (list, tuple)) or (len(normal) not in [2, 3]):
            raise IllegalArgumentTypeException(normal, 'list or tuple of X, Y, and Z components')
        if not Epsilon.equals(1.0, norm(normal), 1e-3):
            raise IllegalArgumentTypeException(normal, 'unit vector')

        if not isinstance(dt, datetime):
            raise IllegalArgumentTypeException(dt, 'datetime')
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        normal = (*normal, 0.0) if (2 == len(normal)) else normal
        sunModel = SunLib(gdf=gdf, model=model)
        solarAlti, _ = sunModel.getSolarAnglesInRadians(dt)
        radDir = sunModel.getRadiationDirection(dt)
        
        dotProd = dot(radDir, normal)

        if (0.0 < solarAlti) and (0.0 < dotProd):
            dni = PerrinDeBrichambaut.directNormalIrradiance(solarAlti, skyType=skyType)
            di = dotProd * dni
            return di
        return 0.0

    @staticmethod
    def noMaskDNI(dt, gdf=LatLonLib.NANTES, model='pysolar', skyType=PerrinDeBrichambaut.STANDARD_SKY):
        '''
        Direct Normal Irradiance (DNI in [W/m2]) is the amount of solar radiation received 
        per unit area by a surface that is always held perpendicular (or normal) to the rays
        that come in a straight line from the direction of the sun at its current position in 
        the sky. 
        '''
        if not isinstance(dt, datetime):
            raise IllegalArgumentTypeException(dt, 'datetime')
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        sunModel = SunLib(gdf=gdf, model=model)
        solarAlti, _ = sunModel.getSolarAnglesInRadians(dt)

        if (0.0 < solarAlti):
            return PerrinDeBrichambaut.directNormalIrradiance(solarAlti, skyType=skyType)
        return 0.0

    @staticmethod
    def plot(label, normal, ofile=None):
        magn = 0.5

        lat, _ = LatLonLib.fromGeoDataFrameToLatLon(LatLonLib.NANTES)

        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(3 * magn * 8.26, 1.3 * magn * 8.26))
        fig.suptitle(f'Direct Solar Irradiance, lat={lat:+.1f}°', size=20)
        for i, month in enumerate([3, 6, 12]):
            X, Y, Z = [], [], []
            for hour in range(24):
                for minutes in range(0, 60, 30):
                    dt = datetime(2021, month, 21, hour, minutes)
                    X.append(hour + minutes / 60)
                    Y.append(DirectSolarIrradianceLib.noMaskDI(normal, dt))
                    Z.append(DirectSolarIrradianceLib.noMaskDNI(dt))
            setlocale(LC_ALL, 'en_US.utf8')
            ax[i].set_title(f'{label} - {dt.strftime("%b %d")}st')
            ax[i].plot(X, Y, linestyle='-', color='black', linewidth=1)
            ax[i].plot(X, Z, linestyle=':', color='grey', linewidth=2, label='DNI')
            ax[i].set_xlabel('Hour')
            if (0 == i):
                ax[i].set_ylabel('Instantaneous irradiance [W.m$^{-2}$]')
            ax[i].set_ylim([0, 1000])
            ax[i].legend()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, format='pdf', bbox_inches='tight')
        plt.close(fig)

    @staticmethod
    def plotFelixMarboutin(ofile=None):
        t = 1.0 / sqrt(2.0)
        PAIRS = [
            # ('Roof', (0, 0, 1)),
            ('NE', (t, t, 0)),
            ('N', (0, 1, 0)),
            ('NW', (-t, t, 0)),
            ('W', (-1, 0, 0)),
            ('SW', (-t, -t, 0)),
            ('S', (0, -1, 0)),
            ('SE', (t, -t, 0)),
            ('E', (1, 0, 0)),
            ] 
        magn = 0.5

        lat, _ = LatLonLib.fromGeoDataFrameToLatLon(LatLonLib.NANTES)

        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(3.0 * magn * 8.26, 1.1 * magn * 8.26))
        fig.suptitle(f'''Direct Solar Irradiance, lat={lat:+.1f}°''', size=20)
        MINS = range(0, 60, 15)
        for i, month in enumerate([12, 3, 6]):
            for label, normal in PAIRS:
                X, Y = [], []
                for hour in range(4, 22):
                    for minutes in MINS:
                        dt = datetime(2021, month, 21, hour, minutes)
                        X.append(hour + minutes / 60)
                        Y.append(DirectSolarIrradianceLib.noMaskDI(normal, dt))
                linestyle = '-' if (1 == len(label)) else ':'
                ax[i].plot(X, Y, linestyle=linestyle, linewidth=1.5,
                           label=f'{label} {sum(Y) / (1e3 * len(MINS)):.1f} kWh/m$^2$')

            setlocale(LC_ALL, 'en_US.utf8')
            ax[i].set_title(f'{dt.strftime("%b %d")}st')
            ax[i].set_xlabel('Hour')
            if (0 == i):
                ax[i].set_ylabel('Instantaneous irradiance [W.m$^{-2}$]')
                ax[i].set_xlim([8, 16])
            elif (1 == i):
                ax[i].set_xlim([6, 18])
            elif (1 == 2):
                ax[i].set_xlim([4, 20])
            ax[i].set_ylim([0, 900])
            ax[i].legend(loc='upper left', framealpha=0.5, ncol=2, fontsize=8)

        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, format='pdf', bbox_inches='tight')
        plt.close(fig)

    @staticmethod
    def plotFelixMarboutinAnnuel(ofile=None):
        t = 1.0 / sqrt(2.0)
        PAIRS = [
            # ('Roof', (0, 0, 1)),
            ('NE', (t, t, 0)),
            ('N', (0, 1, 0)),
            ('NW', (-t, t, 0)),
            ('W', (-1, 0, 0)),
            ('SW', (-t, -t, 0)),
            ('S', (0, -1, 0)),
            ('SE', (t, -t, 0)),
            ('E', (1, 0, 0)),
            ] 
        magn = 0.5

        lat, _ = LatLonLib.fromGeoDataFrameToLatLon(LatLonLib.NANTES)

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(2.0 * magn * 8.26, 1.1 * magn * 8.26))
        fig.suptitle(f'''Direct Solar Irradiation, lat={lat:+.1f}°''', size=20)
        MINS = range(0, 60, 30)
        for label, normal in PAIRS:
            X, Y = [], []
            for month in range(1, 13):
                for day in range(1, 28, 10):
                    _Y = []
                    for hour in range(4, 22):
                        for minutes in MINS:
                            dt = datetime(2021, month, day, hour, minutes)
                            _Y.append(DirectSolarIrradianceLib.noMaskDI(normal, dt))

                    dayInYear = dt.timetuple().tm_yday
                    X.append(dayInYear)
                    Y.append(sum(_Y) / (1e3 * len(MINS)))

            linestyle = '-' if (1 == len(label)) else ':'
            ax.plot(X, Y, linestyle=linestyle, linewidth=1.5,
                       label=f'{label} {10 * sum(Y) / 1e3:.2f} MWh/m$^2$')
        ax.set_xlabel('Day of year')
        ax.set_ylabel('Daily irradiation [kWh.m$^{-2}$]')

        for month, label in [(3, 'Spring equinox'), (6, 'Summer solstice'), (9, 'Autumn equinox')]:
            x0 = int(datetime(2021, month, 21).strftime('%j'))
            ax.axvline(x=x0, linestyle=':', color='blue', linewidth=1)
            ax.text(x0 + 5, 0.4, label, fontsize=10, rotation=90, color='blue')

        ax.set_ylim([0, 5.2])
        # ax.grid(color='gray', linestyle=':', linewidth=1)
        ax.legend(loc='upper left', framealpha=0.5, ncol=4, fontsize=8)

        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, format='pdf', bbox_inches='tight')
        plt.close(fig)

    @staticmethod
    def plotAtkinsonAnnuel(ofile=None):
        t = 1.0 / sqrt(2.0)
        PAIRS1 = [
            ('Roof', (0, 0, 1)),
            ('N', (0, 1, 0)),
            ('W', (-1, 0, 0)),
            ('S', (0, -1, 0)),
            ('E', (1, 0, 0)),
            ] 
        PAIRS2 = [
            ('Roof', (0, 0, 1)),
            ('NE', (t, t, 0)),
            ('NW', (-t, t, 0)),
            ('SW', (-t, -t, 0)),
            ('SE', (t, -t, 0)),
            ] 
        magn = 0.5

        lat, _ = LatLonLib.fromGeoDataFrameToLatLon(LatLonLib.NANTES)

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(2.0 * magn * 8.26, 1.1 * magn * 8.26))
        fig.suptitle(f'''Direct Solar Irradiation, lat={lat:+.1f}°''', size=20)
        MINS = range(0, 60, 30)
        for label, pairs in [('Roof+N+E+S+W', PAIRS1), ('Roof+NE+SE+SW+NW', PAIRS2)]:
            X, Y = [], []
            for month in range(1, 13):
                for day in range(1, 28, 10):
                    _Y = {0: [], 1: [], 2: [], 3: [], 4: []}
                    for hour in range(4, 22):
                        for minutes in MINS:
                            for i, (_, normal) in enumerate(pairs):
                                dt = datetime(2021, month, day, hour, minutes)
                                _Y[i].append(DirectSolarIrradianceLib.noMaskDI(normal, dt))

                    dayInYear = dt.timetuple().tm_yday
                    X.append(dayInYear)
                    acc = sum([sum(_Y[i]) for i in range(5)])
                    Y.append(acc / (1e3 * len(MINS)))

            linestyle = '-' if (1 == len(label)) else ':'
            ax.plot(X, Y, linestyle=linestyle, linewidth=1.5,
                       label=f'{label} {10 * sum(Y) / 1e3:.2f} MWh/m$^3$')
        ax.set_xlabel('Day of year')
        ax.set_ylabel('Daily irradiation [kWh]')

        for month, label in [(3, 'Spring equinox'), (6, 'Summer solstice'), (9, 'Autumn equinox')]:
            x0 = int(datetime(2021, month, 21).strftime('%j'))
            ax.axvline(x=x0, linestyle=':', color='blue', linewidth=1)
            ax.text(x0 + 5, 6, label, fontsize=10, rotation=90, color='blue')

        ax.set_ylim([5, 20])
        # ax.grid(color='gray', linestyle=':', linewidth=1)
        ax.legend(loc='upper left', framealpha=0.5, ncol=4, fontsize=8)

        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, format='pdf', bbox_inches='tight')
        plt.close(fig)

'''
DirectSolarIrradianceLib.plot('South orientation', (0, -1, 0), '/tmp/south.pdf')
DirectSolarIrradianceLib.plot('East orientation', (1, 0, 0), '/tmp/east.pdf')
DirectSolarIrradianceLib.plot('West orientation', (-1, 0, 0), '/tmp/west.pdf')
DirectSolarIrradianceLib.plot('Roof', (0, 0, 1), '/tmp/roof.pdf')

DirectSolarIrradianceLib.plotFelixMarboutin('/tmp/felix_marboutin.pdf')
DirectSolarIrradianceLib.plotFelixMarboutinAnnuel('/tmp/felix_marboutin_annuel.pdf')
DirectSolarIrradianceLib.plotAtkinsonAnnuel('/tmp/atkinson_annuel.pdf')
'''
