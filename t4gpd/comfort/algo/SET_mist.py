# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 17:39:51 2021

@author: xlaffaille
"""
import math


def set_mist_optimized(tdb, tr, v, rh, met, clo, vapor_pressure, wme, body_surface_area,
                       patm, fa_eff, p_mist):  # fa_eff et p_mist ajouté par Xenia
    # Initial variables as defined in the ASHRAE 55-2017
    air_velocity = max(v, 0.1)
    k_clo = 0.25
    body_weight = 69.9
    met_factor = 58.2
    sbc = 0.000000056697  # Stefan-Boltzmann constant (W/m2K4)
    c_sw = 170  # driving coefficient for regulatory sweating
    c_dil = 120  # driving coefficient for vasodilation
    c_str = 0.5  # driving coefficient for vasoconstriction

    temp_skin_neutral = 33.7
    temp_core_neutral = 36.8
    temp_body_neutral = 36.49
    skin_blood_flow_neutral = 6.3

    temp_skin = temp_skin_neutral
    temp_core = temp_core_neutral
    skin_blood_flow = skin_blood_flow_neutral
    alfa = 0.1  # fractional skin mass
    e_sk = 0.1 * met  # total evaporative heat loss, W

    pressure_in_atmospheres = patm / 101325
    length_time_simulation = 60  # length time simulation
    r_clo = 0.155 * clo  # thermal resistance of clothing, °C M^2 /W

    f_a_cl = 1.0 + 0.15 * clo  # increase in body surface area due to clothing
    lr = 2.2 / pressure_in_atmospheres  # Lewis ratio
    rm = met * met_factor  # metabolic rate
    m = met * met_factor

    if clo <= 0:
        w_crit = 0.38 * pow(air_velocity, -0.29)  # evaporative efficiency
        i_cl = 1.0  # thermal resistance of clothing, clo
    else:
        w_crit = 0.59 * pow(air_velocity, -0.08)
        i_cl = 0.45

    # h_cc corrected convective heat transfer coefficient
    h_cc = 3.0 * pow(pressure_in_atmospheres, 0.53)
    # h_fc forced convective heat transfer coefficient, W/(m2 °C)
    h_fc = 8.600001 * pow((air_velocity * pressure_in_atmospheres), 0.53)
    h_cc = max(h_cc, h_fc)

    c_hr = 4.7  # linearized radiative heat transfer coefficient
    CTC = c_hr + h_cc
    r_a = 1.0 / (f_a_cl * CTC)  # resistance of air layer to dry heat
    t_op = (c_hr * tr + h_cc * tdb) / CTC  # operative temperature

    # initialize some variables
    dry = 0
    p_wet = 0
    _set_mist = 0  # ajoute _mist au _set par Xenia

    for TIM in range(length_time_simulation):

        iteration_limit = 150
        # t_cl temperature of the outer surface of clothing
        t_cl = (r_a * temp_skin + r_clo * t_op) / (r_a + r_clo)  # initial guess
        n_iterations = 0
        tc_converged = False

        while not tc_converged:

            c_hr = 4.0 * sbc * ((t_cl + tr) / 2.0 + 273.15) ** 3.0 * 0.72
            CTC = c_hr + h_cc
            r_a = 1.0 / (f_a_cl * CTC)
            t_op = (c_hr * tr + h_cc * tdb) / CTC
            t_cl_new = (r_a * temp_skin + r_clo * t_op) / (r_a + r_clo)
            if abs(t_cl_new - t_cl) <= 0.01:
                tc_converged = True
            t_cl = t_cl_new
            n_iterations += 1

            if n_iterations > iteration_limit:
                raise StopIteration("Max iterations exceeded")

        dry = (temp_skin - t_op) / (r_a + r_clo)  # total sensible heat loss, W
        # h_fcs rate of energy transport between core and skin, W
        h_fcs = (temp_core - temp_skin) * (5.28 + 1.163 * skin_blood_flow)
        q_res = 0.0023 * m * (44.0 - vapor_pressure)  # heat loss due to respiration
        CRES = 0.0014 * m * (34.0 - tdb)
        s_core = m - h_fcs - q_res - CRES - wme  # rate of energy storage in the core
        s_skin = h_fcs - dry - e_sk  # rate of energy storage in the skin
        TCSK = 0.97 * alfa * body_weight
        TCCR = 0.97 * (1 - alfa) * body_weight
        DTSK = (s_skin * body_surface_area) / (TCSK * 60.0)  # °C per minute
        DTCR = s_core * body_surface_area / (TCCR * 60.0)
        temp_skin = temp_skin + DTSK
        temp_core = temp_core + DTCR
        t_body = alfa * temp_skin + (1 - alfa) * temp_core  # mean body temperature, °C
        # sk_sig thermoregulatory control signal from the skin
        sk_sig = temp_skin - temp_skin_neutral
        warms = (sk_sig > 0) * sk_sig  # vasodialtion signal
        colds = ((-1.0 * sk_sig) > 0) * (-1.0 * sk_sig)  # vasoconstriction signal
        # c_reg_sig thermoregulatory control signal from the skin, °C
        c_reg_sig = temp_core - temp_core_neutral
        # c_warm vasodilation signal
        c_warm = (c_reg_sig > 0) * c_reg_sig
        # c_cold vasoconstriction signal
        c_cold = ((-1.0 * c_reg_sig) > 0) * (-1.0 * c_reg_sig)
        BDSIG = t_body - temp_body_neutral
        WARMB = (BDSIG > 0) * BDSIG
        skin_blood_flow = (skin_blood_flow_neutral + c_dil * c_warm) / (
            1 + c_str * colds
        )
        if skin_blood_flow > 90.0:
            skin_blood_flow = 90.0
        if skin_blood_flow < 0.5:
            skin_blood_flow = 0.5
        REGSW = c_sw * WARMB * math.exp(warms / 10.7)
        if REGSW > 500.0:
            REGSW = 500.0
        e_rsw = 0.68 * REGSW  # heat lost by vaporization sweat
        r_ea = 1.0 / (lr * f_a_cl * h_cc)  # evaporative resistance air layer
        r_ecl = r_clo / (lr * i_cl)
        # e_max = maximum evaporative capacity
        e_max = (
            math.exp(18.6686 - 4030.183 / (temp_skin + 235.0)) - vapor_pressure
        ) / (r_ea + r_ecl)
        p_rsw = e_rsw / e_max  # ratio heat loss sweating to max heat loss sweating
        p_wet = 0.06 + 0.94 * p_rsw  # skin wetness
        e_diff = p_wet * e_max - e_rsw  # vapor diffusion through skin
        if p_wet > w_crit:
            p_wet = w_crit
            p_rsw = w_crit / 0.94
            e_rsw = p_rsw * e_max
            e_diff = 0.06 * (1.0 - p_rsw) * e_max
        if e_max < 0:
            e_diff = 0
            e_rsw = 0
            p_wet = w_crit
        e_sk = (
            e_rsw + e_diff
        )  # total evaporative heat loss sweating and vapor diffusion
        MSHIV = 19.4 * colds * c_cold
        m = rm + MSHIV
        alfa = 0.0417737 + 0.7451833 / (skin_blood_flow + 0.585417)
        
    #################################################################### Debut Xenia
    # saturated water vapor pressure at the clothing temperature
    p_clo = math.exp(18.956 - 4030.183 / (t_cl + 235)) 
    p_clo = p_clo / 10  # [kPa]
  
    # rate of total evaporative heat loss from the skin at misting
    e_mist = fa_eff * (1 - p_wet) * p_mist * (p_clo - vapor_pressure) / r_ea
  
    # sum of skin wetness at clothed nodes Esk+Emist - total evaporative heat loss from the skin in misting environement
    e_clo = e_sk + e_mist
  
    # total heat loss from skin, W
    hsk = dry + e_clo  
    #################################################################### Fin Xenia
    
    W = p_wet
    PSSK = math.exp(18.6686 - 4030.183 / (temp_skin + 235.0))
    CHRS = c_hr
    if met < 0.85:
        CHCS = 3.0
    else:
        CHCS = 5.66 * (met - 0.85) ** 0.39
    if CHCS < 3.0:
        CHCS = 3.0
    CTCS = CHCS + CHRS
    RCLOS = 1.52 / ((met - wme / met_factor) + 0.6944) - 0.1835
    RCLS = 0.155 * RCLOS
    FACLS = 1.0 + k_clo * RCLOS
    FCLS = 1.0 / (1.0 + 0.155 * FACLS * CTCS * RCLOS)
    IMS = 0.45
    ICLS = IMS * CHCS / CTCS * (1 - FCLS) / (CHCS / CTCS - FCLS * IMS)
    RAS = 1.0 / (FACLS * CTCS)
    REAS = 1.0 / (lr * FACLS * CHCS)
    RECLS = RCLS / (lr * ICLS)
    HD_S = 1.0 / (RAS + RCLS)
    HE_S = 1.0 / (REAS + RECLS)

    delta = 0.0001
    dx = 100.0
    set_mist_old = round(temp_skin - hsk / HD_S, 2)
    while abs(dx) > 0.01:  # ajoute _mist au _set par Xenia
        err_1 = (
            hsk
            -HD_S * (temp_skin - set_mist_old)
            -W
            * HE_S
            * (PSSK - 0.5 * (math.exp(18.6686 - 4030.183 / (set_mist_old + 235.0))))
        )
        err_2 = (
            hsk
            -HD_S * (temp_skin - (set_mist_old + delta))
            -W
            * HE_S
            * (PSSK - 0.5 * (math.exp(18.6686 - 4030.183 / (set_mist_old + delta + 235.0))))
        )
        _set_mist = set_mist_old - delta * err_1 / (err_2 - err_1)
        dx = _set_mist - set_mist_old
        set_mist_old = _set_mist

    return _set_mist
