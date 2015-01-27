from __builtin__ import str, range, len # why does it put these in when that is unnecessary?!
from os.path import expanduser, isfile
from os import listdir
import time
from time import sleep

#t0 = time.time()
#dt = time.time() - t0
#print "Time was %.2f seconds" %dt 

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
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from TrackFitting import *


#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import axes3d

##########################################################################################
##########################################################################################
# things that won't really change
OUTPUT_PATH = "/mnt/hgfs/VMShared/output/cosmic_gain/"
FILE_TYPE = ".pdf"
N_AMPS = 16

############

DISPLAY_LEVEL = 0
QUIET = False
#PROCESS_FILE_LIMIT = None
PROCESS_FILE_LIMIT = 50

# Track finding options
THRESHOLD = 50
N_PIX_MIN = 2
GROW = 1
ISOTROPIC = True

# Cut options
TRACK_LENGTH_CUT = 150
ELLIPTICITY_CUT  = 3
CHISQ_CUT        = 10
R2_CUT           = 0.8

# Post processing options
MAKE_LANDAUS = True
MAKE_FE55_SPECTRA = True

GLOBAL_OUT = []


#===============================================================================
def DEBUG(image, footprintset):
    ds9.mtv(image)
    
    for footprint in footprintset:
        from lsst.afw.image.imageLib import MaskedImageF
        masked_imaged = MaskedImageF(image)
        heavy_footprint = afwDetect.HeavyFootprintF(footprint, masked_imaged)
        stat = GetTrackStats(heavy_footprint, image, False)
    
        argstring = "@:"+str(4*stat.ellipse_Ixx)+','+str(4*stat.ellipse_Ixy)+','+str(4*stat.ellipse_Iyy) #multiply by four just to make it more exaggerated otherwise they all look like cirlces
        ds9.dot(argstring,stat.centroid_x,stat.centroid_y) #ellipse around the centroid
        ds9.dot("x",stat.centroid_x,stat.centroid_y)# cross on the peak
        displayUtils.drawBBox(stat.BBox, borderWidth=0.5) # border to fully encompass the bbox and no more
        
#        print "flux = " + str(stat.flux)


def DoAnalysis(input_path, pickle_file, SINGLE_FILE = True, SPECIFIC_FILE = None, SINGLE_POINT = False):
    t0 = time.time()
    total_found = 0
    
    from image_assembly import AssembleImage, MakeBiasImage, GetImage_SingleAmp
    
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
        if str(filename).find('.DS') != -1: continue # skip coadd file
        if isfile(filename): file_list.append(filename) # skip bias dir
    
    if SPECIFIC_FILE != None:
        file_list = []
        file_list.append(SPECIFIC_FILE)
        SINGLE_FILE = True
    
    if not SINGLE_FILE: print "Processing %s files using settings:" %len(file_list)
    print "THRESHOLD = %s" %THRESHOLD
    print "N_PIX_MIN = %s" %N_PIX_MIN
    print "GROW = %s" %GROW
    print "ISOTROPIC = %s" %ISOTROPIC

    amplist = []
    for i in range(N_AMPS):
        amplist.append([])
    
    
    for i, filename in enumerate(file_list):
        if PROCESS_FILE_LIMIT != None:
            if i >= PROCESS_FILE_LIMIT: break
        print "Processing %s of %s files (%.2f %% done)" %(i, len(file_list), 100 * float(i) / float(len(file_list)))
        if not QUIET: print "Current file = %s..." %filename
        
        for amp in range(N_AMPS):
            image = GetImage_SingleAmp(filename, True, amp)
            maskedImg = afwImg.MaskedImageF(image)
            exposure = afwImg.ExposureF(maskedImg)
            
            if DISPLAY_LEVEL >= 1 and SINGLE_FILE == True: ds9.mtv(image)
#            exit()    
        
        # = Do finding ====================================================================
            threshold = afwDetect.Threshold(THRESHOLD, afwDetect.Threshold.VALUE)
            footPrintSet = afwDetect.FootprintSet(exposure.getMaskedImage(), threshold, "DETECTED", N_PIX_MIN)
            footPrintSet = afwDetect.FootprintSet(footPrintSet, GROW, ISOTROPIC)
        
            footPrints = footPrintSet.getFootprints()
            if not QUIET: print "Found %s footprints in amp %s of file %s"%(footPrints.size(), amp, filename)
            total_found += footPrints.size()
       
            if footPrints.size() >= 2000: # files with bright defects cause all sorts of problems
                print "Bad file - skipping..."
                continue

#            for pointnum, footprint in enumerate(footPrints):
#                heavy_footprint = afwDetect.HeavyFootprintF(footprint, maskedImg)
#                stat = GetTrackStats(heavy_footprint, image, False, track_number=pointnum)
#                amplist[amp].append(stat)
#                if SINGLE_POINT == True: exit()

#            pointlist = [1,7,11,12,13,14,23]
#            pointlist = [11]
            pointlist = np.arange(20)

            for pointnum, footprint in enumerate(footPrints):
#                if pointnum in pointlist:
                heavy_footprint = afwDetect.HeavyFootprintF(footprint, maskedImg)
                stat = GetTrackStats(heavy_footprint, image, False, track_number=pointnum)
                amplist[amp].append(stat)
#                 if pointnum == pointlist[-1]: exit()
#                    ds9.mtv(image)
#                    DrawStat(stat, True)
#                if SINGLE_POINT == True: exit()
            
        if SINGLE_FILE == True: exit()
    

    dt = time.time() - t0
    print "Data analysed in %.2f seconds, %s total footprints found" %(dt,total_found) 
    
    t0 = time.time()
    pickle.dump(amplist, open(pickle_file, 'wb'))
    dt = time.time() - t0
    print "Data pickled in %.2f seconds" %dt 
#===============================================================================

#
#def GetGains_Cosmics_using_pixels(amplist):
#    
#    histmin = 0
#    histmax = 100
#    nbins = 50
#    fitmin = 12
#    fitmax = 60
#
#    mpvs, mpvs_errors, chisqrs  = [], [], []
#    for amp in range(N_AMPS):
#        c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
#        landau_hist = TH1F('dE/dx', 'Muon pixel energy spectrum - Amp ' + str(amp),nbins,histmin,histmax)
#        
#        stat = TrackStats()
#        for i, stat in enumerate(amplist[amp]):
#            for value in stat.pixel_list_all_in_footprint:
#                length_thru_pixel = 10
#
#                if length_thru_pixel > 100.5 or length_thru_pixel < 10: print "Error in length through pixel!"                
#                pix_dedx = value / length_thru_pixel
##               if i % 4 == 0: landau_hist.Fill(pix_dedx)
#                landau_hist.Fill(pix_dedx)
#            landau_hist.Draw()
#            landau_hist.GetXaxis().SetTitle('dE/dx per pixel (ADU/#mum)')
#            landau_hist.GetYaxis().SetTitle('Frequency')
#            
#            langaus_func, chisqr = LanGausFit(landau_hist, fitmin,fitmax)
#            langaus_func.SetNpx(1000)
#            langaus_func.Draw("same")
#         
#            mpvs.append(langaus_func.GetParameter(1))
#            mpvs_errors.append(langaus_func.GetParError(1))
#            chisqrs.append(chisqr)
#            
#            
#            legend = TPaveText(0.65,0.68,0.99,0.93,"NDC")
#            legend.SetTextAlign(12) 
#            legend.SetFillColor(0) 
#            legend.AddText("MPV = " + str(round(mpvs[amp],2)) + " #pm " + str(round(mpvs_errors[amp],2)) + " ADU")
#            legend.AddText("Entries = " + str(landau_hist.GetEntries()))
#            legend.AddText("#chi^{2}_{red} = " + str(round(chisqr,2)))
#            legend.Draw("same")
#            
#            c3.SaveAs(OUTPUT_PATH + "amp" + str(zfill(str(amp),2)) +"dedx_hist" + FILE_TYPE)
#            del c3
#            del landau_hist
#
#    tot_chi_sq = 0
#    for i in range(N_AMPS):
#        print "Amp " + str(i) + " ChiSq = \t" + str(chisqrs[i])
#        tot_chi_sq += chisqrs[i]
#    print "Avg ChiSq = " + str(tot_chi_sq/len(chisqrs)) + "\n"
#
#    for i in range(N_AMPS):
#        print "Amp " + str(i) + " MPV = \t" + str(mpvs[i])
#
#
#    return mpvs, mpvs_errors, chisqrs

#===============================================================================

def GetGains_Cosmics(amplist):
    histmin = 0
    histmax = 100
    nbins = 50
    fitmin = 12
    fitmax = 60

    mpvs, mpvs_errors, chisqrs  = [], [], []
    for amp in range(N_AMPS):
        c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        landau_hist = TH1F('dE/dx', 'Muon energy spectrum - Amp ' + str(amp),nbins,histmin,histmax)
        
        for i, stat in enumerate(amplist[amp]):
#            if i % 4 == 0: landau_hist.Fill(stat.de_dx)
            landau_hist.Fill(stat.de_dx)
        landau_hist.Draw()
        landau_hist.GetXaxis().SetTitle('dE/dx (ADU/#mum)')
        landau_hist.GetYaxis().SetTitle('Frequency')
        
        langaus_func, chisqr = LanGausFit(landau_hist, fitmin,fitmax)
        langaus_func.SetNpx(1000)
        langaus_func.Draw("same")
     
#        langaus_func = LandauFit(landau_hist, fitmin,fitmax)
#        langaus_func.SetNpx(1000)
#        langaus_func.Draw("same")
#        chisqr = 0
        
        mpvs.append(langaus_func.GetParameter(1))
        mpvs_errors.append(langaus_func.GetParError(1))
        chisqrs.append(chisqr)
        
        
        legend = TPaveText(0.65,0.68,0.99,0.93,"NDC")
        legend.SetTextAlign(12) 
        legend.SetFillColor(0) 
        legend.AddText("MPV = " + str(round(mpvs[amp],2)) + " #pm " + str(round(mpvs_errors[amp],2)) + " ADU")
        legend.AddText("Entries = " + str(landau_hist.GetEntries()))
        legend.AddText("#chi^{2}_{red} = " + str(round(chisqr,2)))
        legend.Draw("same")
        
        c3.SaveAs(OUTPUT_PATH + "amp" + str(zfill(str(amp),2)) +"dedx_hist" + FILE_TYPE)
        del c3
        del landau_hist

    tot_chi_sq = 0
    for i in range(N_AMPS):
        print "Amp " + str(i) + " ChiSq = \t" + str(chisqrs[i])
        tot_chi_sq += chisqrs[i]
    avg_chi_sq = tot_chi_sq/len(chisqrs)
    print "Avg ChiSq = " + str(avg_chi_sq) + "\n"
    GLOBAL_OUT.append("Avg ChiSq = " + str(avg_chi_sq))

    for i in range(N_AMPS):
        print "Amp " + str(i) + " MPV = \t" + str(mpvs[i])

#    print "Worst cosmic fit has Chisq_red of %.2f" %chisqrs.sort[0]
#    chisqrs.sort(cmp=None, key=None, reverse=False)

    return mpvs, mpvs_errors, chisqrs

def GetGains_Fe55(amplist):
    from root_functions import GetLeftRightBinsAtPercentOfMax

    histmin = 200
    histmax = 700
    nbins = 200
#     fitmin = 400
#     fitmax = 550
    fit_threshold = 0.1
    
    hist_array = []

    K_Alphas = []
    K_Alphas_widths = []
    K_Betas = []
    K_Betas_widths = []
    
    means, mean_errors, chisqrs = [], [], []
    for amp in range(N_AMPS):

        stat = TrackStats()
        av_pixels = 0
        ntracks = 0

        c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        hist = TH1F('hist', '^{55}Fe Spectrum - Amp ' + str(amp),nbins,histmin,histmax)
        for stat in amplist[amp]:
            hist.Fill(stat.flux)
            av_pixels += stat.npix
            ntracks += 1
        hist.Draw()
        hist.GetXaxis().SetTitle('Charge (ADU)')
        hist.GetYaxis().SetTitle('Frequency')
        
        GLOBAL_OUT.append(str(amp) + '\t' + "%.2f"%(float(av_pixels)/float(ntracks)))
        
        fitmin, fitmax = GetLeftRightBinsAtPercentOfMax(hist, fit_threshold)
        
        fitfunc, chisqr = DoubleGausFit(hist, fitmin, fitmax)
        fitfunc.Draw("same")
        
        K_Alphas.append(fitfunc.GetParameter(0))
        K_Alphas_widths.append(fitfunc.GetParameter(1))
        K_Betas.append(fitfunc.GetParameter(3))
        K_Betas_widths.append(fitfunc.GetParameter(4))
        
        mean = fitfunc.GetParameter(0)
        mean_error = fitfunc.GetParError(0)
        means.append(mean)
        mean_errors.append(mean_error)
        chisqrs.append(chisqr)
        
        legend = TPaveText(0.65,0.68,0.99,0.93,"NDC")
        legend.SetTextAlign(12) 
        legend.SetFillColor(0) 
        legend.AddText("K_{#alpha} peak = " + str(round(mean,2)) + " #pm " + str(round(mean_error,2)) + " ADU")
        legend.AddText("Entries = " + str(len(amplist[amp])))
        legend.AddText("#chi^{2}_{red} = " + str(round(chisqr,2)))
        legend.Draw("same")
#        c3.SetLogy()
        c3.SaveAs(OUTPUT_PATH + "fe55_amp_" + str(zfill(str(amp),2)) +"sprectrum" + FILE_TYPE)
        hist_array.append(hist)
        del c3
        del hist

    print "amp \t K_a \t K_a_width \t K_b \t K_b_width"
    for amp in range(N_AMPS):
        print "%s\t%.3f\t%.3f\t%.3f\t%.3f\t" %(amp,K_Alphas[amp], K_Alphas_widths[amp], K_Betas[amp], K_Betas_widths[amp])

    mastercanvas = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    hist_array[amp].SetLineColor(1)
    hist_array[amp].Draw()
    for amp in range(N_AMPS -1):
        hist_array[amp].SetLineColor(amp+1)
        hist_array[amp].Draw("same")
    mastercanvas.SetLogy()
    mastercanvas.SaveAs(OUTPUT_PATH + "fe55_spectra_overlay" + FILE_TYPE)

    mastercanvas2 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    masterhist = TH1F('hist', '^{55}Fe Spectrum - Amp ' + str(amp),nbins,histmin,histmax)
    for amp in range(N_AMPS):
        masterhist.Add(hist_array[amp])
        masterhist.SetLineColor(amp+1)
        masterhist.Draw("")
    mastercanvas2.SetLogy()
    mastercanvas2.SaveAs(OUTPUT_PATH + "fe55_spectra_overlay_cumulative" + FILE_TYPE)
 

    return means, mean_errors, chisqrs

def DrawStat(stat, zoom_to_point = False):
#    if stat.ellipse_b == 0:
#        ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
    argstring = "@:"+str(4*stat.ellipse_Ixx)+','+str(4*stat.ellipse_Ixy)+','+str(4*stat.ellipse_Iyy) #multiply by four just to make it more exaggerated otherwise they all look like cirlces
    ds9.dot(argstring,stat.centroid_x,stat.centroid_y) #ellipse around the centroid
    ds9.dot("x",stat.centroid_x,stat.centroid_y)# cross on the peak
    displayUtils.drawBBox(stat.BBox, borderWidth=0.5) # border to fully encompass the bbox and no more
    if zoom_to_point: ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
    print 'length (diag,px) = %s, length (3D,true,um) = %s, flux = %s, npix = %s, dedx = %s' %(stat.diagonal_length_pixels, stat.length_true_um, stat.flux, stat.npix, stat.de_dx)


#===============================================================================
#===============================================================================
#===============================================================================
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
    
def Cut_R2(stat, cut):
    if stat.LineOfBestFit.R2 <= cut:
        return False
    else:
        return True

if __name__ == '__main__':
    start_time = time.time()
    import cPickle as pickle
    print "Running center cosmic finder\n"
    SINGLE_FILE = False
    SINGLE_POINT = False
    SPECIFIC_FILE = None

    home_dir = expanduser("~")
#    iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/temp'
#     iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/20_ampwise_fe55'
#    iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/10_ampwise_fe55_th25_gr1'
#    iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/10_ampwise_fe55_th25_gr2'
#    iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/single_fe55'

#    iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/10_ampwise_fe55_th25_gr1'
#     iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/10_ampwise_fe55_th25_gr1'
    
    iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/113_03_ampwise_th50_gr1_50_files'
#     iron_pickle_file = '/mnt/hgfs/VMShared/output/datasets/all_data_ampwise_fe55'


#     cosmic_pickle_file = '/mnt/hgfs/VMShared/output/datasets/temp'
    cosmic_pickle_file = '/mnt/hgfs/VMShared/output/datasets/all_ampwise_cosmics'
#    cosmic_pickle_file = '/hgfs/VMShared/output/datasets/cosmic_th50_px2_gr0_mega'
#    cosmic_pickle_file = '/hgfs/VMShared/output/datasets/cosmic_th50_px2_gr1_iso_mega'
#    cosmic_pickle_file = '/hgfs/VMShared/output/datasets/cosmic_th50_px2_gr2_iso_mega'
#    cosmic_pickle_file = '/hgfs/VMShared/output/datasets/cosmic_th50_px2_gr1_not_iso_mega'
#    cosmic_pickle_file = '/hgfs/VMShared/output/datasets/cosmic_th50_px2_gr2_not_iso_mega'

    input_path = '/mnt/hgfs/VMShared/data/fe55/20140709-112014/'
#    input_path = '/mnt/hgfs/VMShared/Data/all_darks/'


#    SPECIFIC_FILE = 'somefile'

#===============================================================================

    if SPECIFIC_FILE != None: SINGLE_FILE = True
    
#     DoAnalysis(input_path, cosmic_pickle_file, SINGLE_FILE, SPECIFIC_FILE=SPECIFIC_FILE, SINGLE_POINT=SINGLE_POINT)
    DoAnalysis(input_path, iron_pickle_file, SINGLE_FILE, SPECIFIC_FILE=SPECIFIC_FILE, SINGLE_POINT=SINGLE_POINT)
#     exit()   

    #= Fe55 - Get Gains =========================================================================
    if MAKE_FE55_SPECTRA:
        t0 = time.time()
        rawlist = pickle.load(open(iron_pickle_file, 'rb'))
        dt = time.time() - t0
        print "Data unpickled in %.2f seconds" %dt 
        
        amplist = []
        for i in range(16):
            amplist.append([])
    
        amplist = rawlist # <-- no cuts for Fe55
        means, mean_errors, chisqrs = GetGains_Fe55(amplist)
    
        avg_rel_error_percent_fe55 = 0
        for i in range(N_AMPS):
            avg_rel_error_percent_fe55 += 100 * (mean_errors[i]/means[i])
        avg_rel_error_percent_fe55 /= float(N_AMPS)
        print 'Avg rel error Fe55 %s' %avg_rel_error_percent_fe55

    exit()
    
    #= Cosmics - Get gains =========================================================================
    if MAKE_LANDAUS:
        rawlist = pickle.load(open(cosmic_pickle_file, 'rb'))
        amplist = []
        for i in range(N_AMPS):
            amplist.append([])
        nstats = 0
        rawstats = 0
        for amp in range(N_AMPS):
            for stat in rawlist[amp]:
                rawstats +=1
                if Cut_Length(stat, TRACK_LENGTH_CUT):
                    if Cut_Ellipticity(stat, ELLIPTICITY_CUT):
                        amplist[amp].append(stat)
                        nstats += 1
        print "%s cosmic stats loaded" %rawstats
        print "%s after cuts" %nstats
        mpvs, mpvs_errors, chisqrs = GetGains_Cosmics(amplist)
    #    mpvs, mpvs_errors, chisqrs = GetGains_Cosmics_using_pixels(amplist)
        
        avg_rel_error_percent_cosmics = 0
        for i in range(N_AMPS):
            avg_rel_error_percent_cosmics += 100 * (mpvs_errors[i]/mpvs[i])
        avg_rel_error_percent_cosmics /= float(N_AMPS)
        print 'Avg rel error cosmics %s' %avg_rel_error_percent_cosmics
    
    
    #= Correlation plot ==========================================================================
    if MAKE_LANDAUS and MAKE_FE55_SPECTRA:
        xlist, ylist, xerrlist, yerrlist = array('d'), array('d'), array('d'), array('d')
        for i in range(N_AMPS):
            xlist.append(1600/means[i])
            xerrlist.append((mean_errors[i]/means[i]) * xlist[i])
            ylist.append(70/mpvs[i])
            yerrlist.append((mpvs_errors[i]/mpvs[i]) * ylist[i])
    
        c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        gr = TGraphErrors(len(xlist), xlist, ylist, xerrlist, yerrlist) #populate graph with data points
    
        gr.SetTitle("")
        gr.GetXaxis().SetTitle( "^{55}Fe Gain (e^{-}/ADU)" )
        gr.GetYaxis().SetTitle( "Cosmic Gain (e^{-}/ADU)" )
        gr.GetYaxis().SetTitleOffset(1.1)
        gr.GetXaxis().SetTitleOffset(1.2)
        
    #    fitfunc = TF1("line","[0]*x", 0,5) #straight line THROUGH ORIGIN!
        fitfunc = TF1("line","[0]*x + [1]", 0,5) # straight line
        fitfunc.SetNpx(1000)
        fitfunc.SetParameter(0,1) # grad
        fitfunc.SetParameter(1,3) # y-intercept
    
        gr.Fit(fitfunc,"ME")
        gr.Draw("AP")
        
        chisq = fitfunc.GetChisquare()
        NDF = fitfunc.GetNDF()
        try:
            chisqr_over_NDF = chisq/NDF
        except:
            chisqr_over_NDF = -1
        print "Chisqr / NDF = " + str(chisq) + ' / ' + str(NDF) + ' = ' + str(chisqr_over_NDF) +'\n'
    
        R2 = gr.GetCorrelationFactor()**2
        legend = TPaveText(0.25,0.60,0.55,0.85,"NDC")
        legend.SetTextAlign(12) 
        legend.SetFillColor(0) 
        legend.SetTextSize(0.05) 
        legend.AddText("R^{2} = " + str(round(R2,3)))
        legend.AddText("#chi^{2}_{red} = " + str(round(chisqr_over_NDF,1)))
        legend.Draw("same")
        
        c1.SaveAs(OUTPUT_PATH + "cosmic_landau_correlation" + FILE_TYPE)
    
    
    #===========================================================================
    #===========================================================================



        
    #= Master Landaus =======================================================
    
    if MAKE_LANDAUS:
        histmin = 0
        histmax = 100
        nbins = 50
        fitmin = 12
        fitmax = 60
    
        c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        landau_hist = TH1F('Track Length', 'Track Length',nbins,histmin,histmax)
        for amp in range(N_AMPS):
            for stat in rawlist[amp]:
                landau_hist.Fill(stat.de_dx)
        landau_hist.Draw()
        landau_hist.GetXaxis().SetTitle('dE/dx (ADU/#mum)')
        landau_hist.GetYaxis().SetTitle('Frequency')
        langaus_func, rawchisqr = LanGausFit(landau_hist, fitmin,fitmax)
        langaus_func.SetNpx(1000)
        langaus_func.Draw("same")
        print "raw master landau chisq_red = %.3f"%(rawchisqr)
        
        c3.SaveAs(OUTPUT_PATH + "Master_landau_raw" + FILE_TYPE)
        del c3
        del landau_hist
        
        
            
        c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        landau_hist = TH1F('Track Length', 'Track Length',nbins,histmin,histmax)
        for amp in range(N_AMPS):
            for stat in amplist[amp]:
                if Cut_Length(stat, TRACK_LENGTH_CUT):
#                    if Cut_Ellipticity(stat, ELLIPTICITY_CUT):
#                        if Cut_Chisq(stat, CHISQ_CUT):
#                             if Cut_R2(stat, R2_CUT):
                                landau_hist.Fill(stat.de_dx)
        landau_hist.Draw()
        landau_hist.GetXaxis().SetTitle('dE/dx (ADU/#mum)')
        landau_hist.GetYaxis().SetTitle('Frequency')
        langaus_func, cutchisq = LanGausFit(landau_hist, fitmin,fitmax)
        langaus_func.SetNpx(1000)
        langaus_func.Draw("same")

        print "cut master landau chisq_red = %.3f"%(cutchisq)
        GLOBAL_OUT.append('cut master landau chisq_red = %.3f"%(cutchisq)')

        # 1.548 with 150,3 and 28,598 entries
        # 6.926 with just r2 cut at 0.8, 20,891 entries
        # 23.353 with just chisq cut at 20,277
        # 6.926 with length at 150 and r2 at 0.8
  
  
        c3.SaveAs(OUTPUT_PATH + "Master_landau_cut" + FILE_TYPE)
        del c3
        del landau_hist
        
        
        
        
    #= R2 distribution =======================================================
    if MAKE_LANDAUS:
        histmin = 0
        histmax = 1
        nbins = 100
    
        c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        r2_hist_cut = TH1F('R2', 'R2',nbins,histmin,histmax)
        for amp in range(N_AMPS):
            for stat in amplist[amp]:
                r2_hist_cut.Fill(stat.LineOfBestFit.R2)
        r2_hist_cut.Draw()
        r2_hist_cut.GetXaxis().SetTitle('R^{2}')
        c3.SetLogy()
        c3.SaveAs(OUTPUT_PATH + "r2_cut" + FILE_TYPE)
        del c3
        del r2_hist_cut
        
        c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        r2_hist_raw= TH1F('R2', 'R2',nbins,histmin,histmax)
        for amp in range(N_AMPS):
            for stat in rawlist[amp]:
                r2_hist_raw.Fill(stat.LineOfBestFit.R2)
#                r2_hist_raw.Fill(stat.LineOfBestFit.chisq_red / stat.diagonal_length_pixels)
        r2_hist_raw.Draw()
        r2_hist_raw.GetXaxis().SetTitle('R^{2}')
#        c3.SetLogy()
        c3.SaveAs(OUTPUT_PATH + "r2_raw" + FILE_TYPE)
        del c3
        del r2_hist_raw
    

    #===========================================================================
    if MAKE_LANDAUS:
        try:
            dummy = amplist[0][0].pixel_list_all_in_footprint
            list_is_heavy = True
        except:
            list_is_heavy = False
            print "List is not heavy, skipping requested section..." 
        
        if list_is_heavy:    
            histmin = THRESHOLD
            histmax = 10000
            nbins = 1000
        
            c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
            pixel_hist = TH1F('Pixel values within footprint', 'Pixel values within footprint',nbins,histmin,histmax)
            i = 0
            for amp in range(N_AMPS):
                for stat in amplist[amp]:
                    for value in stat.pixel_list_all_in_footprint:
                        pixel_hist.Fill(value)
            pixel_hist.GetXaxis().SetTitle('Pixel value (ADU)')
            pixel_hist.GetYaxis().SetTitle('Frequency')
            pixel_hist.Draw()
        #    c1.SetLogx()
            c1.SetLogy()
            c1.SaveAs(cosmic_pickle_file +"_pixel_value_footprint" + FILE_TYPE)
            del c1
            del pixel_hist
        
    
    #= Track length histo=======================================================
    
    if MAKE_LANDAUS:
        histmin = 0
        histmax = 800
        nbins = 50
    
        c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        landau_hist = TH1F('Track Length', 'Track Length',nbins,histmin,histmax)
        for amp in range(N_AMPS):
            for stat in amplist[amp]:
                landau_hist.Fill(stat.length_true_um)
        landau_hist.Draw()
        landau_hist.GetXaxis().SetTitle('Track Length (#mum)')
        landau_hist.GetYaxis().SetTitle('Frequency')
        c3.SaveAs(OUTPUT_PATH + "track_length_distribution" + FILE_TYPE)
        del c3
        del landau_hist
        



############## END CODE ##############
    
    all_time = time.time() - start_time
    for line in GLOBAL_OUT:
        print line
    print "All analysis done in %.2f seconds" %all_time 
    exit()
    
############# DONE ################
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    #===========================================================================
    c4 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    
    from array import array
    xpoints, ypoints = array('d'), array('d')
    
    for stat in statslist:
        if stat.ellipse_b <> 0:
            xpoints.append(float(stat.ellipse_a))
            ypoints.append(float(stat.ellipse_b))

    ab_graph = TGraph(len(xpoints), xpoints, ypoints)
    
    ab_graph.GetXaxis().SetTitle('a')
    ab_graph.GetYaxis().SetTitle('b')
    ab_graph.GetXaxis().SetRangeUser(0,100)
    ab_graph.GetYaxis().SetRangeUser(0,10)
    
    ab_graph.Draw("AP")
    c4.SaveAs(OUTPUT_PATH + "ab_graph" + FILE_TYPE)
    del c4
    del ab_graph
    
    #===========================================================================
    # NB This uses the raw (pre-cut) dataset!
    histmin = 0
    histmax = 50
    nbins = 50

    c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    landau_hist = TH1F('a/b ratio', 'a/b ratio',nbins,histmin,histmax)
    for stat in rawlist:
        if stat.ellipse_b <> 0:
            landau_hist.Fill(stat.ellipse_a/stat.ellipse_b)
    landau_hist.Draw()
    c3.SaveAs(OUTPUT_PATH + "ratio" + FILE_TYPE)
    del c3
    del landau_hist



    #===========================================================================
    histmin = 0
    histmax = 500
    nbins = 100

    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    pixel_hist = TH1F('Pixel values within BBox', 'Pixel values within BBox',nbins,histmin,histmax)
    for stat in statslist:
        for value in stat.pixel_list_all_in_bbox:
            if value >= 15:
                pixel_hist.Fill(value)
    pixel_hist.GetXaxis().SetTitle('Pixel value (ADU)')
    pixel_hist.GetYaxis().SetTitle('Frequency')
    pixel_hist.Draw()
    c1.SaveAs(OUTPUT_PATH + "pixel_value_hist_bbox" + FILE_TYPE)
    del c1
    del pixel_hist
    
    
    #===========================================================================
    histmin = 0
    histmax = 500
    nbins = 50

    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    pixel_hist = TH1F('Pixel values within footprint', 'Pixel values within footprint',nbins,histmin,histmax)
    i = 0
    for stat in statslist:
        for value in stat.pixel_list_all_in_footprint:
            pixel_hist.Fill(value)
    pixel_hist.GetXaxis().SetTitle('Pixel value (ADU)')
    pixel_hist.GetYaxis().SetTitle('Frequency')
    pixel_hist.Draw()
    c1.SaveAs(OUTPUT_PATH + "pixel_value_hist_footprint" + FILE_TYPE)
    del c1
    del pixel_hist
    
    
    
    #===========================================================================
    histmin = 0
    histmax = 250
    nbins = 50

    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    pixel_hist = TH1F('Pixels per footprint', 'Pixels per footprint',nbins,histmin,histmax)
    i = 0
    for stat in statslist:
        pixel_hist.Fill(len(stat.pixel_list_all_in_footprint))
    pixel_hist.GetXaxis().SetTitle('Footprint Area (pixels)')
    pixel_hist.GetYaxis().SetTitle('Frequency')
    pixel_hist.Draw()
    c1.SaveAs(OUTPUT_PATH + "pixels_per_footprint" + FILE_TYPE)
    del c1
    del pixel_hist
    
    
    
    #===========================================================================


    print '\n*** End code ***'
    exit()
    
    
    
#======================================================================================================================================================
#======================================================================================================================================================
#======================================================================================================================================================
#======================================================================================================================================================
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #
#    for rowdata in imdata[:]:
#        for pixeldata in rowdata:
##            print pixeldata
#            imagehist.Fill(pixeldata)







#    filename = '/home/mmmerlin/useful/herring_bone.fits'

    
    ## Paul's way
#    filename = input_path + input_file
#    bigimage = AssembleImage(filename)
#    if DISPLAY_LEVEL >= 1: ds9.mtv(bigimage)
    
    
    ## My bad way
#    image = AssembleImage_bad_way(filename)
#    if DISPLAY_LEVEL >= 1: ds9.mtv(image)
    
    
    ##Mosaic way
#    mosaicmaker = BuildMosaic(input_path + input_file)
#    mosaic = mosaicmaker.makeMosaic()
#    if DISPLAY_LEVEL >= 1: ds9.mtv(mosaic)
## Note - to use this you then need to write a function to convert 
## the mosaic into an image for processing as mosaics do not function like images


    ## Single image way
#    exposure = afwImg.ExposureF(input_path + input_file)




#def GetNumpyArrayFromFootprint(footprint, parent_image):
#    out = np.zeros(footprint.getArea(), dtype=parent_image.getArray().dtype)
#    array = afwDetect.flattenArray(footprint, parent_image.getArray(), out, parent_image.getXY0())
#    return array


#class MuonConfig(Config):
#    # TODO: strip this down to remove bloat
#    
#    detection = ConfigField(dtype=SourceDetectionTask.ConfigClass, doc="Detection config")
#    background = ConfigField(dtype=BackgroundConfig, doc="Background subtraction config")
#    cosmicray = ConfigField(dtype=measAlg.FindCosmicRaysConfig, doc="Cosmic-ray config")
#    psfSigma = Field(dtype=float, default=2.0, doc="PSF Gaussian sigma")
#    psfSize = Field(dtype=int, default=21, doc="PSF size (pixels)")
#
#    def setDefaults(self):
#        super(MuonConfig, self).setDefaults()
#        self.cosmicray.keepCRs = True # We like CRs!
#        self.cosmicray.nCrPixelMax = 1000000
#        self.cosmicray.minSigma = 5.0
#        self.cosmicray.min_DN = 1.0
#        self.cosmicray.cond3_fac2 = 0.4
