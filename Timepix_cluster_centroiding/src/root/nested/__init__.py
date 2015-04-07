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
import cPickle as pickle

from ROOT import *
import ROOT
gROOT.SetBatch(1) #don't show drawing on the screen along the way



DISPLAY = True

PICKLED = False

path  = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A2(300nm)/Run4/'
#     path  = '/mnt/hgfs/VMShared/Data/Chem_09-06-14/Butanone_2us_delay/'
OUTPUT_PATH = '/mnt/hgfs/VMShared/output/temp/'
all_timecodes_pickle = OUTPUT_PATH + 'raw.pickle'
centroided_timecodes_pickle = OUTPUT_PATH + 'p4.pickle'


xmin = 1
ymin = 1
xmax = 254
ymax = 254

GLOBAL_OUT = []
GLOBAL_OUT_2 = []

OFFSET = 6400

all_timecodes = []
centroided_timecodes = []


if __name__ == '__main__':
    
    if not PICKLED:
        
        if DISPLAY:
            try:
                ds9.initDS9(False)
            except ds9.Ds9Error:
                print 'DS9 launch bug error thrown away (probably)'
    

        
    #     OpenTimepixInDS9(path + '1_0002.txt')
    #     exit()
        
        
    #     thresholdValue = 10
    #     npixMin = 1
    #     grow = 0
    #     isotropic = False
    

        
        display_num = 0
        for filenum, filename in enumerate(os.listdir(path)):
            if filenum%10==0: print 'Processing %s'%filenum
    #         if filename != '1_0002.txt': continue
#             if filenum >= 50: continue
    
    
            thresholdValue = 1
            npixMin = 1
            grow = 0
            isotropic = False
    
    #         print filename
            image = TimepixToExposure(path + filename, xmin, xmax, ymin, ymax)
            if DISPLAY == True and filenum == display_num: ds9.mtv(image)
            
            threshold = afwDetect.Threshold(thresholdValue)
            footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
            footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
            footPrints = footPrintSet.getFootprints()
            
    #         print "Found %s footprints in %s"%(len(footPrints), filename)
            
            footprint_pixels = 0
            for footprintnum, footprint in enumerate(footPrints):
    #             if DISPLAY and filenum == display_num: displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more
                npix = afwDetect.Footprint.getNpix(footprint)
                if npix >= 4:
                    box = footprint.getBBox()
                    bbox_xmin = box.getMinX()
                    bbox_xmax = box.getMaxX() + 1
                    bbox_ymin = box.getMinY()
                    bbox_ymax = box.getMaxY() + 1
                      
                    data = image.getArray()[bbox_ymin:bbox_ymax,bbox_xmin:bbox_xmax]        
                    centroid_x, centroid_y = footprint.getCentroid()
                     
    #                 x,y,t,chisq = CentroidTimepixCluster(data, OUTPUT_PATH + str(footprintnum) + '.png')
                    x,y,t,chisq = CentroidTimepixCluster(data, fit_function = 'p4')
                    x += xmin
                    y += ymin
                    if chisq < 1.2:
                        centroided_timecodes.append(t-OFFSET)
                    
                    for value in GetAllTimecodesInCluster(data):
                        all_timecodes.append(value-OFFSET)
                 
    #                 GLOBAL_OUT.append(str(x) + '\t' + str(y) + '\t' + str(t) + '\t' + str(chisq))
    #                 GLOBAL_OUT_2.append(str(centroid_x) + '\t' + str(centroid_y))# + '\t' + str(image.getArray()[ymin,xmin] ))
                ####next footprint
        ####next file

        pickle.dump(all_timecodes,          open(all_timecodes_pickle,          'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(centroided_timecodes,   open(centroided_timecodes_pickle,   'wb'), pickle.HIGHEST_PROTOCOL)
    else:
        for item in pickle.load(open(all_timecodes_pickle, 'rb')):
            all_timecodes.append(item)
        for item in pickle.load(open(centroided_timecodes_pickle, 'rb')):
            centroided_timecodes.append(item)
    


    
    
    histmax = 400
    name = 'raw_timecodes'
    h1 = ListToHist(all_timecodes, OUTPUT_PATH + 'all_timecodes.png', log_y = True, nbins = (histmax-1), histmin = 1, histmax = histmax, name = name)
      
#     histmax = max(centroided_timecodes)
    histmax = 400
    name = 'centroided_timecodes'
    h1 = ListToHist(centroided_timecodes, OUTPUT_PATH + 'centroided_timecodes_chi_sq_cut.png', log_y = True, nbins = (histmax-1), histmin = 1, histmax = histmax, name = name)
   

#     for line in GLOBAL_OUT:
#         print line
#         
#     print '--------------'
#         
#     for line in GLOBAL_OUT_2:
#         print line
    
    print '\n***End code***'      
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#             if npix >= 9:
#                 print npix
#                 ds9.mtv(image)
#                 displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5)
#                 centroid_x, centroid_y = footprint.getCentroid()
#                 ds9.zoom(100, centroid_x, centroid_y, 0) # use to zoom to a single point
#                 ds9.ds9Cmd('scale log') 
#                 ds9.ds9Cmd('scale limits 4100 4150')
#                 exit()




#         ds9.zoom(100, centroid_x, centroid_y, 0) # use to zoom to a single point
#         ds9.ds9Cmd('scale log') 
#         ds9.ds9Cmd('scale limits 4830 4860')
#         
#         CentroidTimepixCluster(data, OUTPUT_PATH + 'test.png')
#         
#         
#         if filenum == display_num: exit()