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
import lsst.afw.detection as afwDetect
from root_functions import ListToHist, ListVsList
from lsst.afw.image import makeImageFromArray
import matplotlib.pyplot as pl
import cPickle as pickle
from time import sleep

from ROOT import *
import ROOT
gROOT.SetBatch(1) #don't show drawing on the screen along the way


from image_assembly import AssembleImage

DISPLAY = True

PICKLED = False

# path  = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/4-9-15/100V_TOF/'
# path  = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015//'
path  = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/4-9-15/100V_good_trigger/'
# OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/bnl/4-9-15/100V_good_trigger/'
OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/bnl/4-9-15/100V_TOF/'

all_cluster_pickle    = OUTPUT_PATH + 'pickles/all_cluster_timecodes.pickle'
min_timecodes_pickle  = OUTPUT_PATH + 'pickles/min.pickle'
max_timecodes_pickle  = OUTPUT_PATH + 'pickles/max.pickle'
p2_timecodes_pickle   = OUTPUT_PATH + 'pickles/p2.pickle'
p4_timecodes_pickle   = OUTPUT_PATH + 'pickles/p4.pickle'
gaus_timecodes_pickle = OUTPUT_PATH + 'pickles/gaus.pickle'


xmin = 1
ymin = 1
xmax = 254
ymax = 254

GLOBAL_OUT = []

OFFSET = 0

all_cluster_timecodes = []
cluster_sizes = []
min_timecode_list = []
max_timecode_list = []
p2_timecodes = []
p4_timecodes = []
gaus_timecodes = []
centroided_timecodes = []


if __name__ == '__main__':
    if not PICKLED:
#         Combine_and_pickle_dir(path, OUTPUT_PATH + 'raw_xyt.pickle')
#         exit()
        
        if DISPLAY:
            try:
                ds9.initDS9(False)
            except ds9.Ds9Error:
                print 'DS9 launch bug error thrown away (probably)'
    
    
#         data_array = Load_XYT_pickle(OUTPUT_PATH + 'raw_xyt.pickle')
#         histmin = 7490
#         histmax = 7510
#         hist_range = histmax - histmin
#         index = np.where(abs(data_array[:,2]-histmin-hist_range/2.)<=hist_range/2.)
#         print'loaded'
# #         h1 = ListToHist(data_array[index,2].flatten(), OUTPUT_PATH + 'ToF_peaks.png', log_y = False, nbins = hist_range, histmin = histmin, histmax = histmax, name = 'ToF')
#         image = XYT_to_image(data_array[index], True)
# #         XYT_to_image(data_array, True)
#         print'done'
#         exit()
        
        
        
#         PMT_xs, PMT_ys = ReadBNL_PMTWaveform('/mnt/hgfs/VMShared/Data/new_sensors/bnl/4-9-15/TOF_04-09-15_o2_ethylene')
#         ListVsList(PMT_xs*-1e6, PMT_ys, OUTPUT_PATH + 'PMT.png', xmin=-21, xmax = -16, xtitle='Time (ns)', setlogy = False, marker_style=9, marker_color = 1, marker_size = 0.5, plot_opt = 'AP')#, ymin, ymax, marker_color, set_grid)
#         ListVsList(PMT_xs*-1e6, PMT_ys, OUTPUT_PATH + 'PMT_other.png', xmin=-15, xmax = -10, xtitle='Time (ns)', setlogy = False, marker_style=9, marker_color = 1, marker_size = 0.5, plot_opt = 'AP')#, ymin, ymax, marker_color, set_grid)
#         ListVsList(PMT_xs*-1e6, PMT_ys, OUTPUT_PATH + 'PMT_all.png', xmin=0, xmax = -250, xtitle='Time (ns)', setlogy = False, marker_style=9, marker_color = 1, marker_size = 0.5, plot_opt = 'AP')#, ymin, ymax, marker_color, set_grid)
    
    
    
#         OpenTimepixInDS9(path + 'eight_0003.txt')
#         ds9.ds9Cmd('scale limits 6400 6600')
#         exit()
         
        
        
        thresholdValue = 1
        npixMin = 1
        grow = 0
        isotropic = False
    
        display_num = 0
        for filenum, filename in enumerate(os.listdir(path)):
#             if filenum >10: continue
            if filenum%10==0: print 'Processing %s'%filenum
    
            image = TimepixToExposure(path + filename, xmin, xmax, ymin, ymax)
            if DISPLAY == True and filenum == display_num: ds9.mtv(image)
            
            threshold = afwDetect.Threshold(thresholdValue)
            footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
            footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
            footPrints = footPrintSet.getFootprints()
#             print "Found %s footprints in %s"%(len(footPrints), filename)
            
            footprint_pixels = 0
            for footprintnum, footprint in enumerate(footPrints):
                if footprintnum>=100: exit()
#                 if DISPLAY and filenum == display_num: displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more
                npix = afwDetect.Footprint.getNpix(footprint)
#                 if npix >1:cluster_sizes.append(npix)
                
                if npix >= 4:
                    box = footprint.getBBox()
                    bbox_xmin = box.getMinX()
                    bbox_xmax = box.getMaxX() + 1
                    bbox_ymin = box.getMinY()
                    bbox_ymax = box.getMaxY() + 1
                      
                    data = image.getArray()[bbox_ymin:bbox_ymax,bbox_xmin:bbox_xmax]        
                    centroid_x, centroid_y = footprint.getCentroid()
                    x,y,t,chisq = CentroidTimepixCluster(data, fit_function = 'gaus', save_path='/mnt/hgfs/VMShared/temp/3D_cluster_fits/'+str(footprintnum)+'.png')
                    x += bbox_xmin
                    y += bbox_ymin
                    if chisq < 1.2:
                        centroided_timecodes.append(t-OFFSET)
                        max_timecode_list.append(GetMaxClusterTimecode(data) - OFFSET)
                    
                    for value in GetAllTimecodesInCluster(data):
                        all_cluster_timecodes.append(value-OFFSET)
             
                ####next footprint
        ####next file

     
        pickle.dump(max_timecode_list,      open(max_timecodes_pickle,  'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(all_cluster_timecodes,  open(all_cluster_pickle,    'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(centroided_timecodes,   open(p4_timecodes_pickle, 'wb'), pickle.HIGHEST_PROTOCOL)
#         print 'done'
#         exit()
    
    
    
    
    
    else:
        for item in pickle.load(open(all_cluster_pickle, 'rb')):
            all_cluster_timecodes.append(item)
        for item in pickle.load(open(max_timecodes_pickle, 'rb')):
            max_timecode_list.append(item)
        for item in pickle.load(open(gaus_timecodes_pickle, 'rb')):
            gaus_timecodes.append(item)

        for item in pickle.load(open(p2_timecodes_pickle, 'rb')):
            p2_timecodes.append(item)
        for item in pickle.load(open(p4_timecodes_pickle, 'rb')):
            p4_timecodes.append(item)
  
#     for i, value in enumerate(gaus_timecodes):
#         print i,value


#     histmax = 60
#     name = 'cluster_sizes'
#     h1 = ListToHist(cluster_sizes, OUTPUT_PATH + 'cluster_sizes.png', log_y = False, nbins = (histmax-1), histmin = 0, histmax = histmax, name = name)
    
    
    
    
    histmin = 2500
    histmax = 2700
    nbins = 100
    threshold = 25
    log = True
    fit = False
    
#     name = 'min_timecode'
#     h1 = ListToHist(min_timecode_list, OUTPUT_PATH + 'min_timecode.png', log_y = True, nbins = nbins, histmin = 0, histmax = histmax, name = name, fit_gaus = True, fit_to_percentage_of_peak = threshold)
    
    name = 'max_timecode'
    h2 = ListToHist(max_timecode_list, OUTPUT_PATH + 'max_timecode.png', log_y = log, nbins = nbins, histmin = histmin, histmax = histmax, name = name, fit_gaus = fit, fit_to_percentage_of_peak = threshold)
   
    name = 'all_cluster_timecodes'
    h3 = ListToHist(all_cluster_timecodes, OUTPUT_PATH + 'all_cluster_timecodes.png', log_y = log, nbins = nbins, histmin = histmin, histmax = histmax, name = name, fit_gaus = fit, fit_to_percentage_of_peak = threshold)
      
    name = 'p2_timecodes'
    h4 = ListToHist(p2_timecodes, OUTPUT_PATH + 'p2_timecodes.png', log_y = log, nbins = nbins, histmin = histmin, histmax = histmax, name = name, fit_gaus = fit, fit_to_percentage_of_peak = threshold)
    
    name = 'p4_timecodes'
    h5 = ListToHist(p4_timecodes, OUTPUT_PATH + 'p4_timecodes.png', log_y = log, nbins = nbins, histmin = histmin, histmax = histmax, name = name, fit_gaus = fit, fit_to_percentage_of_peak = threshold)
    
    name = 'gaus_timecodes'
    h6 = ListToHist(gaus_timecodes, OUTPUT_PATH + 'gaus_timecodes.png', log_y = log, nbins = nbins, histmin = histmin, histmax = histmax, name = name, fit_gaus = fit, fit_to_percentage_of_peak = threshold)
  
    
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