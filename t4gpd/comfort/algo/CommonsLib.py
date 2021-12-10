'''
Created on 12 mai 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from numpy import abs, exp, mean, sin, sqrt

from t4gpd.comfort.algo.ConstantsLib import ConstantsLib


class CommonsLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def airPressure(AirTC, RH):
        # Air pressure in Pascal and mPa
        # Saturated water pressure
        P_s = exp(18.956 - (4030.183 / (AirTC + 235)))  # [mb] 10mb=1kPa=1000Pa=1000N.m-2
        # Partial air pressure at T_air in Pascal
        P_a = RH * P_s
        # Partial air pressure at T_air in [kPa]
        P_air = P_a / 1000
        return P_a, P_air

    @staticmethod
    def convectiveHeatTransferCoefficient(AirTC, WS_ms, P_a):
        # calculation of hc parameter depending on wind speed
        if (0.1 <= WS_ms):
            # convective heat transfer coefficient (W m2 K???1) after Staiger et al. (2012) as 
            # for external conditions only forced convection v_air > 0.1 m/s 
            hc = 12.1 * sqrt(WS_ms * P_a / 1013.25)
        else:
            # convective heat transfer coefficient (W m???2 K???1) after Parsons (2003) and Da Silva
            var = WS_ms + 0.0052 * (ConstantsLib.M - 58)
            hc_1 = 2.38 * abs(ConstantsLib.tsk - AirTC) ** 0.25  
            hc_2 = 3.5 + 5.2 * var
            hc_3 = 8.7 * var ** 0.6
            # max value of hc between natural and forced convection
            hc = max(hc_1, hc_2, hc_3)
        return hc

    @staticmethod
    def iterationEtu(w, heo, P_air, T_ao, hu, NUATF, SERFL, ERFS, EVCF):
        '''
        function to approximate ETU after Watanabe et al. (2014)
        function for iterating the the universal effective temperature in degrees Celsius (C)
        '''
        # P_ETUs saturated water vapor pressure at ETU, kPa
        P_ETUs = exp(18.956 - (4030.183 / (T_ao + 235)))  # [mb] #first assumption that ETU is T_ao?????
        P_ETUs = P_ETUs / 10  # [kPa]
        
        # standard effective humid field
        SEHF = w * heo * (P_air - 0.5 * P_ETUs)
        
        ETU = T_ao + 1 / hu * (NUATF + SERFL + ERFS + SEHF + EVCF)
  
        while True:
            err_ETU = ETU - (T_ao + 1 / hu * (NUATF + SERFL + ERFS + SEHF + EVCF))
            if (0.001 < abs(err_ETU)):
                ETU = ETU + 0.1
                P_ETUs = exp(18.956 - (4030.183 / (ETU + 235)))  # [mb]
                P_ETUs = P_ETUs / 10  # [kPa]
                SEHF = w * heo * (P_air - 0.5 * P_ETUs)
            else:
                return ETU

    @staticmethod
    def iterationTcl(tsk, Icl, fcl, hc, T_kel, T_air, T_mrt, tcl_init):
        '''
        # ITERATION_TCL
        # for PMV  and PT calculation
        # function for iterating the clothing surface temperature, in degrees Celsius (C)
        '''
        oldTcl = tcl_init
        dif_min_tcl = 0.001  # C

        while True:
            newTcl = (oldTcl - 
                      ((oldTcl - tsk + Icl * fcl * 
                        (3.96e-8 * ((oldTcl + T_kel) ** 4 - (T_mrt + T_kel) ** 4))
                        +hc * (oldTcl - T_air)) / 
                        (1 + Icl * fcl * (3.96e-8 * 4 * (oldTcl + T_kel) ** 3
                                          +hc * (oldTcl)))))  # after Staiger et al. (2012)

            dif = abs(oldTcl - newTcl)
            oldTcl = mean([newTcl, oldTcl])
            if (dif < dif_min_tcl):
                return oldTcl
            oldTcl = newTcl

    @staticmethod
    def radiantHeatTransferCoefficient(AirTC, RH, WS_ms, T_mrt):
        # frd effective radiation area factor [-] assumed to be alpha_eff 
        frd = ConstantsLib.alpha_eff

        P_a, _ = CommonsLib.airPressure(AirTC, RH)

        hc = CommonsLib.convectiveHeatTransferCoefficient(AirTC, WS_ms, P_a)

        # initial clothing surface temperature, in degrees Celsius (C)
        tcl_init = AirTC

        # Call function "ITERATION_TCL" the clothing surface temperature, in degrees Celsius (C)
        tcl = CommonsLib.iterationTcl(
            ConstantsLib.tsk, ConstantsLib.Icl, ConstantsLib.fcl, hc,
            ConstantsLib.T_kel, AirTC, T_mrt, tcl_init)

        # radiant heat transfer coefficient 
        hr = (ConstantsLib.epsi_p * ConstantsLib.sigma_B * frd * 
              ((tcl + ConstantsLib.T_kel) ** 4 - 
               (T_mrt + ConstantsLib.T_kel) ** 4) / 
              ((tcl + ConstantsLib.T_kel) - (T_mrt + ConstantsLib.T_kel)))
        return hr

    @staticmethod
    def SDIF_Idn(N, SR01Up_1):
        # Calculation of direct and diffuse shortwave radiation based on nebulosity approximation 
        # from MF weather station

        # Calculation of clearness index K and diffuse solar radiation coeff DIFF
        # K calcule en fonction de la regression quadratique de Black (1956)
        # DIFF calcule en fonction de Muneer et al. (2004)
        K = 0.803 - 0.458 * (N / 8.) ** 2 - 0.34 * (N / 8.)
        if (K < 0.2):
            DIFF = 0.98
        else:
            DIFF = 0.962 + 0.779 * K - 4.375 * K ** 2 + 2.716 * K ** 3

        # Calculation of direct and diffuse repartition of incoming global radiation (SWin=UP) 
        SDIR = (1.0 - DIFF) * SR01Up_1
        SDIF = DIFF * SR01Up_1

        # Idn [W.m-2] normal direct solar radiation
        Idn = SDIR / sin(ConstantsLib.h_sun_rad)

        return (SDIF, Idn)
