import lsst.afw.detection   as afwDetect
import lsst.afw.display.utils as displayUtils
from lsst.meas.algorithms.detection import (SourceDetectionTask, estimateBackground, BackgroundConfig,)
import lsst.meas.algorithms as measAlg

import numpy as np
import lsst.afw.image       as afwImg
import lsst.afw.display.ds9 as ds9

from os.path import expanduser

from TrackFitting import *
import TrackFitting

from timeit import itertools
import time
from image_assembly import AssembleImage

#t0 = time.time()
#dt = time.time() - t0
#print "Time was %.2f seconds" %dt 


#===============================================================================


def DoAnalysis(input_path, SINGLE_FILE = True, SPECIFIC_FILE = None, SINGLE_POINT = False):
    thresholdValue = 50
    npixMin = 2
    grow = 0
    isotropic = False
    
    from image_assembly import AssembleImage, MakeBiasImage, GetImage_SingleAmp
    from os import listdir
    from os.path import isfile
    
    if DISPLAY_LEVEL >= 1:
        try: # initialise DS9, deal with a bug in its launching
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'
        print 'called ds9 to display' 
#= Open image, assemble, background subtract ===============================================================
    
    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'
    
    dircontents = listdir(input_path)
    file_list = []
    for thisfile in dircontents:
        filename = input_path + thisfile
        if str(filename).find('coadded') != -1: continue # skip coadd file
        if isfile(filename): file_list.append(filename) # skip bias dir
    
    if SPECIFIC_FILE != None:
        file_list = []
        file_list.append(SPECIFIC_FILE)
        SINGLE_FILE = True
    
    if not SINGLE_FILE: print "Processing %s files..." %len(file_list)

    nleft, nright, ntop, nbottom, nmidline = 0,0,0,0,0

    statslist = []
    for filename in file_list:
        print "Processing %s..." %filename
        
        image = AssembleImage(filename, metadata_filename, True)# make image, subtract background and assemble exposure
        maskedImg = afwImg.MaskedImageF(image)
        exposure = afwImg.ExposureF(maskedImg)
        
        if DISPLAY_LEVEL >= 1 and SINGLE_FILE == True: ds9.mtv(image)
    
    # = Do finding ====================================================================
        threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
        footPrintSet = afwDetect.FootprintSet(exposure.getMaskedImage(), threshold, "DETECTED", npixMin)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
    
        footPrints = footPrintSet.getFootprints()
    
        if footPrints.size() >= 800: # files with bright defects cause all sorts of problems
            print "Bad file - skipping..."
            continue
    
        for i,footprint in enumerate(footPrints):
            heavy_footprint = afwDetect.HeavyFootprintF(footprint, maskedImg)
            stat = GetTrackStats(heavy_footprint, image, filename, False)
            statslist.append(stat)
            
            if stat.left_track == True:
                print "left track @ track# %s in file %s" %(i,filename)
                nleft += 1
            if stat.right_track == True:
                print "right track @ track# %s in file %s" %(i,filename)
                nright += 1
            if stat.top_track == True:
                print "top track @ track# %s in file %s" %(i,filename)
                ntop += 1
            if stat.bottom_track == True:
                print "bottom track @ track# %s in file %s" %(i,filename)
                nbottom += 1
            if stat.midline_track == True:
                print "midline track @ track# %s in file %s" %(i,filename)
                nmidline += 1
          
        if SINGLE_FILE == True:
            break
        else:
            print '%s footprints found in %s' %(footPrints.size(), filename)
             
    print "nmidline %s" %nmidline
    print "nleft %s" %nleft
    print "nright %s" %nright
    print "ntop %s" %ntop
    print "nbottom %s" %nbottom
#===============================================================================




def DrawStat(stat):
    if stat.ellipse_b == 0:
        ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
        
    argstring = "@:"+str(4*stat.ellipse_Ixx)+','+str(4*stat.ellipse_Ixy)+','+str(4*stat.ellipse_Iyy) #multiply by four just to make it more exaggerated otherwise they all look like cirlces
    ds9.dot(argstring,stat.centroid_x,stat.centroid_y) #ellipse around the centroid
    ds9.dot("x",stat.centroid_x,stat.centroid_y)# cross on the peak
    displayUtils.drawBBox(stat.BBox, borderWidth=0.5) # border to fully encompass the bbox and no more
#    ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
    print 'length (diag,px) = %s, length (3D,true,um) = %s, flux = %s, npix = %s, dedx = %s' %(stat.diagonal_length_pixels, stat.length_true_um, stat.flux, stat.npix, stat.de_dx)


#===============================================================================
#===============================================================================
#===============================================================================


if __name__ == '__main__':
    import pickle
    print "Running center cosmic finder\n"
    DISPLAY_LEVEL = 2
    
    SINGLE_FILE = False
    SINGLE_POINT = False
    SPECIFIC_FILE = None
#    SPECIFIC_FILE = '/home/mmmerlin/Desktop/VMShared/Data/all_darks/113-03_dark_dark_999.00_035_20140709120811.fits'

    home_dir = expanduser("~")
    input_path = home_dir + '/Desktop/VMShared/Data/all_darks/'
#    SPECIFIC_FILE = home_dir + '/Desktop/VMShared/Data/long_darks_20140708/113-03_dark_dark_999.00_035_20140709120811.fits'

#===============================================================================

    if SPECIFIC_FILE != None: SINGLE_FILE = True
    
    DoAnalysis(input_path, SINGLE_FILE, SPECIFIC_FILE=SPECIFIC_FILE, SINGLE_POINT=SINGLE_POINT)
    
    exit()
    
    if DISPLAY_LEVEL > 1 and SINGLE_FILE == True:
        for stat in rawlist:
            DrawStat(stat)



    print '\n*** End code ***'
    exit()
