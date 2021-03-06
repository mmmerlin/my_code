import os
from os.path import expanduser, join
from os import listdir
import numpy as np
import string        
               
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


data_path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Vacuum_gauge/'
out_path = '/mnt/hgfs/VMShared/output/DESY/2015_june/cluster/'


if __name__ == '__main__':
    if DISPLAY:
        try:
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'

        
        
        #########################################
#         nfiles = len(os.listdir(data_path))
#           
#         intensity_array = MakeCompositeImage_Timepix(data_path, 0, 255, 0, 255, 0, 9999, -99999, 99999, return_raw_array=True)
#         print out_path + 'composite.jpeg'
# #         ViewIntensityArrayInDs9(intensity_array, savefile=out_path +'composite.jpeg')
# #         exit()
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
#         fig.savefig(out_path + '_Turn-on_curve.png')
            
        
        
        mask_list = GeneratePixelMaskListFromFileset(data_path, 0.1, file_limit=99999)  
        pixel_mask = MakeMaskArray(mask_list)  
        print 'masking %s pixels'%len(mask_list[0])


    
#         ViewIntensityArrayInDs9(-1*(pixel_mask-1), savefile=OUTPUT_PATH + str(val) + '_pixel_mask.jpeg')
#         exit()
###################################################################
        
        thresholdValue = 1
        npixMin = 1
        grow = 0
        isotropic = False
        
        cluster_sizes = []
        pixels_per_frame_list = []
        footprint_pixels_per_frame_list = []
        ions_per_frame = []
        
        display_num = 10
        for filenum, filename in enumerate(os.listdir(data_path)):
            if filenum %100 == 0: print 'Processing file # %s'%filenum
            
#             image, npix = TimepixToExposure_binary(data_path + filename, xmin, xmax, ymin, ymax)
            image, npix = TimepixToExposure_binary(data_path + filename, xmin, xmax, ymin, ymax, mask_pixels=pixel_mask)
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
            
            footprint_pixels_per_frame_list.append(footprint_pixels)
#             if filenum == display_num: exit()
            if DISPLAY and filenum == display_num:
                arg = 'saveimage jpeg ' + str(out_path + str(filenum) + '_example_frame.jpeg') + ' 100'
                ds9.ds9Cmd(arg)
        
        
        histmax = 70
        name = 'cluster_size'
        h1 = ListToHist(cluster_sizes, out_path + 'cluster_size.png', log_y = False, nbins = histmax-1, histmin = 1, histmax = histmax, name = name)
        
#         histmax = 1.2* max(pixels_per_frame_list)
        histmax = 2501
        name = 'pixels_per_frame'
        h2 = ListToHist(pixels_per_frame_list, out_path + 'pixels_per_frame.png', log_y = False, nbins = 50, histmin = 1, histmax = histmax, name = name)
        
        
        histmax = 151
        name = 'ions_per_frame'
        h3 = ListToHist(ions_per_frame, out_path + 'ions_per_frame.png', log_y = False, nbins = 50, histmin = 1, histmax = histmax, name = name)
        
    print '\n***End code***'      
    
    
    
    
    