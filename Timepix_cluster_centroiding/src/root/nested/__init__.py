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

from ROOT import *
import ROOT
gROOT.SetBatch(0) #don't show drawing on the screen along the way


from my_functions import CentroidTimepixCluster

DISPLAY = True


xmin = 1
ymin = 1
xmax = 254
ymax = 254




if __name__ == '__main__':
    if DISPLAY:
        try:
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'

    
    
    
    path  = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A2(300nm)/Run4/'
    OUTPUT_PATH = '/mnt/hgfs/VMShared/output/temp/'
    
    
    rootfilename = OUTPUT_PATH + 'temp.root'
#         ROOTfile = TFile.Open(rootfilename, "RECREATE")

    
    thresholdValue = 1
    npixMin = 2
    grow = 0
    isotropic = False
    
    display_num = 0
    for filenum, filename in enumerate(os.listdir(path)):
        image = TimepixToExposure(path + filename, xmin, xmax, ymin, ymax)
        if DISPLAY == True and filenum == display_num: ds9.mtv(image)
        
        threshold = afwDetect.Threshold(thresholdValue)
        footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
        footPrints = footPrintSet.getFootprints()
        
        footprint_pixels = 0
        
        for footprint in footPrints:
            if DISPLAY and filenum == display_num: displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more
#                 npix = afwDetect.Footprint.getNpix(footprint)
            
#                 footprint_data = afwDetect.HeavyFootprintF(footprint, maskedImg)
#                 box = footprint.getBBox()
#                 xmin = box.getMinX()
#                 xmax = box.getMaxX() + 1
#                 ymin = box.getMinY()
#                 ymax = box.getMaxY() + 1
#                 data = parent_image.getArray()[ymin:ymax,xmin:xmax]
            
#         from TrackFitting import *
        
        box = footprint.getBBox()
        xmin = box.getMinX()
        xmax = box.getMaxX() + 1
        ymin = box.getMinY()
        ymax = box.getMaxY() + 1
        
        data = image.getArray()[ymin:ymax,xmin:xmax]        
        centroid_x, centroid_y = footprint.getCentroid()
        
        ds9.zoom(100, centroid_x, centroid_y, 0) # use to zoom to a single point
        ds9.ds9Cmd('scale log')
        ds9.ds9Cmd('scale limits 6540 6570')
        CentroidTimepixCluster(data, OUTPUT_PATH + 'test.png')
        
        from root_functions import *
        
        
        if filenum == display_num: exit()
    
    
    print '\n***End code***'      