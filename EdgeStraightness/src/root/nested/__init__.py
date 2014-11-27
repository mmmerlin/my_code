from __builtin__ import str, range, len # why does it put these in when that is unnecessary?!
from os.path import expanduser, isfile
from os import listdir
import time
from time import sleep

import lsst.afw.detection     as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.meas.algorithms   as measAlg
import lsst.afw.image         as afwImg
import lsst.afw.display.ds9   as ds9


from ROOT import TCanvas, TF1, TH1F, TGraph, TLegend, TGraphErrors, TPaveText
from array import array
import numpy as np
from numpy.core.defchararray import zfill

# my stuff
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit, ListToHist, ListVsList, CANVAS_HEIGHT, CANVAS_WIDTH
from TrackFitting import *
from ImageStat import Stat
import TrackViewer as TV
import TrackFitting
from copy import copy


##########################################################################################
# things that won't really change
OUTPUT_PATH = "/mnt/hgfs/VMShared/output/edge_straightness/"
FILE_TYPE = ".pdf"
N_AMPS = 16

############

DISPLAY_LEVEL = 0
QUIET = False
PROCESS_FILE_LIMIT = None
#PROCESS_FILE_LIMIT = 1

# Track finding options
THRESHOLD = 50
N_PIX_MIN = 1
GROW = 1
ISOTROPIC = False

# Cut options
TRACK_LENGTH_CUT = 150
ELLIPTICITY_CUT  = 3
CHISQ_CUT        = 10
R2_CUT           = 0.8


GLOBAL_OUT = []



def Cut_Length(stat, cut):
    if stat.length_true_um >= cut:
        return True
    else:
        return False
def Cut_Ellipticity(stat, cut):
    if stat.ellipse_b == 0:
        return False
    
    ratio = stat.ellipse_a / stat.ellipse_b
    if ratio >= cut:
        return True
    else:
        return False
def Cut_Chisq(stat, cut):
    if stat.LineOfBestFit.chisq_red == -1: return False
    if stat.LineOfBestFit.chisq_red / stat.diagonal_length_pixels <= 0.001: return False
    if stat.LineOfBestFit.chisq_red / stat.diagonal_length_pixels >= cut:
        return False
    else:
        return True
    

def Cut_GetEdgeTracks(stat):
    edge_sum = stat.bottom_track + stat.top_track + stat.left_track + stat.right_track
    if edge_sum > 0:
        return True
    else:
        return False
    
def Cut_GetMidlineTracks(stat):
    if stat.midline_track == True:
        return True
    else:
        return False
    
def Cut_R2(stat, cut):
    if stat.LineOfBestFit.R2 <= cut:
        return False
    else:
        return True

if __name__ == '__main__':
    start_time = time.time()
    import cPickle as pickle
    print "Running PSF Calculator\n"

    cosmic_pickle_file = '/mnt/hgfs/VMShared/output/datasets/edge_tracks_200thr_gr2_px2_gain_corrected'
#     cosmic_pickle_file = '/mnt/hgfs/VMShared/output/datasets/all_cosmics_with_data'
#     cosmic_pickle_file = '/mnt/hgfs/VMShared/output/datasets/clean_cosmics_L400_R095_D500'
    
    t0 = time.time()
    all_tracks = pickle.load(open(cosmic_pickle_file, 'rb'))
    dt = time.time() - t0
    print "%s tracks unpickled in %.2f seconds" %(len(all_tracks),dt) 
    
    top_tracks = []
    bottom_tracks = []
    left_tracks = []
    right_tracks = []
    edge_tracks = []
    midline_tracks = []
    
    nstats = 0
    rawstats = len(all_tracks)
    
    discs = []
    all_tracks_temp = []

    ###################################################
####     Applying cuts, optionally re-saving dataset
    n_post_cut = 0
    for stat in all_tracks:
        if stat.length_true_um < 200: continue
        if stat.discriminator > 2000: continue
        
        n_post_cut += 1
        all_tracks_temp.append(stat)
        
        if stat.left_track == True:
            left_tracks.append(stat)            
        if stat.right_track == True:
            right_tracks.append(stat)            
        if stat.top_track == True:
            top_tracks.append(stat)            
        if stat.bottom_track == True:
            bottom_tracks.append(stat)            
        if stat.midline_track == True:
            midline_tracks.append(stat)      

    all_tracks = all_tracks_temp #remove cut tracks from the all_track dataset
       
    n_left = len(left_tracks)
    n_right = len(right_tracks)    
    n_top = len(top_tracks)    
    n_bottom = len(bottom_tracks)    
    n_midline = len(midline_tracks)      
    
    print "Total post cuts = %s" %n_post_cut
    print "left",   n_left
    print "right",  n_right
    print "top",    n_top
    print "bottom", n_bottom
    print "middle", n_midline
        
        
    ListToHist([stat.discriminator for stat in all_tracks], OUTPUT_PATH + 'discs.png', histmin = 0, histmax = 5000, nbins = 50)#, log_z, nbins, histmin, histmax)
    ListToHist([stat.LineOfBestFit.R2 for stat in all_tracks],OUTPUT_PATH + 'r2.png', histmin = 0, histmax = 1.1, nbins = 50)
    ListToHist([stat.npix for stat in all_tracks], OUTPUT_PATH + 'npix.png', histmin = 0, histmax = 1000, nbins = 100)
  
 
    for i,stat in enumerate(all_tracks):
        legend_text = []
        legend_text.append('R^{2} = ' + str(round(stat.LineOfBestFit.R2,5)))
        legend_text.append('Chisq = ' + str(stat.LineOfBestFit.chisq_red))
        legend_text.append('Disc = ' + str(round(stat.discriminator,0)))
        legend_text.append(TrackFitting.GetEdgeType(stat))
        TV.TrackToFile_ROOT_2D_3D(stat.data, OUTPUT_PATH + 'tracks/' + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
    
    
    exit()
        
        
        
        
#         
#         
#         
#     #get new coefficients as distance to line uses straight line of form ax + by + c = 0
#     a = -1. * fitted_line.a
#     b = 1
#     c = -1. * fitted_line.b
#     
#     histmin = -1 * max(data.shape[0], data.shape[1])
#     histmax = max(data.shape[0], data.shape[1])
#     nbins = (histmax - histmin) * 2
#     
#     discriminator = 0
#     for xcoord in range(data.shape[0]):
#         for ycoord in range(data.shape[1]):
#             x = xcoord + 0.5 #adjust for bin centers - NB This is important!
#             y = ycoord + 0.5 #adjust for bin centers - NB This is important!
#             value = float(data[xcoord,ycoord])
#             distance = abs(a*x + b*y + c) / (a**2 + b**2)**0.5
#             try:
#                 discriminator += value * (math.e**(distance))
#             except:
#                 discriminator = 1e324
#                 return discriminator
#     discriminator /= ((data.shape[0])**2 + (data.shape[1])**2)**0.5        
#     
#         
#         
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    exit()
    
    





    ######################################################
    nsecs = 6 #3,5,9 
    
    xpoints, sigmas, sigma_errors = [], [], []
    av_sigma = [0.] * nsecs
    av_sigma_error = [0.] * nsecs
    npts = 0
    
    savepath = '/home/mmmerlin/output/PSF/'
    for i,stat in enumerate(post_cuts): 
        xs,s,se = MeasurePSF_in_Sections(stat.data, stat.LineOfBestFit, nsecs, tgraph_filename=savepath + str(i) + '.png')
        assert nsecs == len(xs) or len(xs) == 0
        for j in range(len(xs)):
            xpoints.append(xs[j])
            sigmas.append(s[j])
            sigma_errors.append(se[j])
            av_sigma[j] += s[j]
            av_sigma_error[j] += se[j]**2
        npts += 1
    
    for j in range(nsecs): #make averages into averages
        av_sigma[j] /= float(npts)
        av_sigma_error[j] = (av_sigma_error[j]/float(npts))**0.5

    
    
    for i,stat in enumerate(some_list):
#        if i <> 3: continue
        legend_text = []
        legend_text.append('R^{2} = ' + str(round(stat.LineOfBestFit.R2,5)))
        legend_text.append('Disc = ' + str(round(stat.discriminator,0)))
        legend_text.append('Chisq = ' + str(stat.LineOfBestFit.chisq_red))
        TV.TrackToFile_ROOT_2D_3D(stat.data, savepath + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
    
    
    
    
    
       
#    ListVsList([stat.LineOfBestFit.R2 for stat in rawlist], [stat.LineOfBestFit.chisq_red for stat in rawlist],  '/home/mmmerlin/output/PSF/r2_vs_chisq.pdf', xmax = 1)
        
    exit()




############## END CODE ##############
    
    all_time = time.time() - start_time
    for line in GLOBAL_OUT:
        print line
    print "All analysis done in %.2f seconds" %all_time 
    exit()
    
############# DONE ################
    
