def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    return [float('nan') if x==0 else x for x in values]

import numpy as np
from scipy.interpolate import interp1d
import pylab as pl

plot_range = [320,1050]

current_sign = 1.
    
TWO_COLS = True
    
# #===========================================================================
master_sensitivity  = '/mnt/hgfs/VMShared/data/QE_Timepix/master_sensitivity.txt'

master_calib        = '/mnt/hgfs/VMShared/data/QE_Timepix/20151014/master_calibration_2.txt'
    
    
# data_file = '/mnt/hgfs/VMShared/data/QE_Timepix/20151014/1_thor_SM1PD1A.txt'
# data_file = '/mnt/hgfs/VMShared/data/QE_Timepix/20151014/2_timepixcam_7343-W6.txt'
# data_file = '/mnt/hgfs/VMShared/data/QE_Timepix/20151014/3_timepixcam_7343-W6.txt'
# data_file = '/mnt/hgfs/VMShared/data/QE_Timepix/20151014/4_timepixcam_7343-W6.txt'
# data_file = '/mnt/hgfs/VMShared/data/QE_Timepix/20151014/5_thor_SM1PD1A.txt'
 
 
data_file = '/mnt/hgfs/VMShared/data/QE_Timepix/20151014/fixed.txt'

 
thorlabs_calib_file = '/mnt/hgfs/VMShared/data/QE_Timepix/20151014/thorlabs_calib_data.txt'
dut_area = 25
# #===========================================================================


#===========================================================================
# master_calib        = '/mnt/hgfs/VMShared/data/QE_Timepix/Thorlabs_test/this_calib.txt'
# master_sensitivity  = '/mnt/hgfs/VMShared/data/QE_Timepix/master_sensitivity.txt'
#    
#    
# data_file           = '/mnt/hgfs/VMShared/data/QE_Timepix/Thorlabs_test/test_data.txt'
# thorlabs_calib_file = '/mnt/hgfs/VMShared/data/QE_Timepix/Thorlabs_test/thorlabs_calib_data.txt'
# dut_area = 63.62
#===========================================================================



#===============================================================================
plank = 6.62607E-34
c = 2.99792E+08
e_charge = 1.60218E-19

pd1_area = 104.8
#===============================================================================


if TWO_COLS:
    mc_wl, mc_pd1, mc_pd2 = np.loadtxt(master_calib, unpack = True)
else: 
    mc_wl, mc_ratio = np.loadtxt(master_calib, unpack = True)
wavelengths, pd1, dut = np.loadtxt(data_file, unpack = True)
master_sens_wl, master_sens= np.loadtxt(master_sensitivity, unpack = True)

mc_pd2 = [-1*val for val in mc_pd2] #sanitise all the silly decimals



wavelengths = [int(wl.round()) for wl in wavelengths] #sanitise all the silly decimals
mc_wl = [int(wl.round()) for wl in mc_wl] #sanitise all the silly decimals

assert len(wavelengths) == len(pd1) == len(dut)
print "Wavelength range = %s - %s nm"%(wavelengths[0], wavelengths[-1])

npoints = 1 + ((wavelengths[-1] - wavelengths[0]) / 5)
if npoints != len(wavelengths):
    raise Exception('Data points missing')


# assert len(wavelengths) == len(mc_wl)






###### Do interpolation
interp = interp1d(master_sens_wl, master_sens, kind='cubic')
t_new = np.linspace(min(master_sens_wl), max(master_sens_wl), len(master_sens_wl)*20)
# pl.plot(master_sens_wl,master_sens,'o',t_new,interp(t_new),'-')
# pl.show()
 
master_sens_interp = []
for wl in wavelengths:
    if wl > max(master_sens_wl): break #can't interpolate past the end of the real data
    master_sens_interp.append(interp(wl))


# for wl, ms_val in zip(wavelengths,master_sens_interp):
#     print wl, ms_val
# exit()


#trim all arrays to stop where the master sensitivity data stops
if TWO_COLS:
    n_valid_points = min(len(master_sens_interp), len(mc_pd1))
else:
    n_valid_points = min(len(master_sens_interp), len(mc_ratio))
    

mc_wl = mc_wl[0:n_valid_points]
if TWO_COLS: 
    mc_pd1 = mc_pd1[0:n_valid_points]
    mc_pd2 = mc_pd2[0:n_valid_points]
wavelengths = wavelengths[0:n_valid_points]
pd1 = pd1[0:n_valid_points]
dut = dut[0:n_valid_points]
master_sens_wl = master_sens_wl[0:n_valid_points]
master_sens = master_sens[0:n_valid_points]


assert mc_wl[0] == wavelengths[0]






QEs = [] 
responsivities= []

for i in range(len(wavelengths)):
    if TWO_COLS:
        value = current_sign * 100 * pd1[i] * mc_pd2[i] * master_sens_interp[i] * pd1_area * plank * c * 1e9 / (dut[i] * mc_pd1[i] * dut_area * e_charge * wavelengths[i])
    else:
        value = current_sign * 100 * pd1[i] * mc_ratio[i] * master_sens_interp[i] * pd1_area * plank * c * 1e9 / (dut[i] * dut_area * e_charge * wavelengths[i])
    QEs.append(value)
    resp_val = value * wavelengths[i] * 1e-9 * e_charge / (plank * c)
    responsivities.append(resp_val)
    False




#===============================================================================
# Plotting
#===============================================================================



pl.plot(wavelengths,zero_to_nan(QEs),'o')
pl.show(block = True)



pl.plot(wavelengths,zero_to_nan(responsivities),'or')
thorlabs_wls, thorlabs_calib = np.loadtxt(thorlabs_calib_file, unpack = True)
pl.plot(thorlabs_wls,thorlabs_calib*100,'ob')

pl.show(block = True)







print 'Finished'
exit()
