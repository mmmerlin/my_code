import os
from os.path import expanduser, join
from os import listdir
import numpy as np
import string        
               
from ROOT import TCanvas, TF1, TH1F, TGraph
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import GetXYTarray_SingleFile, MakeCompositeImage_Timepix
from math import floor
import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils
import lsst.afw.detection   as afwDetect
from root_functions import ListToHist
from lsst.afw.image import makeImageFromArray


def TimepixToExposure_binary(filename, xmin, xmax, ymin, ymax, mask_pixels):
#     from lsst.afw.image import makeImageFromArray

    data = np.loadtxt(filename)

    my_array = np.zeros((256,256), dtype = np.int32)
    
    if data.shape == (0,):
        my_image = makeImageFromArray(my_array)
        
    elif data.shape == (3,):
        x = data[0] 
        y = data[1] 
        t = data[2]
        
        if x >= xmin and x <= xmax and y >= ymin and y <= ymax:
#             if include_index[y][x] == 0:
        
            my_array[y,x] = 1
      
        my_image = makeImageFromArray(my_array)
    
    else:   
        x = data[:, 0] 
        y = data[:, 1] 
        t = data[:, 2]
    
        for pointnum in range(len(x)):
            if x[pointnum] >= xmin and x[pointnum] <= xmax and y[pointnum] >= ymin and y[pointnum] <= ymax:
#                 if include_index[y][x] == 0:
                my_array[y[pointnum],x[pointnum]] = 1
            
        my_image = makeImageFromArray(my_array)
    
#     out_image = np.zeros((256,256), dtype = np.int32)
#     out_image[include_index] = my_image[include_index]
#     my_image = my_image[include_index]
    
    return my_image#[include_index]

def MakeMaskArray(mask_list):
    mask_array = np.ones((256,256), dtype = np.int32)
    
    for i in range(len(mask_list[0])):
        y = mask_list[0][i]
        x = mask_list[1][i]
        mask_array[y][x] = 0
    
    return mask_array


DISPLAY = True

glitch_threshold = 5000

# old sensor
xmin = 1
ymin = 1
xmax = 254
ymax = 254


OUTPUT_PATH = '/mnt/hgfs/VMShared/output/chem_new_sensors_first_light/'
OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/'

FILE_TYPE = ".png"

if __name__ == '__main__':
#     path     = '/mnt/hgfs/VMShared/Data/chem_new_sensors_first_light/old_sensor/'
#     path     = '/mnt/hgfs/VMShared/Data/chem_new_sensors_first_light/7343-4(120nm)400thr/'
#     path     = '/mnt/hgfs/VMShared/Data/chem_new_sensors_first_light/7343-2(200nm)/'
#     path     = '/mnt/hgfs/VMShared/Data/chem_new_sensors_first_light/7343-6(50nm)/'

#     path     = '/mnt/hgfs/VMShared/Data/new_senors/7153-6(300nm)/Run1/'
#     path     = '/mnt/hgfs/VMShared/Data/new_senors/7343-6(50nm_bad_bonds)/'
#     path     = '/mnt/hgfs/VMShared/Data/new_senors/OLD_SENSOR_1/'
#     path     = '/mnt/hgfs/VMShared/Data/new_senors/OLD_SENSOR_2/Run3/'
#     path = '/mnt/hgfs/VMShared/Data/new_senors/7153-6(300nm)/Run1/'

    path     = '/mnt/hgfs/VMShared/Data/temp/temp/'

    
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
     
     
    intensity_array = MakeCompositeImage_Timepix(path, 1, 253, 1, 253, 0, 9999, -99999, 99999, return_raw_array=True)
    nfiles = len(os.listdir(path))
#     intensity_array /= float(nfiles)
    mask_pixels = np.where(intensity_array >= 0.03*(nfiles))
    print mask_pixels
    for element in mask_pixels:
        print element
        
    print mask_pixels
    print intensity_array[187][19]
    
    mask = MakeMaskArray(mask_pixels)
    intensity_array *= mask
    
    ds9.mtv(makeImageFromArray(intensity_array))
    exit()
    
    
    
      
    for thr_range in range(1,1001):
        badpixel_threshold = (float(thr_range)/1000.)*(nfiles)
        index = np.where(intensity_array <= badpixel_threshold)
        intensity_sum = intensity_array[index].sum(dtype = np.float64)
#         print str(thr_range/10.) + '\t' + str(intensity_sum/nfiles)
     
    mask_pixels = np.where(intensity_array >= 0.03*(nfiles))
    print 'done'
    exit()
#     index = np.where(intensity_array <= 0.03*(nfiles))
    index = np.where(intensity_array <= 0.03*(nfiles))



    if DISPLAY:
        try:
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'

    
    thresholdValue = 1
    npixMin = 1
    grow = 0
    isotropic = False
    
    cluster_sizes = []
    
    display_num = 5
    for filenum, filename in enumerate(os.listdir(path)):
        image = TimepixToExposure_binary(path + filename, xmin, xmax, ymin, ymax, mask_pixels=mask_pixels)

        if DISPLAY == True and filenum == display_num: ds9.mtv(image)
        
        threshold = afwDetect.Threshold(thresholdValue)
        footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
        footPrints = footPrintSet.getFootprints()

        for footprint in footPrints:
            if DISPLAY and filenum == display_num: displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more
            npix = afwDetect.Footprint.getNpix(footprint)
            cluster_sizes.append(npix)
#         print cluster_sizes
        if filenum == display_num: exit()
    
    
    histmax = 25
#     filename = '7153-6(300nm)_Run1'
    filename = 'test'
    ListToHist(cluster_sizes, OUTPUT_PATH + filename + '_1-20.png', log_z = False, nbins = histmax-1, histmin = 1, histmax = histmax)
    ListToHist(cluster_sizes, OUTPUT_PATH + filename + '_2-20.png', log_z = False, nbins = histmax-2, histmin = 2, histmax = histmax)
    
    
    
    print '\n***End code***'      