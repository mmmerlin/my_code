import os
from os.path import expanduser, join
from os import listdir
import numpy as np
import string        
               
from ROOT import TCanvas, TF1, TH1F, TGraph
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import *
from math import floor
import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils
import lsst.afw.detection   as afwDetect
from root_functions import ListToHist, ListVsList
from lsst.afw.image import makeImageFromArray
import matplotlib.pyplot as pl


DISPLAY = True

glitch_threshold = 5000

# old sensor
xmin = 1
ymin = 1
xmax = 254
ymax = 254


OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/'

FILE_TYPE = ".png"

if __name__ == '__main__':
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A2(300nm)/Run5/'
   
    path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A1(50nm_bad_bonds)/Run3/'
    ID = 'A1_run3'
    

#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A3(200nm)/'
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A4(120nm)400thr/'
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/old_sensor/'
#     path     = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/first_light/A5(50nm)/'



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
    
    
    nfiles = len(os.listdir(path))
    
#     intensity_array = MakeCompositeImage_Timepix(path, 1, 255, 1, 255, 0, 9999, -99999, 99999, return_raw_array=True)
    intensity_array = MakeCompositeImage_Timepix(path, 0, 255, 0, 255, 0, 9999, -99999, 99999, return_raw_array=True)
#     ViewIntensityArrayInDs9(intensity_array)
    
    xlist, ylist = [],[]
    for thr_range in range(1,1001):
        badpixel_threshold = (float(thr_range)/1000.)*(nfiles)
        index = np.where(intensity_array <= badpixel_threshold)
        intensity_sum = intensity_array[index].sum(dtype = np.float64)
#         print str(thr_range/10.) + '\t' + str(intensity_sum/nfiles)
        xlist.append(thr_range/10.)
        ylist.append(intensity_sum/nfiles)
    
    fig = pl.figure(figsize = (16,9), dpi = 72)
    pl.subplot(2,1,1)
    pl.xlabel('Bad pixel hit threshold (%)', horizontalalignment = 'right' )
    pl.ylabel('# Hit pixels')
    pl.plot(xlist, ylist)
    pl.subplot(2,1,2)
    xmax_zoom_percentage = 6
    pl.xlim([0,xmax_zoom_percentage])
    pl.ylim([0,1.1*max(ylist[0:xmax_zoom_percentage * 10])])
    pl.plot(xlist, ylist)
    pl.xlabel('Bad pixel hit threshold (%)', horizontalalignment = 'right' )
    pl.ylabel('# Hit pixels')
    fig.savefig(OUTPUT_PATH + ID + '_Turn-on_curve.png')
    
    ListVsList(xlist, ylist, OUTPUT_PATH + ID + '_Turn-on_curve_ROOT.png', xtitle = 'Bad pixel hit threshold (%)', ytitle='# Hit pixels')
    ListVsList(xlist, ylist, OUTPUT_PATH + ID + '_Turn-on_curve_ROOT_0-10.png', xtitle = 'Bad pixel hit threshold (%)', ytitle='# Hit pixels', xmax = xmax_zoom_percentage, ymin=0, ymax = 1.1*max(ylist[0:xmax_zoom_percentage * 10]), set_grid = True)
    exit()


    mask_list = GeneratePixelMaskListFromFileset(path, 0.02)    
    print 'masking %s pixels'%len(mask_list[0])
    pixel_mask = MakeMaskArray(mask_list)
#     ViewMaskInDs9(pixel_mask)
#     exit()
    
    
    thresholdValue = 1
    npixMin = 1
    grow = 0
    isotropic = False
    
    cluster_sizes = []
    pixels_per_frame_list = []
    
    display_num = 10
    for filenum, filename in enumerate(os.listdir(path)):
#         OpenTimepixInDS9(path + filename)
#         exit()
        
#         image, npix = TimepixToExposure_binary(path + filename, xmin, xmax, ymin, ymax)
        image, npix = TimepixToExposure_binary(path + filename, xmin, xmax, ymin, ymax, mask_pixels=pixel_mask)
        pixels_per_frame_list.append(npix)
        
        if DISPLAY == True and filenum == display_num: ds9.mtv(image)
        
        threshold = afwDetect.Threshold(thresholdValue)
        footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
        footPrints = footPrintSet.getFootprints()

        for footprint in footPrints:
            if DISPLAY and filenum == display_num: displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more
            npix = afwDetect.Footprint.getNpix(footprint)
            cluster_sizes.append(npix)
#         if filenum == display_num: exit()
    
    
    histmax = 30
    ListToHist(cluster_sizes, OUTPUT_PATH + ID + '_1-10.png', log_z = False, nbins = histmax-1, histmin = 1, histmax = histmax)
#     ListToHist(cluster_sizes, OUTPUT_PATH + ID + '_2-10.png', log_z = False, nbins = histmax-2, histmin = 2, histmax = histmax)
    
    histmax = 300
    ListToHist(pixels_per_frame_list, OUTPUT_PATH + ID + '_pixel_per_frame.png', log_z = False, nbins = (histmax-1)/10, histmin = 1, histmax = histmax)
    
    
    print '\n***End code***'      