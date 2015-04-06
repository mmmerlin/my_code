import os
from os.path import expanduser, join
from os import listdir
import numpy as np
import string        
               
from ROOT import TCanvas, TF1, TH1F, TGraph, TFile
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import *
from math import floor
import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils
import lsst.afw.detection   as afwDetect
from root_functions import ListToHist, ListVsList
from lsst.afw.image import makeImageFromArray
import matplotlib.pyplot as pl

from my_functions import CentroidTimepixCluster

DISPLAY = True


# old sensor
xmin = 1
ymin = 1
xmax = 254
ymax = 254


# OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/'
OUTPUT_PATH = '/mnt/hgfs/VMShared/output/suny_01042015/big_runs/'

FILE_TYPE = ".png"

if __name__ == '__main__':
    if DISPLAY:
        try:
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'

#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A1(50nm_bad_bonds)/Run3/'
#     ID = 'A1_run3'
    
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A1(50nm_bad_bonds)/Run1/'
#     ID = 'A1_run1'

#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A2(300nm)/Run1/'
#     ID = 'A2_run1'
    
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A4(120nm)_eq_test/420/'
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A4(120nm)400thr/'
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A5(50nm)/'
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A1(50nm_bad_bonds)/Run1/'
    
    
    
    
    root_path     = '/mnt/hgfs/VMShared/Data/new_sensors/suny_01042015/50nm_big_runs/'
#     values = [410,415,418,420,421,422,423,424,425,426,427,428,429,430]
#     values = ['422_big_only_ions']
    values = ['422_big_only_electrons']
#     values = ['422_big']
    ID = ''
    
    
    root_path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A2(300nm)/'
    values = ['Run4/']
    OUTPUT_PATH = '/mnt/hgfs/VMShared/output/temp/'
    
    
    for val in values:
        ID = str(val)
        path = root_path + str(val) + '/'
        rootfilename = OUTPUT_PATH + ID + '.root'
        ROOTfile = TFile.Open(rootfilename, "RECREATE")
    
    #     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A3(200nm)/'
    #     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A4(120nm)400thr/'
    #     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/old_sensor/'
    #     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A5(50nm)/'
    
#         MakeToFSpectrum(path,OUTPUT_PATH + ID, 1, 254, 1, 254, False, [3900,4400])
    
    
        #########################
        c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        
    #     n_glitches = 0
    #     n_goodframes = 0
    #     n_pix_hits = 0
    #     nfiles = 0.
    #     
    #     for filename in os.listdir(path):
    #         xs, ys, ts = GetXYTarray_SingleFile(path + filename, xmin, xmax, ymin, ymax)
    #         assert len(xs) == len(ys) == len(ts)
    #         if len(xs) >= glitch_threshold: print "skipped glitch frame"; n_glitches +=1; continue
    #         n_goodframes += 1
    #         nfiles += 1
    #         n_pix_hits += len(ts)
    #          
    #     pixels_per_frame = float(n_pix_hits) / float(n_goodframes)
         
         
    #     intensity_array = MakeCompositeImage_Timepix(path, 1, 253, 1, 253, 0, 9999, -99999, 99999, return_raw_array=True)
    #     nfiles = len(os.listdir(path))
    # #     intensity_array /= float(nfiles)
    #     mask_pixels = np.where(intensity_array >= 0.03*(nfiles))
    #     print mask_pixels
    #     for element in mask_pixels:
    #         print element
    #          
    #     print mask_pixels
    #     print intensity_array[187][19]
         
             
    
        
    #     MaskBadPixels(intensity_array, pixel_mask)
    #     temp = makeImageFromArray(intensity_array)
    #     ds9.mtv(temp)
    #     exit()
        
        
        
        
        
        
        
#         nfiles = len(os.listdir(path))
#         
# #     #     intensity_array = MakeCompositeImage_Timepix(path, 1, 255, 1, 255, 0, 9999, -99999, 99999, return_raw_array=True)
#         intensity_array = MakeCompositeImage_Timepix(path, 0, 255, 0, 255, 0, 1000, -99999, 99999, return_raw_array=True)
#         ViewIntensityArrayInDs9(intensity_array, savefile=OUTPUT_PATH + str(val) + '_composite.jpeg')
#         exit()
#          
#         xlist, ylist = [],[]
#         for thr_range in range(1,1001):
#             badpixel_threshold = (float(thr_range)/1000.)*(nfiles)
#             index = np.where(intensity_array <= badpixel_threshold)
#             intensity_sum = intensity_array[index].sum(dtype = np.float64)
#     #         print str(thr_range/10.) + '\t' + str(intensity_sum/nfiles)
#             xlist.append(thr_range/10.)
#             ylist.append(intensity_sum/nfiles)
#          
#         fig = pl.figure(figsize = (16,9), dpi = 72)
#         pl.subplot(2,1,1)
#         pl.xlabel('Bad pixel hit threshold (%)', horizontalalignment = 'right' )
#         pl.ylabel('# Hit pixels')
#         pl.plot(xlist, ylist)
#         pl.subplot(2,1,2)
#         xmax_zoom_percentage = 20
#         pl.xlim([0,xmax_zoom_percentage])
#         pl.ylim([0,1.1*max(ylist[0:xmax_zoom_percentage * 10])])
#         pl.plot(xlist, ylist)
#         pl.xlabel('Bad pixel hit threshold (%)', horizontalalignment = 'right' )
#         pl.ylabel('# Hit pixels')
#         fig.savefig(OUTPUT_PATH + ID + '_Turn-on_curve.png')
#          
#         gr1 = ListVsList(xlist, ylist, OUTPUT_PATH + ID + '_Turn-on_curve_ROOT.png', xtitle = 'Bad pixel hit threshold (%)', ytitle='# Hit pixels')
#         gr2 = ListVsList(xlist, ylist, OUTPUT_PATH + ID + '_Turn-on_curve_ROOT_zoomed.png', xtitle = 'Bad pixel hit threshold (%)', ytitle='# Hit pixels', xmax = xmax_zoom_percentage, ymin=0, ymax = 1.1*max(ylist[0:xmax_zoom_percentage * 10]), set_grid = True)
#         gr1.SetName('Turn-on_curve')
#         gr2.SetName('Turn-on_curve_0-' + str(xmax_zoom_percentage))
#         gr1.Write()
#         gr2.Write()
#         del gr1, gr2
#      
#      
#         mask_list = GeneratePixelMaskListFromFileset(path, 0.40)  
#         pixel_mask = MakeMaskArray(mask_list)  
#         print 'masking %s pixels'%len(mask_list[0])
# 
# 
#         
# 
# 
#   
#         ViewIntensityArrayInDs9(-1*(pixel_mask-1), savefile=OUTPUT_PATH + str(val) + '_pixel_mask.jpeg')

###################################################################
        
        thresholdValue = 1
        npixMin = 2
        grow = 1
        isotropic = False
        
        cluster_sizes = []
        pixels_per_frame_list = []
        footprint_pixels_per_frame_list = []
        ions_per_frame = []
        
        display_num = 0
        for filenum, filename in enumerate(os.listdir(path)):
    #         OpenTimepixInDS9(path + filename)
    #         exit()
            
            image, npix = TimepixToExposure_binary(path + filename, xmin, xmax, ymin, ymax)
#             image, npix = TimepixToExposure_binary(path + filename, xmin, xmax, ymin, ymax, mask_pixels=pixel_mask)
            pixels_per_frame_list.append(npix)
            
            if DISPLAY == True and filenum == display_num: ds9.mtv(image)
            
            threshold = afwDetect.Threshold(thresholdValue)
            footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
            footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
            footPrints = footPrintSet.getFootprints()
            
            footprint_pixels = 0
            
            ions_per_frame.append(len(footPrints))
            for footprint in footPrints:
                if DISPLAY and filenum == display_num: displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more
                npix = afwDetect.Footprint.getNpix(footprint)
                cluster_sizes.append(npix)
                footprint_pixels += npix
                
#                 footprint_data = afwDetect.HeavyFootprintF(footprint, maskedImg)
#                 box = footprint.getBBox()
#                 xmin = box.getMinX()
#                 xmax = box.getMaxX() + 1
#                 ymin = box.getMinY()
#                 ymax = box.getMaxY() + 1
#                 data = parent_image.getArray()[ymin:ymax,xmin:xmax]
                
#                 CentroidTimepixCluster(heavy_footprint.data)
            
            
            footprint_pixels_per_frame_list.append(footprint_pixels)
    #         if filenum == display_num: exit()
            if DISPLAY and filenum == display_num:
                arg = 'saveimage jpeg ' + str(OUTPUT_PATH + str(val) + '_example_frame.jpeg') + ' 100'
                ds9.ds9Cmd(arg)
        
        
        histmax = 30
        name = 'cluster_size'
        h1 = ListToHist(cluster_sizes, OUTPUT_PATH + ID + '_cluster_size.png', log_z = False, nbins = histmax-1, histmin = 1, histmax = histmax, name = name)
        
        histmax = 20001#201
        name = 'pixels_per_frame'
        h2 = ListToHist(pixels_per_frame_list, OUTPUT_PATH + ID + '_pixels_per_frame.png', log_z = False, nbins = 100, histmin = 1, histmax = histmax, name = name)
        
        histmax = 20001#20001
        name = 'footprint_pixels_per_frame'
        h4 = ListToHist(footprint_pixels_per_frame_list, OUTPUT_PATH + ID + '_footprint_pixels_per_frame.png', log_z = False, nbins = 100, histmin = 1, histmax = histmax, name = name)
        name = 'footprint_pixels_per_frame_big_bins'
        h5 = ListToHist(footprint_pixels_per_frame_list, OUTPUT_PATH + ID + '_footprint_pixels_per_frame_big_bins.png', log_z = False, nbins = 50, histmin = 1, histmax = histmax, name = name)
        
        histmax = max(ions_per_frame)
        name = 'ions_per_frame'
        h3 = ListToHist(ions_per_frame, OUTPUT_PATH + ID + '_ions_per_frame.png', log_z = False, nbins = (histmax-1), histmin = 1, histmax = histmax, name = name)
        
        h1.Write()
        h2.Write()
        h3.Write()
        h4.Write()
        h5.Write()
        ROOTfile.Close()
        del h1, h2, h3, h4, h5
    
    print '\n***End code***'      