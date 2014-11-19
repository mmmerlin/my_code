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
    outlist = []

    FILE_TYPE = '.png'    
    OUTPUT_PATH = "/mnt/hgfs/VMShared/output/QE_LSST/112-04/"

    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'
#     path = '/mnt/hgfs/VMShared/Data/QE_LSST/113-03/wl/20140709-112014/'
#     calib_file = '/mnt/hgfs/VMShared/output/QE_LSST/113-03/calib.txt'
    
    path        = '/mnt/hgfs/VMShared/Data/QE_LSST/112-04/wl/20140419-190507/'
    calib_file  = '/mnt/hgfs/VMShared/output/QE_LSST/112-04/calib.txt'
    

    files_in_dir = os.listdir(path)
    files_in_dir.sort()
    
    
#     wavelengths = [filename[14:18] for filename in files_in_dir if filename[14:18] != 'bias']
#     files = [join(path, filename)  for filename in files_in_dir if filename[14:18] != 'bias']   # exclude bias file
    
    wavelengths = [filename[14:18] for filename in files_in_dir if filename.find('bias') == -1]
    files = [join(path, filename)  for filename in files_in_dir if filename.find('bias') == -1]   # exclude bias file
    bias_files = [join(path, filename) for filename in files_in_dir if filename.find('bias') != -1]   # make list of bias file

#     ADC_Offsets, NoiseFactors = GetADC_OffsetsAndNoisesFromBiasFiles(path)
#     wavelength_selection = ['1050']

#     wavelengths = [320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420,425,430,435,440,445,450,465,480,495,510,525,540,555,570,585,600,615,630,645,660,675,690,705,720,735,750,765,780,795,810,825,840,855,870,885,900,915,930,945,950,955,960,965,970,975,980,985,990,995,1000,1005,1010,1015,1020,1025,1030,1035,1040,1045,1050,1055,1060,1065,1070,1075,1080]
    
    gains, ADC_Offsets, NoiseFactors = np.loadtxt(calib_file, skiprows = 1, delimiter = '\t', unpack = True, usecols = (1,2,3))

#     gains = [3.79509352,3.851916292,3.834108654,3.876996568,3.835078189,3.856641255,3.832781099,3.856389413,3.758698179,3.808504386,3.742609872,3.810088368,3.775578121,3.809432767,3.780270026,3.79986126] #112-04 750 file set gains
    gains = [3.863893926,3.889311364,3.839592821,3.880267774,3.829443828,3.859452995,3.8523837,3.826228492,3.913972084,3.952911679,3.844514444,3.9919436,3.897239172,3.957293714,3.879582217,3.888644858] #112-04 900 file set gains
    
    for i in range(16):
        print i, '\t', gains[i]
#     exit()

    for filenum in range(len(files)):
        
        wavelength = wavelengths[filenum]
        filename = files[filenum]
        
        
#         if wavelength not in wavelength_selection: continue
        if wavelength != '0660': continue
        


##############################################
###### for plotting the photodiode curves in python
##############################################
#         hdulist = pf.open(filename)
#         import pylab as pl
#         import matplotlib
#         junk0, junk1, t, y = zip(*hdulist[17].data)
#         stats, loc = monodiode_current(hdulist)
#         pl.figure()
# #         pl.plot(t, y, "-")
#         pl.plot(junk0, junk1, "-")
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
#         exit()
#         continue
##############################################

         
##############################################
###### extract photodiode data
# ##############################################
        if False:
            hdulist = pf.open(filename)
            exptime = hdulist[0].header['exptime']
             
            t, y, t_alt, y_alt = zip(*hdulist[17].data)
    #         for i in range(len(t)):
    #             print str(t[i]) + '\t' + str(y[i]) + '\t' + str(t_alt[i]) + '\t' + str(y_alt[i])
             
     
            stats, loc = monodiode_current(hdulist)
            turnon_time = loc[0]
             
            if len(loc) == 2:
                turnoff_time = loc[1]
            else:
                turnoff_time = 99
                 
            if np.abs(np.average(y)) > 25:
                y_true = y
            else:
                y_true = y_alt
             
            baseline = np.average(y_true[0:turnon_time - 4])        
            peak_value = np.average(y_true[turnon_time + 4:turnoff_time + 1])   
            light_time = max(exptime, (t[turnoff_time]-t[turnon_time]))
            integral = -1. * light_time * (peak_value - baseline)

             
             
            line = '%s\t%s\t%s\t%s\t%s'%(wavelength, baseline, peak_value, light_time, integral)
            outlist.append(line)
    #         print "baseline = ", baseline
    #         print "peak_value = ", peak_value
    #         print "light_time = ", light_time
    #         print "integral = ", integral
# ##############################################
        
        
        
        
##############################################
###### ADU subtract, gain correct and integrate images
##############################################   
        if True:
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
##############################################   
        
        

    for line in outlist:
        print line
        

    print '\n***End code***'




