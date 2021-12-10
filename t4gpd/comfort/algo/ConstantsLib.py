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
from numpy import exp

from t4gpd.commons.AngleLib import AngleLib


class ConstantsLib(object):
    '''
    classdocs
    '''
    # ah [-] solar absorptivity of the clothed body after Watanabe et al. (2013) casual clothing:
    # summer = 0.66
    # autumn = 0.69
    # winter = 0.77
    ah = 0.66

    alpha = 0.2  # alpha 0.2 for sedentary, 0.1 for vasodilation and 0.33 for vasoconstriction
    alpha_eff = 0.72  # effective radiation surface of a subject in upright standing position
    alpha_k = 0.7  # absorption coefficient for shortwave radiation (visible = SR)
    alpha_l = 0.97  # absorption coefficient for longwave radiation (infrared = IR)

    body_surface_area = 1.8258  # body surface area, default value 1.8258 [m2] 

    Clo = 0.5  # clothing level

    # parameters for (Kestrel) Tmrt calculation based on observed globe temperature 
    D_glo = 25  # Diameter of globe thermometer (mm)
    epsi_p = 0.97  # body emissivity
    epsi_glo = 0.95  # Emissivite du globe for a black globe (Khuen et al., 1970)

    # fa_eff --> effective area factor between 0.1 and 1 (Oh et al., 2020) 
    # --> constant set at 0.5
    fa_eff = 0.5

    # clothing surface area factor fcl depending on clothing level 
    fcl = (1.0 + 0.2 * Clo) if (0.5 >= Clo) else (1.05 + 0.1 * Clo)  # clothing surface area factor

    # Clo clothing level in standard environment is 0 so that:
    # Fcleo effective clothing thermal efficiency [-] in standard environment is 1.0
    Fcleo = 1.0
    # fclo clothing area factor in the standard environment, dimensionless selon Watanabe et al. (2014)
    fclo = 0.31

    # for radiation calculation in ETU
    # fp [-] projected area factor
    fp = alpha_eff

    F_lat = 0.22  # angular factor for lateral direction (N-S et E-W)
    F_vert = 0.06  # angular factor for vertical direction (up-down)

    # hco convective heat transfer coefficient [W.m-2.K-1] in standard environment 3.0 W.m-2.K-1
    hco = 3.0
    # heo evaporative heat transfer coefficient [W.m-2.kPa-1] in standard environment 3.0 LR W/(m2 kPa)
    heo = 3.0

    hfg = 2430  # hfg heat of vaporization of water [kJ.kg-1] at 30 C

    # hro ou hrc radiant heat transfer coefficient [W.m-2.K-1] in standard environment 4.5 W.m-2.K-1
    hro = 4.5

    # h_sun solar altitude [deg]
    h_sun = 66
    # function to convert angles from deg to rad
    h_sun_rad = AngleLib.toRadians(h_sun) 

    icl = Clo  # intrinsic permeation efficiency ratio
    Icl = Clo * 0.155  # clothing insulation, in square meters Kelvin per watt (m2 K/W)

    Iclo = fclo * 0.155

    M = 93  # metabolic rate M, in Watt per square meter (W/m2)
    M_met = M / 58.2  # metabolic rate M_met, in met

    patm = 101325  # atmospheric pressure, default value 101325 [Pa]

    # phi_skyh [-] angle factor between the human body and sky surface
    phi_skyh = F_vert 
    # phi_groundh [-] angle factor between the human body and ground surface
    phi_groundh = F_vert

    p_mist = 0.25  # default value in Oh et al (2020)

    sigma_B = 5.67e-8  # Wm^(-2) K^(-4) Stefan-Boltzman constant

    tcr = 37.0  # body core temperature [C]
    tcrn = 36.8  # neutral core temperature [C]
    tskn = 33.7  # neutral skin temperature [C]

    T_kel = 273.15  # temperature in Kelvin for temperature conversion

    # T_v hypothetical air temperature [C] in standard environment: the air temperature of an 
    # isothermal environment at predicted mean vote (PMV)=0 
    T_v = 27.1

    W = 0  # effective mechanical power, in Watt per square meter (W/m2)
    W_met = W / 58.2  # effective mechanical power, in met

    tsk = 35.7 - 0.0275 * (M - W)  # skin external temperature tsk depending on M and W

    # Fpclo permeation efficiency factor in the standard environment, dimensionless
    Fpclo = 1 / (1 + 0.143 * hco * Iclo)

    # vapor pressure at skin temperature tsk
    # saturated air pressure at skin
    P_ssk = exp(18.956 - (4030.183 / (tsk + 235)))  # [mb] 10mb =1kPa = 1000Pa = 1000N.m-2
    P_ssk = P_ssk / 10  # [kPa]
