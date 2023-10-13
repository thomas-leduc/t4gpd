'''
Created on 4 mars 2022

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
from io import StringIO
from re import sub

import matplotlib.pyplot as plt
from numpy import float64, linspace, ndarray, vectorize
from pandas import DataFrame, read_csv
from scipy.stats import norm
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class AbstractEnergyDemand(object):
    '''
    classdocs
    '''

    def __init__(self, D=None, S=None, E=None):
        '''
        Constructor
        '''
        if D is None:
            _D = self._getDevicesPerAgeGroup()
            self.D = _D.drop(columns=['device']).to_numpy(dtype=float64)
            # self.D = _D.drop(columns=['device']).to_numpy(dtype=str)
        elif isinstance(D, ndarray):
            self.D = D
        elif isinstance(D, DataFrame):
            self.D = D.to_numpy()
        else:
            raise IllegalArgumentTypeException(D, 'numpy.ndarray or pandas.DataFrame')

        if S is None:
            _S = self._getNormalScenario()
            self.S = _S.drop(columns=['Age group']).to_numpy(dtype=str)
        elif isinstance(S, ndarray):
            self.S = S
        elif isinstance(S, DataFrame):
            self.S = S.to_numpy()
        else:
            raise IllegalArgumentTypeException(S, 'numpy.ndarray or pandas.DataFrame')

        if E is None:
            _E = self._getDeviceEnergyConsumption()
            self.E = _E.drop(columns=['device', 'comment']).to_numpy(dtype=str)
        elif isinstance(E, ndarray):
            self.E = E
        elif isinstance(E, DataFrame):
            self.E = E.to_numpy()
        else:
            raise IllegalArgumentTypeException(E, 'numpy.ndarray or pandas.DataFrame')

        # CHECK DIMENSIONS
        n, m = self.D.shape

        if not (((1 == self.S.ndim) and (m == self.S.shape[0])) or
                ((2 == self.S.ndim) and (m == self.S.shape[0]) and  (1 == self.S.shape[1]))):
            raise IllegalArgumentTypeException(self.S, f'1D numpy.ndarray or 2D numpy.ndarray (m={m} rows x 1 col.)')

        if not (((1 == self.E.ndim) and (n == self.E.shape[0])) or
                ((2 == self.E.ndim) and (n == self.E.shape[0]) and  (1 == self.E.shape[1]))):
            raise IllegalArgumentTypeException(self.S, f'1D numpy.ndarray or 2D numpy.ndarray (n={3} rows x 1 col.)')

        self.S = self.S.reshape(-1)
        self.E = self.E.reshape(-1)

    @staticmethod
    def _getDevicesPerAgeGroup():
        _sio = StringIO("""device;Men;Ind_11_17;Ind_18_24;Ind_25_39;Ind_40_54;Ind_55_64;Ind_65_79;Ind_80p
gateway;95.0;0.0;0.0;0.0;0.0;0.0;0.0;0.0
laptop;0.0;91.0;82.0;73.0;83.0;76.0;58.0;0.0
tablet;0.0;37.0;36.0;49.0;45.0;47.0;29.0;0.0
smartphone;0.0;86.0;98.0;95.0;80.0;62.0;44.0;0.0
smart object;0.0;31.0;25.0;21.0;17.0;9.0;5.0;0.0
smart speaker;0.0;15.0;14.0;1.0;9.0;7.0;5.0;0.0
tv;0;0;79.2;93.1;95.3;97.9;97.9;0.0
""")
        return read_csv(_sio, sep=';')

    @staticmethod
    def _getDeviceEnergyConsumption():
        _sio = StringIO("""device;Wh;comment
gateway;26.0;150 kWh/an < box < 300 kWh/an
laptop;75.0;50 Wh < laptop < 100 Wh
tablet;4.0;2 Wh < tablet < 6 Wh
smartphone;10*delta(h-19);Once a day
smart object;1.0;
smart speaker;5.0;
tv;100.0;40 Wh (Oled) < TV < 250 Wh (Plasma)
""")
        return read_csv(_sio, sep=';')

    @staticmethod
    def _getNormalScenario():
        '''
        _sio = StringIO("""Age group;IT equipment usage rate
Men;100
Ind_11_17;rect(0,5,w) * (rect(12,14,h) * 20 + rect(18,20,h) * 70 + rect(20,23,h) * 50) + rect(5,7,w) * (rect(8,13,h) * 90 + rect(18,20,h) * 70 + rect(20,22,h) * 90)
Ind_18_24;rect(0,5,w) * (rect(19,21,h) * 70 + rect(21,24,h) * 60) + rect(5,7,w) * (rect(10,15,h) * 50 + rect(21,24,h) * 70)
Ind_25_39;rect(0,5,w) * (rect(9,12,h) * 20 + rect(12,14,h) * 30 + rect(19,21,h) * 60 + rect(21,24,h) * 70) + rect(5,7,w) * (rect(10,15,h) * 90 + rect(18,24,h) * 90)
Ind_40_54;rect(0,5,w) * (rect(9,12,h) * 30 + rect(12,14,h) * 35 + rect(19,21,h) * 80 + rect(21,23,h) * 70) + rect(5,7,w) * (rect(8,10,h) * 50 + rect(12,14,h) * 60 + rect(18,22,h) * 70)
Ind_55_64;rect(0,5,w) * (rect(9,12,h) * 40 + rect(12,14,h) * 35 + rect(19,21,h) * 80) + rect(5,7,w) * (rect(7,9,h) * 90 + rect(12,14,h) * 60 + rect(18,22,h) * 70)
Ind_65_79;rect(7,9,h) * 20 + rect(9,12,h) * 40 + rect(12,15,h) * 90 + rect(15,17,h) * 50 + rect(17,22,h) * 70
Ind_80p;rect(9,13,h) * 60 + rect(14,22,h) * 40
""")
        '''
        _sio = StringIO("""Age group;IT equipment usage rate
Men;100
Ind_11_17;rect(0,5,w) * (rect(12,14,h) * snd(20) + rect(18,20,h) * snd(70) + rect(20,23,h) * snd(50)) + rect(5,7,w) * (rect(8,13,h) * snd(90) + rect(18,20,h) * snd(70) + rect(20,22,h) * snd(90))
Ind_18_24;rect(0,5,w) * (rect(19,21,h) * snd(70) + rect(21,24,h) * snd(60)) + rect(5,7,w) * (rect(10,15,h) * snd(50) + rect(21,24,h) * snd(70))
Ind_25_39;rect(0,5,w) * (rect(9,12,h) * snd(20) + rect(12,14,h) * snd(30) + rect(19,21,h) * snd(60) + rect(21,24,h) * snd(70)) + rect(5,7,w) * (rect(10,15,h) * snd(90) + rect(18,24,h) * snd(90))
Ind_40_54;rect(0,5,w) * (rect(9,12,h) * snd(30) + rect(12,14,h) * snd(35) + rect(19,21,h) * snd(80) + rect(21,23,h) * snd(70)) + rect(5,7,w) * (rect(8,10,h) * snd(50) + rect(12,14,h) * snd(60) + rect(18,22,h) * snd(70))
Ind_55_64;rect(0,5,w) * (rect(9,12,h) * snd(40) + rect(12,14,h) * snd(35) + rect(19,21,h) * snd(80)) + rect(5,7,w) * (rect(7,9,h) * snd(90) + rect(12,14,h) * snd(60) + rect(18,22,h) * snd(70))
Ind_65_79;rect(7,9,h) * snd(20) + rect(9,12,h) * snd(40) + rect(12,15,h) * snd(90) + rect(15,17,h) * snd(50) + rect(17,22,h) * snd(70)
Ind_80p;rect(9,13,h) * snd(60) + rect(14,22,h) * snd(40)
""")
        return read_csv(_sio, sep=';')

    @staticmethod
    def _unitImpulse(x):
        return 1 if (0 == x) else 0

    @staticmethod
    def _indicatorFunction(x0, x1, x):
        return 1 if (x0 <= x < x1) else 0

    @staticmethod
    def _randomVariates(mu, std=None):
        if std is None:
            std = 0.1 * mu
        return norm(mu, std).rvs()

    def __eval(self, ch):
        h, w = self.h, self.w
        rect = lambda t0, t1, t: self._indicatorFunction(t0, t1, t)
        snd = lambda x: x
        return eval(ch) if isinstance(ch, str) else ch 

    def plotScenario(self, ofile=None):
        _eval_vector = vectorize(self.__eval)

        AGE_GROUPS = ['Men.', '11_17', '18-24', '25-39', '40-54', '55-64', '65-79', '80+']
        COLORS = ['darkgrey', 'dimgrey', 'black']
        STYLES = ['solid', 'dashed', 'dashdot', 'dotted']
        MARKERS = ['+', 'h', 'D', '', 'o', '>']
        WIDTH = [2, 3]
        H = range(24)

        for day_label, self.w in [('weekday', 0), ('weekend', 5)]:
            rows = []
            for self.h in H:
                rows.append(_eval_vector(self.S))
            df = DataFrame(rows, columns=AGE_GROUPS)
            df['H'] = H

            fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
            # ax.set_title(day_label, size=24)

            for i, ageGroup in enumerate(AGE_GROUPS[1:]):
                ax.scatter(H, df[ageGroup], color=COLORS[i % 3], marker=MARKERS[i % len(MARKERS)])
                ax.plot(H, df[ageGroup], color=COLORS[i % 3],
                        linestyle=STYLES[i % 4], linewidth=WIDTH[i % 2])
                ax.plot([], [], color=COLORS[i % 3], marker=MARKERS[i % len(MARKERS)],
                        linestyle=STYLES[i % 4], linewidth=WIDTH[i % 2], label=ageGroup)

            ax.tick_params(axis='both', which='major', labelsize=16)
            ax.tick_params(axis='both', which='minor', labelsize=10)
            ax.set_ylim(0, 100)
            ax.set_xlabel('Hour', size=20)
            ax.set_ylabel('IT equipment usage ratios (in %)', size=20)
            ax.legend(prop={'size': 20})

            if ofile is None:
                plt.show()
            else:
                plt.savefig(f'{day_label}.pdf', bbox_inches='tight')
            plt.close(fig)

    @staticmethod
    def to_latex():
        _COLUMNS = {'Men': 'household', 'Ind_11_17': '11-17', 'Ind_18_24': '18-24', 'Ind_25_39': '25-39',
                   'Ind_40_54': '40-54', 'Ind_55_64': '55-64', 'Ind_65_79': '65-79', 'Ind_80p': '80+'}

        _D = AbstractEnergyDemand._getDevicesPerAgeGroup()
        _D = _D.rename(columns=_COLUMNS)
        _D = _D.astype(str)

        _E = AbstractEnergyDemand._getDeviceEnergyConsumption()
        _E = _E.drop(columns=['comment']).set_index('device')\
            .rename(columns={'Wh': 'Energy consumption'}).transpose()
        _E['smartphone'] = _E['smartphone'].apply(
            lambda s: s.replace('*delta', '$\\times\\delta$'))

        _S = AbstractEnergyDemand._getNormalScenario()
        _S = _S.set_index('Age group').transpose().rename(columns=_COLUMNS).transpose().reset_index()
        _S['IT equipment usage rate'] = _S['IT equipment usage rate'].apply(
            lambda s: s.replace('rect', '$\\Pi$'))
        _S['IT equipment usage rate'] = _S['IT equipment usage rate'].apply(
            lambda s: s.replace('*', '$\\times$'))
        '''
        _S['IT equipment usage rate'] = _S['IT equipment usage rate'].apply(
            lambda s: s.replace('snd', '$\\Phi$'))
        '''
        _S['IT equipment usage rate'] = _S['IT equipment usage rate'].apply(
            lambda s: sub('snd\(([0-9]*)\)', '$Phi_{\\1}$', s).replace('Phi', '\\Phi'))

        print(f'''
{_D.style.hide().to_latex(hrules=True)}

{_E.style.to_latex(hrules=True)}

{_S.style.hide().to_latex(hrules=True)}
''')
