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
from numpy import abs, exp

from t4gpd.comfort.algo.CommonsLib import CommonsLib
from t4gpd.comfort.algo.ConstantsLib import ConstantsLib


class ETULib(object):
    '''
    classdocs
    '''

    @staticmethod
    def assess_etu(AirTC, RH, WS_ms, T_mrt, N, Albedo, SR01Up_1, SR01Dn_1, IR01UpCo_1, IR01DnCo_1):
        # Calculation of direct and diffuse shortwave radiation based on nebulosity approximation 
        # from MF weather station
        SDIF, Idn = CommonsLib.SDIF_Idn(N, SR01Up_1)

        # Air pressure in Pascal and mPa
        P_a, P_air = CommonsLib.airPressure(AirTC, RH)

        hc = CommonsLib.convectiveHeatTransferCoefficient(AirTC, WS_ms, P_a)

        # Fpcl permeation efficiency factor of clothing [-] after Huang (2006):
        Fpcl = 1 / (1 + 0.143 * hc * ConstantsLib.Icl)

        # frd effective radiation area factor [-] assumed to be alpha_eff 
        frd = ConstantsLib.alpha_eff

        # radiant heat transfer coefficient 
        hr = CommonsLib.radiantHeatTransferCoefficient(AirTC, RH, WS_ms, T_mrt)

        # combined heat transfer coefficient
        h = hc + hr

        # Fcl clothing thermal efficiency factor [-]
        Fcl = 1 / (1 + 0.155 * h * ConstantsLib.fcl * ConstantsLib.Icl)

        # Fcle effective clothing thermal efficiency [-]
        Fcle = Fcl * ConstantsLib.fcl

        hu = ((ConstantsLib.hco + ConstantsLib.hro)
               * ConstantsLib.Fcleo)  # 7.5 W.m-2.K-1
        # hv = (ConstantsLib.hco * ConstantsLib.Fcleo + 
        #       hr * Fcle)

        # "Lewis Relation" for air-vapor layer over skin surface
        La = (15.15 * (ConstantsLib.tsk + ConstantsLib.T_kel)
              / ConstantsLib.T_kel)
        # he 
        he = La * hc

        # he_prim_ETU = he * Fpcl * ConstantsLib.fcl

        # representative air temperature: the air temperature of an isothermal environment 
        # at predicted mean vote (PMV)=0
        T_ao = ConstantsLib.T_v

        #--------------------------------------------------
        # 1. TEMPERATURE
        #--------------------------------------------------
        # non-uniform air temperature field
        NUATF = (ConstantsLib.hco + ConstantsLib.hro) * (AirTC - T_ao)

        #--------------------------------------------------
        # 2. RADIATION
        #--------------------------------------------------
        # standard effective longwave radiant field
        SERFL = ConstantsLib.hro * ConstantsLib.Fcleo * (T_mrt - AirTC)

        # net direct solar radiation to the body [W.m-2]
        Rdir = (ConstantsLib.ah * ConstantsLib.fp
                * ConstantsLib.fcl * Idn)
        # net diffuse solar radiation to the body [W.m-2]
        Rdif = (ConstantsLib.ah * ConstantsLib.phi_skyh
                * frd * ConstantsLib.fcl * SDIF)
        # net reflected solar radiation to the body [W.m-2]
        Rref = (Albedo * ConstantsLib.ah 
                * ConstantsLib.phi_groundh * frd 
                * ConstantsLib.fcl * SR01Up_1)

        # effective shortwave radiant field (ERFS): effective temperature difference in air 
        # temperature caused by the heating power of solar radiation and is defined as the 
        # net solar energy exchanged on the exposed body surface (Rs or called short-wave 
        # solar radiation heat gain on human body) [W/m2]
        ERFS = Rdir + Rdif + Rref
        # Thermal velocity radiation-related Field (TVFr)
        TVFr = ((ConstantsLib.hro * ConstantsLib.Fcleo 
                 -hr * Fcle) * (ConstantsLib.tsk - T_mrt))

        #--------------------------------------------------
        # 3. Humidity
        #--------------------------------------------------
        # calculation of evaporative heat loss from sweating
        # mean body temperature [C]
        tb = (ConstantsLib.alpha * ConstantsLib.tsk + 
              (1 - ConstantsLib.alpha) * ConstantsLib.tcr)
        # mean neutral body temperature [C]
        tbn = (ConstantsLib.alpha * ConstantsLib.tskn + 
               (1 - ConstantsLib.alpha) * ConstantsLib.tcrn)
        Wsigb = abs(tb - tbn)
        Wsigsk = abs(ConstantsLib.tsk - ConstantsLib.tskn)
        # evaporative resistance of clothing [m2.kPa.W-1]
        Recl = ConstantsLib.Icl / (La * ConstantsLib.icl)
        # maximum evaporative heat loss
        Emax = (ConstantsLib.P_ssk - P_air) / (Recl + 1 / (ConstantsLib.fcl * he))
        # Emax2= he*(P_ssk-P_air) #Parsons(2003)
        # Mrsw rate at which sweat is secreted (...)
        Mrsw = 4.7 * 10 ** (-5) * Wsigb * exp(Wsigsk / 10.7)
        # evaporative heat loss from sweating
        Ersw = Mrsw * ConstantsLib.hfg
        # w skin wettedness [-] after Gagge et al.(1986) with values between 0.06 and 1 (dry-completely wet)
        w = 0.06 + 0.94 * (Ersw / Emax)

        # Thermal velocity evaporation-related field (TVFe)
        TVFe = ((w * ConstantsLib.heo * ConstantsLib.Fpclo 
                 * ConstantsLib.fclo - w * he * Fpcl 
                 * ConstantsLib.fcl) * (ConstantsLib.P_ssk - P_air))

        #--------------------------------------------------
        # 4. WIND
        #--------------------------------------------------
        # Thermal velocity field (TVF) [W/m2] is a measure of the cooling power of the actual air velocity and is defined as the net convective heat energy exchanged on the body surface.
        TVF = ((ConstantsLib.hco * ConstantsLib.Fcleo - 
                hc * Fcle) * (ConstantsLib.tsk - AirTC))

        # Effective velocity and clothing field 
        EVCF = TVF + TVFr + TVFe

        #===================================================
        # Calculation of ETU based on Watanabe et al. (2014)
        ETU = CommonsLib.iterationEtu(w, ConstantsLib.heo, P_air,
                                      T_ao, hu, NUATF, SERFL, ERFS, EVCF)

        # recalculate Hymidity with new ETU
        # P_ETUs saturated water vapor pressure at ETU, kPa
        P_ETUs = exp(18.956 - (4030.183 / (ETU + 235)))  # [mb]
        P_ETUs = P_ETUs / 10  # [kPa]

        # standard effective humid field
        SEHF = w * ConstantsLib.heo * (P_air - 0.5 * P_ETUs)

        # Effective temperature differences
        dif_NUATF = NUATF / hu
        dif_SERFL = SERFL / hu
        dif_ERFS = ERFS / hu
        dif_SEHF = SEHF / hu
        dif_EVCF = EVCF / hu

        return ETU, dif_NUATF, dif_SERFL, dif_ERFS, dif_SEHF, dif_EVCF
