import os
from os import listdir
from os.path import expanduser, join
import numpy as np
import string        
               
from ROOT import TCanvas, TF1, TH1F, TGraph, TFile
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit, ListToHist, ListVsList
from my_functions import *
import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils
import lsst.afw.detection as afwDetect
from lsst.afw.image import makeImageFromArray
import matplotlib.pyplot as pl
import cPickle as pickle

from ROOT import *
import ROOT
gROOT.SetBatch(1) #don't show drawing on the screen along the way



DISPLAY = True

PICKLED = False

# path  = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/4-9-15/100V_TOF/'
# OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/bnl/4-9-15/100V_TOF/'

# path  = '/mnt/hgfs/VMShared/Data/new_sensors/suny_24042015/Run16/'
# OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/suny_24042015/Run16/'


# spatial, exalite?
# path  = '/mnt/hgfs/VMShared/Data/oxford/Day 1/PMT comp/'
# OUTPUT_PATH = '/mnt/hgfs/VMShared/output/oxford/Day 1/PMT comp/'

# vmi, P47
# path  = '/mnt/hgfs/VMShared/Data/oxford/Day 4/Run 2/'
# OUTPUT_PATH = '/mnt/hgfs/VMShared/output/oxford/Day 4/Run 2/'


# path  = '/mnt/hgfs/VMShared/Data/new_sensors/oxford/march_2015/E404_50nm_20150326/'
# OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/oxford/march_2015/E404_50nm_20150326/'

path  = '/mnt/hgfs/VMShared/Data/new_sensors/suny_24042015/Run15/'
OUTPUT_PATH = '/mnt/hgfs/VMShared/output/new_sensor_profiling/suny_24042015/Run15/'



xmin = 1
ymin = 1
xmax = 254
ymax = 254



if __name__ == '__main__':
    if not PICKLED:
        if not os.path.isfile(OUTPUT_PATH + 'raw_xyt.pickle'): Combine_and_pickle_dir(path, OUTPUT_PATH + 'raw_xyt.pickle')
        
        if DISPLAY:
            try:
                ds9.initDS9(False)
            except ds9.Ds9Error:
                print 'DS9 launch bug error thrown away (probably)'
    
    
#         OpenTimepixInDS9(path + '1_0100.txt')
# #         ds9.ds9Cmd('scale limits 7490 7510')
# #         ds9.ds9Cmd('scale limits 9750 9850')
#         ds9.ds9Cmd('scale limits 9750 9850')
#         ds9.ds9Cmd('cmap rainbow')
#         exit()
    
    
        data_array = Load_XYT_pickle(OUTPUT_PATH + 'raw_xyt.pickle')
        histmin = 9800
        histmax = 9850
        xrange = [1,240]
        yrange = [1,240]
#         xrange = [1,130]
#         yrange = [65,203]
         
#         histmin = 7490
#         histmax = 7510
        max_entries = 1e8
        hist_range = histmax - histmin

        index = np.where(data_array[:,0]<=xrange[1])
        data_array = data_array[index]
        index = np.where(data_array[:,0]>=xrange[0])
        data_array = data_array[index]
        
        index = np.where(data_array[:,1]<=yrange[1])
        data_array = data_array[index]
        index = np.where(data_array[:,1]>=yrange[0])
        data_array = data_array[index]
         
        index = np.where(abs(data_array[:,2]-histmin-hist_range/2.)<=hist_range/2.)
        print'loaded'
        data = data_array[index,2].flatten()[0:min(max_entries,len(data_array[index,2].flatten()))]
        rms = np.std(data)
        print "rms = %.3f"%rms
        print "(FWHM = %.3f)"%(2.355*rms)
        h1 = ListToHist(data, OUTPUT_PATH + 'ToF_ROI.png', log_y = False, nbins = hist_range, histmin = histmin, histmax = histmax, name = 'ToF', fit_gaus = False, fit_to_percentage_of_peak=5, draw_fit_stats=False)
        h1 = ListToHist(data, OUTPUT_PATH + 'ToF_ROI_log.png', log_y = True, nbins = hist_range, histmin = histmin, histmax = histmax, name = 'ToF', fit_gaus = False, fit_to_percentage_of_peak=5, draw_fit_stats=False)
  
        from root_functions import GetLeftRightBinsAtPercentOfMax, GetLastBinAboveX, GetFirstBinBelowX
        maxbin = h1.GetMaximumBin()
        maxbinvalue = h1.GetBinContent(maxbin)
        maxbincenter = h1.GetBinCenter(maxbin)
        print maxbin
        print maxbinvalue
        print maxbincenter


        dummy, ninety = GetLastBinAboveX(h1,0.9*maxbinvalue)
        dummy, ten = GetLastBinAboveX(h1,0.1*maxbinvalue)
	print ten
	print type(ten)        
	print "10-90% time = %s timecodes = ns"%ninety
	#print "Found %s footprints in %s"%(filename)
	exit()

        
#         Make3DScatter(data_array[:,0],data_array[:,1], data_array[:,2], tmin=histmin, tmax=histmax, savefile='')
  
#         image = XYT_to_image(data_array[index], True)
        image = XYT_to_image(data_array, True)
#         XYT_to_image(data_array, True)
        print'done'
        exit()
        
        
        
#         PMT_xs, PMT_ys = ReadBNL_PMTWaveform('/mnt/hgfs/VMShared/Data/new_sensors/bnl/4-9-15/TOF_04-09-15_o2_ethylene')
#         ListVsList(PMT_xs*-1e6, PMT_ys, OUTPUT_PATH + 'PMT.png', xmin=-21, xmax = -16, xtitle='Time (ns)', setlogy = False, marker_style=9, marker_color = 1, marker_size = 0.5, plot_opt = 'AP')#, ymin, ymax, marker_color, set_grid)
#         ListVsList(PMT_xs*-1e6, PMT_ys, OUTPUT_PATH + 'PMT_other.png', xmin=-15, xmax = -10, xtitle='Time (ns)', setlogy = False, marker_style=9, marker_color = 1, marker_size = 0.5, plot_opt = 'AP')#, ymin, ymax, marker_color, set_grid)
#         ListVsList(PMT_xs*-1e6, PMT_ys, OUTPUT_PATH + 'PMT_all.png', xmin=0, xmax = -250, xtitle='Time (ns)', setlogy = False, marker_style=9, marker_color = 1, marker_size = 0.5, plot_opt = 'AP')#, ymin, ymax, marker_color, set_grid)
    
    
    
#         OpenTimepixInDS9(path + 'eight_0003.txt')
# #         ds9.ds9Cmd('scale limits 6400 6600')
#         ds9.ds9Cmd('scale limits 7490 7510')
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
                if footprintnum>=50: exit()
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
                    x,y,t,chisq = CentroidTimepixCluster(data, fit_function = 'p2', save_path='/mnt/hgfs/VMShared/temp/3D_cluster_fits/'+str(footprintnum)+'.png')
                    x += bbox_xmin
                    y += bbox_ymin
#                     if chisq < 1.2:
#                         centroided_timecodes.append(t-OFFSET)
#                         max_timecode_list.append(GetMaxClusterTimecode(data) - OFFSET)
#                      
#                     for value in GetAllTimecodesInCluster(data):
#                         all_cluster_timecodes.append(value-OFFSET)
             
                ####next footprint
        ####next file

     
        pickle.dump(max_timecode_list,      open(max_timecodes_pickle,  'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(all_cluster_timecodes,  open(all_cluster_pickle,    'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(centroided_timecodes,   open(p4_timecodes_pickle, 'wb'), pickle.HIGHEST_PROTOCOL)
#         print 'done'
#         exit()
    
    
    
    
    
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
   
    
    
    
    
    
    
    
    
    
    
