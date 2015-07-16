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


##########################################################################################
# things that won't really change
OUTPUT_PATH = "/mnt/hgfs/VMShared/output/PSF/"
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
    
def Cut_EdgeTracks(stat):
#    if stat.
        
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
    SINGLE_FILE = False
    SINGLE_POINT = False
    SPECIFIC_FILE = None

    home_dir = expanduser("~")

    cosmic_pickle_file = home_dir + '/output/datasets/all_cosmics_with_data'
    
    t0 = time.time()
    rawlist = pickle.load(open(cosmic_pickle_file, 'rb'))
    dt = time.time() - t0
    print "%s tracks unpickled in %.2f seconds" %(len(rawlist),dt) 
    
    print len(rawlist)
    
    edge_tracks = []
    midline_tracks = []
    
    nstats = 0
    rawstats = 0
    
    TRACK_LENGTH_CUT = 1000
    aspect_limit = 1
    aspect_rejected = 0

    ###################################################
####     Applying cuts, optionally re-saving dataset
    for stat in rawlist:
        rawstats +=1
        
        if Cut_GetEdgeTracks(stat) == True:
            edge_tracks.append(stat)
            continue
        if Cut_GetMidlineTracks(stat) == True:
            midline_tracks.append(stat)
            continue

    midline = rawlist.where()

    
    print len(edge_tracks)
    print len(midline_tracks)
    exit()

    ############################################
    # Generating some plots
    make_n_plots = 0
    savepath = '/home/mmmerlin/output/PSF/'
    for i,stat in enumerate(post_cuts):
        if i >= make_n_plots: break
        legend_text = []
#        legend_text.append('R^{2} = ' + str(round(stat.LineOfBestFit.R2,5)))
#        legend_text.append('Disc = ' + str(round(stat.discriminator,0)))
#        legend_text.append('Chisq = ' + str(stat.LineOfBestFit.chisq_red))
        TV.TrackToFile_ROOT_2D_3D(stat.data, savepath + str(i) + 'both.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
        TV.TrackToFile_ROOT_2D(stat.data, savepath + 'colz_' + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit, plot_opt = 'colz' )
        TV.TrackToFile_ROOT(stat.data, savepath + 'lego20_' + str(i) + '.png', legend_text=legend_text, plot_opt = 'lego2 0' )



    ######################################################
    #do analysis, deal with averaging and compiling return values
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

    
    
    ######################################################
    # All points on top of each other graph
#     c2 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT) 
#     assert len(xpoints) == len(sigmas) == len(sigma_errors)
#     gr = TGraphErrors()
#     for i in range(len(xpoints)):
#         gr.SetPoint(int(i), float(xpoints[i]), float(sigmas[i]))
#         gr.SetPointError(i, float(0), float(sigma_errors[i]))
#     print "Added %s points to PSF Graph"%len(xpoints)
#     gr.SetLineColor(2)
#     gr.SetMarkerColor(2)
#     gr.Draw("AP")
#     gr.GetYaxis().SetTitle('Diffusion #sigma (#mum)')
#     gr.GetXaxis().SetTitle('Av. Si Depth (#mum)')
#     c2.SaveAs(OUTPUT_PATH + '/psf_graph' + '.png')



    ######################################################
    # Averaged points
    c3 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT)
    gr2 = TGraphErrors()
    for i in range(nsecs):
        gr2.SetPoint(int(i), float(xpoints[i]), av_sigma[i])   
        gr2.SetPointError(int(i), float(0), av_sigma_error[i])   
        
    fit_func = TF1("line","[1]*x + [0]", 0,100)
    fit_func.SetNpx(1000)
    gr2.Fit(fit_func, "MEQ", "")
    a = fit_func.GetParameter(1) 
    a_error = fit_func.GetParError(1)
    y_int = fit_func.GetParameter(0) 
    y_int_error = fit_func.GetParError(0)
    R2 = gr2.GetCorrelationFactor()**2
            
    gr2.SetLineColor(2)
    gr2.SetMarkerColor(2)
    gr2.Draw("AP")
    fit_func.Draw("same")
    gr2.GetYaxis().SetTitle('Diffusion #sigma (#mum)')
    gr2.GetXaxis().SetTitle('Av. Si Depth (#mum)')
    
    legend_text = []
    legend_text.append('grad = ' + str(round(a,4)) + ' #pm ' + str(round(a_error,4)))
    legend_text.append('intercept = ' + str(round(y_int,2)) + ' #pm ' + str(round(y_int_error,2)))
    legend_text.append('R^{2} = ' + str(round(R2,3)))
    textbox = TPaveText(0.5,0.25,0.85,0.5,"NDC")
    for line in legend_text: textbox.AddText(line)
    textbox.SetFillColor(0)
    textbox.SetTextSize(1.4* textbox.GetTextSize())
    textbox.Draw("same")
    
    c3.SaveAs(OUTPUT_PATH + '/psf_graph_averaged_' + str(nsecs) + '.png')
 
    ######################################################
    # y-intercept removed in quadrature
    c3 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT)
    gr3 = TGraphErrors()
    for i in range(nsecs):
        gr3.SetPoint(int(i), float(xpoints[i]), (av_sigma[i]**2 - y_int**2)**0.5 )  
        gr3.SetPointError(int(i), float(0), (av_sigma_error[i]**2 + y_int_error**2)**0.5)    
#        gr3.SetPointError(int(i), float(0), abs(av_sigma_error[i]**2 - y_int_error**2)**0.5)    
      
    xmin = 0.
    xmax = 100.
    ymin = 0.
    ymax = float(6.)
    gr_scale_dummy = TGraph()
    gr_scale_dummy.SetPoint(0,xmin,ymin)
    gr_scale_dummy.SetPoint(1,xmax,ymax)
    gr_scale_dummy.SetMarkerColor(0)
    gr_scale_dummy.SetMarkerSize(0)
    gr_scale_dummy.Draw("AP") 
        
#     fit_func_2 = TF1("line","[1]*x + [0]", 0, 100)
    fit_func_2 = TF1("line","TMath::Sqrt([1]*x) + [0]", 0, 100)
#     fit_func_2 = TF1("line","TMath::Sqrt([1]*x)", 0, 100)
    fit_func_2.SetParameter(0,0.1)
    fit_func_2.SetParameter(1,2.0)
    fit_func_2.SetNpx(1000)
    gr3.Fit(fit_func_2, "ME0", "")
    a = fit_func_2.GetParameter(1) 
    a_error = fit_func_2.GetParError(1)
    b = fit_func_2.GetParameter(0) 
    b_error = fit_func_2.GetParError(0)
    R2 = gr3.GetCorrelationFactor()**2
             
    gr3.SetLineColor(4)
    gr3.SetMarkerColor(4)
    fit_func_2.SetLineColor(4)
    gr3.Draw("Psame")
    gr3.GetYaxis().SetTitle('Diffusion #sigma (#mum)')
    gr3.GetXaxis().SetTitle('Av. Si Depth (#mum)')
    gr2.Draw("Psame")
    fit_func.Draw("same")
    fit_func_2.Draw("lsame")
     
    legend_text = []
    legend_text.append('grad = ' + str(round(a,4)) + ' #pm ' + str(round(a_error,4)))
    legend_text.append('intercept = ' + str(round(b,2)) + ' #pm ' + str(round(b_error,2)))
    legend_text.append('R^{2} = ' + str(round(R2,3)))
    textbox = TPaveText(0.5,0.25,0.85,0.45,"NDC")
    for line in legend_text:
        print line
        textbox.AddText(line)
    textbox.SetFillColor(0)
    textbox.SetTextSize(1.4* textbox.GetTextSize())
    textbox.Draw("same")
    
    c3.SaveAs(OUTPUT_PATH + 'psf_graph_averaged_quad_subtracted' + str(nsecs) + '.png')
   
    
    exit()
    
    
#    savepath = '/home/mmmerlin/output/PSF/'
#    i = 0
#    for stat in rawlist:
#        if stat.npix <= 50:
#            i += 1
#            legend_text = []
#            legend_text.append('npix = ' + str(stat.npix))
#            TV.TrackToFile_ROOT_2D(stat.data, savepath + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
#            if i >25: break
#            
    
    for i,stat in enumerate(post_cuts):
#        if i <> 3: continue
        legend_text = []
        legend_text.append('R^{2} = ' + str(round(stat.LineOfBestFit.R2,5)))
        legend_text.append('Disc = ' + str(round(stat.discriminator,0)))
#        legend_text.append('Chisq = ' + str(stat.LineOfBestFit.chisq_red))
#        TV.TrackToFile_ROOT_2D_3D(stat.data, savepath + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
    
    
    
    
    
#    ListToHist([stat.LineOfBestFit.R2 for stat in post_cuts], '/home/mmmerlin/output/PSF/r2_dist.png')
    ListToHist([stat.discriminator for stat in rawlist], '/home/mmmerlin/output/PSF/raw_disc.pdf', histmax = 5000)
    ListToHist([stat.discriminator for stat in post_cuts], '/home/mmmerlin/output/PSF/post_cut_disc.pdf', histmin = 0, histmax = 500, nbins = 50)
    ListToHist([stat.npix for stat in rawlist], '/home/mmmerlin/output/PSF/npx_hist.pdf', histmin = 0, histmax = 100, nbins = 100)
        
#    ListVsList([stat.LineOfBestFit.R2 for stat in rawlist], [stat.LineOfBestFit.chisq_red for stat in rawlist],  '/home/mmmerlin/output/PSF/r2_vs_chisq.pdf', xmax = 1)
        
    exit()




############## END CODE ##############
    
    all_time = time.time() - start_time
    for line in GLOBAL_OUT:
        print line
    print "All analysis done in %.2f seconds" %all_time 
    exit()
    
############# DONE ################
    
