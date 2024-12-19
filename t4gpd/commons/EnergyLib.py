'''
Created on 23 oct. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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


class EnergyLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def fromLongWaveFluxToSurfaceTemperature(lw):
        '''
        Excerpt from https://doi.org/10.1016/j.buildenv.2024.112176

        Surface temperatures are a more efficient index than raw flux 
        values for assessing the radiative specificities of a position
        in the infrared domain. They are derived from long-wave fluxes
        using the equation ST=(LW/(5.670374419*10^(-8)))^(1/4)-273.15.
        '''
        Tsurf = (lw / 5.670374419e-8)**(1/4) - 273.15
        return Tsurf

    @staticmethod
    def plot(ofile=None):
        import matplotlib.pyplot as plt
        from numpy import linspace

        lw = linspace(100, 1100, 100)
        Tsurf = EnergyLib.fromLongWaveFluxToSurfaceTemperature(lw)

        fig, ax = plt.subplots(figsize=(1.4 * 8.26, 1 * 8.26))
        ax.plot(lw, Tsurf)
        ax.set_xlabel("Long-wave flux [W/m$^2$]", fontsize=16)
        ax.set_ylabel("Surface temperature [°C]", fontsize=16)
        ax.grid()
        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)


# EnergyLib.plot()
