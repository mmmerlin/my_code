from __builtin__ import str, len
from monodiode_current import monodiode_current

import lsst.afw.image       as afwImg
import lsst.afw.detection   as afwDetect
import lsst.afw.display.ds9 as ds9

import os
from os.path import join

import ROOT
from ROOT import TCanvas, TH1F
from root_functions import Browse, CANVAS_HEIGHT, CANVAS_WIDTH

from image_assembly import AssembleImage, MakeBiasImage, MakeBiasImage_SingleAmp
from my_image_tools import HistogramImage, FastHistogramImage, HistogramImage_NoAssembly, FastHistogramImageData, GetADC_OffsetsAndNoisesFromBiasFiles

import pyfits as pf
import numpy as np


N_AMPS = 16


if __name__ == '__main__':
    print "Running LSST QE Measurement"

    FILE_TYPE = '.png'    
    OUTPUT_PATH = "/mnt/hgfs/VMShared/output/QE_LSST/"

    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'
    path = '/mnt/hgfs/VMShared/Data/QE_LSST/wl/20140709-112014/'
    outlist = []

    files_in_dir = os.listdir(path)
    files_in_dir.sort()
    
    wavelengths = [filename[14:18] for filename in files_in_dir if filename[14:18] != 'bias']
    files = [join(path, filename)  for filename in files_in_dir if filename[14:18] != 'bias']   # exclude bias file
    bias_files = [join(path, filename) for filename in files_in_dir if filename.find('bias') != -1]   # make list of bias file


#     gains = [3.315808402,3.327915473,3.378822094,3.344825272,3.32604176, 3.380261393,3.339747603,3.357838184,3.294004911,3.245531036,3.219743995,3.225160702,3.254285149,3.294630888,3.231197772,3.25006113]  # DM subtraction
    gains = [3.541729119,3.571020775,3.641136857,3.589221983,3.540086205,3.668066435,3.576249221,3.519930087,3.526646634,3.488946929,3.467217943,3.451805651,3.492744071,3.569686091,3.463400864,3.401701491] # bias subtraction

    ADC_Offsets, NoiseFactors = GetADC_OffsetsAndNoisesFromBiasFiles(path)
    

#     wavelength_selection = ['0700']


    for filenum in range(len(files)):
        
        wavelength = wavelengths[filenum]
        filename = files[filenum]
        
#         if wavelength not in wavelength_selection: continue
        if wavelength != '0675': continue
        
        
#         hdulist = pf.open(filename)

##############################################
###### for plotting the photodiode curves in python
##############################################

#         import pylab as pl
#         import matplotlib
#         junk0, junk1, t, y = zip(*hdulist[17].data)
#         stats, loc = monodiode_current(hdulist)
#         pl.figure()
#         pl.plot(t, y, "-")
# #         pl.plot(junk0, junk1, "-")
#         pl.title(wavelength)
#         pl.xlabel("Time (?)")
#         pl.ylabel("Current (pA)")
#         pl.grid(True)
#         pl.figure()
#         pl.plot(t[loc[0]:loc[1]], y[loc[0]:loc[1]], "-o")
#         pl.xlabel("Time (?)")
#         pl.ylabel("Current (pA)")
#         pl.title(wavelength + "$\mu = %.3f$ $\sigma= %.3f$" % (stats[0], stats[1]))
#         pl.grid(True)
#         pl.show()
#         continue
##############################################

         
##############################################
###### extract photodiode data
# ##############################################
#         exptime = hdulist[0].header['exptime']
#         
#         t, y, t_alt, y_alt = zip(*hdulist[17].data)
# #         for i in range(len(t)):
# #             print str(t[i]) + '\t' + str(y[i]) + '\t' + str(t_alt[i]) + '\t' + str(y_alt[i])
#         
# 
#         stats, loc = monodiode_current(hdulist)
#         turnon_time = loc[0]
#         
#         if len(loc) == 2:
#             turnoff_time = loc[1]
#         else:
#             turnoff_time = 99
#             
#         if np.abs(np.average(y)) > 25:
#             y_true = y
#         else:
#             y_true = y_alt
#         
#         baseline = np.average(y_true[0:turnon_time - 4])        
#         peak_value = np.average(y_true[turnon_time + 4:turnoff_time + 1])   
#         light_time = max(exptime, (t[turnoff_time]-t[turnon_time]))
#         integral = -1. * light_time * (peak_value - baseline)
#         
#         
#         line = '%s\t%s\t%s\t%s\t%s'%(wavelength, baseline, peak_value, light_time, integral)
#         outlist.append(line)
# #         print "baseline = ", baseline
# #         print "peak_value = ", peak_value
# #         print "light_time = ", light_time
# #         print "integral = ", integral
# ##############################################
        
        
        
        
##############################################
###### ADU subtract, gain correct and integrate images
##############################################   
        image = AssembleImage(filename, metadata_filename, subtract_background = False, gain_correction_list = gains, ADC_Offsets = ADC_Offsets)
  
        try:
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'
        ds9.mtv(image)
        print 'done'
        exit()
     
        c3 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT) #create canvas
        hist, power, n_power_points = FastHistogramImageData(image.getArray(), -50000)

        hist.GetXaxis().SetRangeUser(0,30000)
        hist.GetYaxis().SetRangeUser(0,700000)
        hist.SetTitle(str(wavelength))
        hist.Draw()
        
        line = str(wavelength) + '\t' + str(power) + '\t' + str(n_power_points)
        outlist.append(line)
        
        suffix = ''
        prefix = 'gain_corrected_'
        c3.SaveAs(OUTPUT_PATH + prefix + str(wavelengths[filenum] + suffix + FILE_TYPE))
        c3.SaveAs(OUTPUT_PATH + "QE_animation" + ".gif+15")
       
        del c3, hist
        
        

    for line in outlist:
        print line
        

    print '\n***End code***'




