# 	PET calculation after the LadyBug plugin (retrieved on Djordje Spasic's github :
# 	https://github.com/stgeorges/ladybug/commit/b0c2ea970252b62d22bf0e35d739db7f385a3f26)
#
# 	2017.11.10 by Edouard Walther and Quentin Goestschel:
# 		- fixed the error on the reference environment (see paper)
# 	
import math as math
import matplotlib.pyplot as plt
import numpy as np

# Input data #
# Environment constants  #
po = 1013.25  # atmospheric pressure [hPa]
p = 1013.25  # real pressure [hPa]
rob = 1.06  # Blood density kg/L
cb = 3640.0  # Blood specific heat [j/kg/k]
emsk = 0.99  # Skin emissivity [-]
emcl = 0.95  # Clothes emissivity [-]
Lvap = 2.42 * math.pow(10.0, 6.0)  # Latent heat of evaporation [J/Kg]
sigm = 5.67 * math.pow(10.0, -8.0)  # Stefan-Boltzmann constant [W/(m2*K^(-4))]
cair = 1010.0  # Air specific heat  [J./kg/K-]
rdsk = 0.79 * math.pow(10.0, 7.0)  # Skin diffusivity
rdcl = 0.0  # Clothes diffusivity

sex = 1
pos = 1
age = 35
mbody = 75  # Subject weight[kg]
ht = 1.80  # Subject size[m]
Adu = 0.203 * math.pow(mbody, 0.425) * math.pow(ht, 0.725)  # Dubois body area
bodyPosition = "standing"
feff = 0.725
sex = "male"

# Initialisation of the temperature set values
tc_set = 36.6
tsk_set = 34
tbody_set = 0.1 * tsk_set + 0.9 * tc_set


# calcul de la reaction metabolique
def system(ta, tmrt, rh, v_air, M, Icl):
	vpa = rh  # ACHTUNG
	# Area parameters of the body: #
	if Icl < 0.03:
		Icl = 0.02
	icl = Icl  # [clo] Clothing level
	eta = 0.0  # Body efficiency
	# Calculation of the Burton coefficient, k = 0.31 for Hoeppe:
	fcl = 1 + (0.31 * icl)  # Increasment of the exchange area depending on the clothing level:
	if bodyPosition == "sitting":
		feff = 0.696
	elif bodyPosition == "standing":
		feff = 0.725
	elif bodyPosition == "crouching":
		feff = 0.67
	facl = (173.51 * icl - 2.36 - 100.76 * icl * icl + 19.28 * math.pow(icl, 3.0)) / 100.0

	# Basic metabolism for men and women in [W/m2] #
	# Attribution of internal energy depending on the sex of the subject
	if sex == "male":
		met_base = 3.45 * math.pow(mbody, 0.75) * (1.0 + 0.004 * (30.0 - age) + 0.01 * (ht * 100.0 / math.pow(mbody, 1.0 / 3.0) - 43.4))
	else:
		met_base = 3.19 * math.pow(mbody, 0.75) * (1.0 + 0.004 * (30.0 - age) + 0.018 * (ht * 100.0 / math.pow(mbody, 1.0 / 3.0) - 42.1))
	# Source term : metabolic activity
	he = M + met_base
	h = he * (1.0 - eta)

	# Respiratory energy losses #
	# Expired air temperature calculation:
	texp = 0.47 * ta + 21.0

	# Pulmonary flow rate
	rtv = he * 1.44 * math.pow(10.0, -6.0)

	# Sensible heat energy loss:
	Cres = cair * (ta - texp) * rtv

	# Latent heat energy loss:
	vpexp = 6.11 * math.pow(10.0, 7.45 * texp / (235.0 + texp))  # Partial pressure of the breathing air
	Eres = 0.623 * Lvap / p * (vpa - vpexp) * rtv
	# total breathing heat loss
	qresp = (Cres + Eres)

	c = [0 for i in range(11)]
	tcore = [0 for i in range(7)]  # Core temperature list
	hc = 2.67 + 6.5 * math.pow(v_air, 0.67)  # Convection coefficient
	hc = hc * math.pow(p / po, 0.55)  # Correction with pressure

	# Clothed fraction of the body approximation #
	rcl = icl / 6.45  # conversion in m2.K/W
	y = 0
	if facl > 1.0:
		facl = 1.0
		rcl = icl / 6.45  # conversion clo --> m2.K/W
	# y : equivalent clothed height of the cylinder
	# High clothing level : all the height of the cylinder is covered
	if icl >= 2.0:
		y = 1.0
	if icl > 0.6 and icl < 2.0:
		y = (ht - 0.2) / ht
	if icl <= 0.6 and icl > 0.3:
		y = 0.5
	if icl <= 0.3 and icl > 0.0:
		y = 0.1
	# calculation of the closing radius depending on the clothing level (6.28 = 2* pi !)
	r2 = Adu * (fcl - 1.0 + facl) / (6.28 * ht * y)  # External radius
	r1 = facl * Adu / (6.28 * ht * y)  # Internal radius
	di = r2 - r1
	# clothed surface
	Acl = Adu * facl + Adu * (fcl - 1.0)
	# skin temperatures
	for j in range(1, 7):
		tsk = tsk_set
		count1 = 0
		tcl = (ta + tmrt + tsk) / 3.0  # Average value between the temperatures to estimate Tclothes
		enbal2 = 0.0
		while True:
			for count2 in range(1, 100):
				# Estimation of the radiation losses
				rclo2 = emcl * sigm * (math.pow(tcl + 273.2, 4.0) - math.pow(tmrt + 273.2, 4.0)) * feff
				# Calculation of the thermal resistance of the body:
				htcl = (6.28 * ht * y * di) / (rcl * math.log(r2 / r1) * Acl)
				tsk = (hc * (tcl - ta) + rclo2) / htcl + tcl  # Skin temperature calculation

				# Radiation losses #
				Aeffr = Adu * feff  # Effective radiative area depending on the position of the subject
				# For bare skin area:
				rbare = Aeffr * (1.0 - facl) * emsk * sigm * (math.pow(tmrt + 273.2, 4.0) - math.pow(tsk + 273.2, 4.0))
				# For dressed area:
				rclo = feff * Acl * emcl * sigm * (math.pow(tmrt + 273.2, 4.0) - math.pow(tcl + 273.2, 4.0))
				rsum = rbare + rclo  # [W]

				# Convection losses #
				cbare = hc * (ta - tsk) * Adu * (1.0 - facl)
				cclo = hc * (ta - tcl) * Acl
				csum = cbare + cclo  # [W]

				# Calculation of the Terms of the second order polynomial :
				K_blood = Adu * rob * cb
				c[0] = h + qresp
				c[2] = tsk_set / 2 - 0.5 * tsk
				c[3] = 5.28 * Adu * c[2]
				c[4] = 13.0 / 625.0 * K_blood
				c[5] = 0.76275 * K_blood
				c[6] = c[3] - c[5] - tsk * c[4]
				c[7] = -c[0] * c[2] - tsk * c[3] + tsk * c[5]
				c[9] = 5.28 * Adu - 0.76275 * K_blood - 13.0 / 625.0 * K_blood * tsk
				# discriminant #1 (b^2 - 4*a*c)
				c[10] = math.pow((5.28 * Adu - 0.76275 * K_blood - 13.0 / 625.0 * K_blood * tsk), 2) - 4.0 * c[4] * (c[5] * tsk - c[0] - 5.28 * Adu * tsk)
				# discriminant #2 (b^2 - 4*a*c)
				c[8] = c[6] * c[6] - 4.0 * c[4] * c[7]
				if tsk == tsk_set:
					tsk = tsk_set + 0.01
				# Calculation of Tcore[]:
				# case 6 : Set blood flow only
				tcore[6] = (h + qresp) / (5.28 * Adu + K_blood * 6.3 / 3600.0) + tsk
				# cas 2 : Set blood flow + regulation
				tcore[2] = (h + qresp) / (5.28 * Adu + K_blood * 6.3 / 3600.0 / (1.0 + 0.5 * (tsk_set - tsk))) + tsk
				# case 3 : Maximum blood flow only
				tcore[3] = c[0] / (5.28 * Adu + K_blood * 1.0 / 40.0) + tsk  #  max flow = 90 [L/m2/h]/3600 <=> 1/40
				# Roots calculation #1
				if c[10] >= 0.0:  # Numerical safety to avoid negative roots
					tcore[5] = (-c[9] - math.pow(c[10], 0.5)) / (2.0 * c[4])
					tcore[0] = (-c[9] + math.pow(c[10], 0.5)) / (2.0 * c[4])
				# Roots calculation #2
				if c[8] >= 0.0:
					tcore[1] = (-c[6] + math.pow(abs(c[8]), 0.5)) / (2.0 * c[4])
					tcore[4] = (-c[6] - math.pow(abs(c[8]), 0.5)) / (2.0 * c[4])

				# Calculation of sweat losses  #
				tbody = 0.1 * tsk + 0.9 * tcore[j - 1]
				# Sweating flow calculation
				swm = 304.94 * (tbody - tbody_set) * Adu / 3600000.0
				# Saturation vapor pressure at temperature Tsk and for 100% HR
				vpts = 6.11 * math.pow(10.0, 7.45 * tsk / (235.0 + tsk))
				if tbody <= tbody_set:
					swm = 0.0
				if sex == 2:
					swm = 0.7 * swm
				esweat = -swm * Lvap
				hm = 0.633 * hc / (p * cair)  # Evaporation coefficient [W/(m^2*Pa)]
				fec = 1.0 / (1.0 + 0.92 * hc * rcl)
				emax = hm * (vpa - vpts) * Adu * Lvap * fec  # Max latent flux
				wetsk = esweat / emax  # skin wettedness
				# esw: Latent flux depending on w [W.m-2]
				if wetsk > 1.0:
					wetsk = 1.0
				eswdif = esweat - emax  # difference between sweating and max capacity
				if eswdif <= 0.0:
					esw = emax
				if eswdif > 0.0:
					esw = esweat
				if esw > 0.0:
					esw = 0.0
				ed = Lvap / (rdsk + rdcl) * Adu * (1.0 - wetsk) * (vpa - vpts)  # diffusion heat flux

				vb1 = tsk_set - tsk  # difference for the volume blood flow calculation
				vb2 = tcore[j - 1] - tc_set  #  idem
				if vb2 < 0.0:
					vb2 = 0.0
				if vb1 < 0.0:
					vb1 = 0.0
				# Calculation of the blood flow depending on the difference with the set value
				vb = (6.3 + 75 * vb2) / (1.0 + 0.5 * vb1)
				# energy balance MEMI modele
				enbal = h + ed + qresp + esw + csum + rsum
				# clothing temperature
				if count1 == 0:
					xx = 1.0
				if count1 == 1:
					xx = 0.1
				if count1 == 2:
					xx = 0.01
				if count1 == 3:
					xx = 0.001
				if enbal > 0.0:
					tcl = tcl + xx
				if enbal < 0.0:
					tcl = tcl - xx
				if (enbal > 0.0 or enbal2 <= 0.0) and (enbal < 0.0 or enbal2 >= 0.0):
					enbal2 = enbal
					count2 += 1
				else:
					break
			if count1 == 0.0 or count1 == 1.0 or count1 == 2.0:
				count1 = count1 + 1
				enbal2 = 0.0
			else:
				break
		# end "While True" (using 'break' statements)
		for k in range(20):
			g100 = 0
			if count1 == 3.0 and (j != 2 and j != 5):
				if j != 6 and j != 1:
					if j != 3:
						if j != 7:
							if j == 4:
								g100 = True
								break
						else:
							if tcore[j - 1] >= tc_set or tsk <= tsk_set:
								g100 = False
								break
							g100 = True
							break
					else:
						if tcore[j - 1] >= tc_set or tsk > tsk_set:
							g100 = False
							break
						g100 = True
						break
				else:
					if c[10] < 0.0 or (tcore[j - 1] < tc_set or tsk <= 33.85):
						g100 = False
						break
					g100 = True
					break
			if c[8] < 0.0 or (tcore[j - 1] < tc_set or tsk > tsk_set + 0.05):
				g100 = False
				break
		if g100 == False:
			continue
		else:
			if (j == 4 or vb < 91.0) and (j != 4 or vb >= 89.0):
				# Maximum blood flow
				if vb > 90.0:
					vb = 90.0
				# water loss in g/m2/h
				ws = swm * 3600.0 * 1000.0
				if ws > 2000.0:
					ws = 2000.0
				wd = ed / Lvap * 3600.0 * (-1000.0)
				wr = Eres / Lvap * 3600.0 * (-1000.0)
				wsum = ws + wr + wd
				return tcore[j - 1], tsk, tcl, esw
		# water loss
		ws = swm * 3600.0 * 1000.0  # sweating
		wd = ed / Lvap * 3600.0 * (-1000.0)  # diffusion = perspiration
		wr = Eres / Lvap * 3600.0 * (-1000.0)  # respiration latent
		wsum = ws + wr + wd
		if j - 3 < 0:
			index = 3
		else:
			index = j - 3
		return tcore[index], tsk, tcl, esw


def pet(tc, tsk, tcl, ta_init, esw_real):
	# Input variables of the PET reference situation:
	icl_ref = 0.9  # clo
	M_activity_ref = 80  # W
	v_air_ref = 0.1  # m/s
	vpa_ref = 12  # hPa
	icl = icl_ref

	tx = ta_init
	tbody = 0.1 * tsk + 0.9 * tc
	enbal2 = 0.0
	count1 = 0

	# base metabolism
	if sex == "male":
		met_base = 3.45 * math.pow(mbody, 0.75) * (1.0 + 0.004 * (30.0 - age) + 0.01 * (ht * 100.0 / math.pow(mbody, 1.0 / 3.0) - 43.4))
	else:
		met_base = 3.19 * math.pow(mbody, 0.75) * (1.0 + 0.004 * (30.0 - age) + 0.018 * (ht * 100.0 / math.pow(mbody, 1.0 / 3.0) - 42.1))
	# breathing flow rate
	rtv_ref = (M_activity_ref + met_base) * 1.44 * math.pow(10.0, -6.0)

	swm = 304.94 * (tbody - tbody_set) * Adu / 3600000.0  # sweating flow rate 
	vpts = 6.11 * math.pow(10.0, 7.45 * tsk / (235.0 + tsk))  # saturated vapour pressure at skin surface
	if tbody <= tbody_set:
		swm = 0.0
	if sex == "female":
		swm = swm * 0.7
	esweat = -swm * Lvap
	esweat = esw_real
	# standard environment
	hc = 2.67 + 6.5 * math.pow(v_air_ref, 0.67)
	hc = hc * math.pow(p / po, 0.55)
	# radiation saldo
	Aeffr = Adu * feff
	facl = (173.51 * icl - 2.36 - 100.76 * icl * icl + 19.28 * math.pow(icl, 3.0)) / 100.0
	if facl > 1.0:
		facl = 1.0
	# Increase of the exchange area depending on the clothing level
	fcl = 1 + (0.31 * icl)
	Acl = Adu * facl + Adu * (fcl - 1.0)
	hm = 0.633 * hc / (p * cair)  # Evaporation coefficient [W/(m^2*Pa)]
	fec = 1.0 / (1.0 + 0.92 * hc * 0.155 * icl_ref)  # vapour transfer efficiency for reference clothing
	emax = hm * (vpa_ref - vpts) * Adu * Lvap * fec  # max latetn flux for the reference vapour pressure 12 hPa
	wetsk = esweat / emax
	# skin wettedness
	if wetsk > 1.0:
		wetsk = 1.0
	eswdif = esweat - emax
	# diffusion
	ediff = Lvap / (rdsk + rdcl) * Adu * (1.0 - wetsk) * (vpa_ref - vpts)
	# esw: sweating [W.m-2] from the actual environment : in depends only on the difference with the core set temperature
	if eswdif <= 0.0:
		esw = emax
	if eswdif > 0.0:
		esw = esweat
	if esw > 0.0: 
		esw = 0.0

	while count1 != 4:
		rbare = Aeffr * (1.0 - facl) * emsk * sigm * (math.pow(tx + 273.2, 4.0) - math.pow(tsk + 273.2, 4.0))
		rclo = feff * Acl * emcl * sigm * (math.pow(tx + 273.2, 4.0) - math.pow(tcl + 273.2, 4.0))
		rsum = rbare + rclo  # Recalculation of the radiative losses
		# convection
		cbare = hc * (tx - tsk) * Adu * (1.0 - facl)
		cclo = hc * (tx - tcl) * Acl
		csum = cbare + cclo  # Recalculation of the convective losses
		# breathing
		texp = 0.47 * tx + 21.0
		Cres = cair * (tx - texp) * rtv_ref
		vpexp = 6.11 * math.pow(10.0, 7.45 * texp / (235.0 + texp))
		Eres = 0.623 * Lvap / p * (vpa_ref - vpexp) * rtv_ref
		qresp = (Cres + Eres)
		# ----------------------------------------
		# energy balance
		enbal = (M_activity_ref + met_base) + ediff + qresp + esw + csum + rsum
		if count1 == 0:
			xx = 1.0
		if count1 == 1:
			xx = 0.1
		if count1 == 2:
			xx = 0.01
		if count1 == 3:
			xx = 0.001
		if enbal > 0.0:
			tx = tx - xx
		if enbal < 0.0:
			tx += xx
		if (enbal > 0.0 or enbal2 <= 0.0) and (enbal < 0.0 or enbal2 >= 0.0):
			enbal2 = enbal
		else:
			count1 = count1 + 1
	return tsk, enbal, esw, ediff, tx, tcl

# real environment
# M_activity=80 # [W]
# icl=0.9
# Tair=21
# Tmrt=21
# v_air=0.1
# pvap=12. #Imposed value of Pvap

# tc, tsk, tcl, esw_real = system(Tair, Tmrt, pvap, v_air, M_activity, icl)
# tsk, enbal, esw, ed, PET, tcl = pet(tc, tsk, tcl, Tair, esw_real)

# print("PET value", round(PET,2))
# print("Tc ", round(tc,2)," / Tsk ", round(tsk,2)," / Tcl ", round(tcl,2))
