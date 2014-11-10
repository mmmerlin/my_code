from __builtin__ import str, range, len # why does it put these in when that is unnecessary?!
from os.path import expanduser, isfile, os
from os import listdir
import time

import lsst.afw.detection     as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.afw.display.ds9   as ds9
import lsst.afw.image as afwImg

import ROOT
from ROOT import TCanvas, TF1, TH1F, TGraph, TLegend, TGraphErrors, TPaveText
import numpy as np
from numpy.core.defchararray import zfill

import cPickle as pickle


# my stuff
from root_functions import DoubleGausFit, CANVAS_HEIGHT, CANVAS_WIDTH
from image_assembly import GetImage_SingleAmp, MakeBiasImage_SingleAmp
from my_image_tools import FastHistogramImageData

##########################################################################################
# path options
input_path = '/mnt/hgfs/VMShared/Data/QE_LSST/fe55/20140709-112014/'
OUTPUT_PATH = "/mnt/hgfs/VMShared/output/QE_LSST/"

PICKLE_PATH = '/mnt/hgfs/VMShared/Data/QE_LSST/pickles/'
PICKLE_NAME = 'temp'
OUTFILE = OUTPUT_PATH + 'noise.txt'

# input_path = '/mnt/hgfs/VMShared/Data/John/light/'
# PICKLE_PATH = '/mnt/hgfs/VMShared/output/Fe55_John/pickles/'
# OUTPUT_PATH = '/mnt/hgfs/VMShared/output/Fe55_John/'


FILE_TYPE = ".png"
N_AMPS = 16

############


# Track finding options
THRESHOLD = 25
N_PIX_MIN = 2
GROW = 2
ISOTROPIC = False


# Analysis options
SPECIFIC_FILE = None
SINGLE_POINT = False
QUIET = False
PROCESS_FILE_LIMIT = 99999


# Post processing options
MAKE_FE55_SPECTRA = True
GLOBAL_OUT = []


def DoAnalysis(input_path):
    t0 = time.time()
    total_found = 0
    
    # write header for noise file
    with open(OUTFILE, 'w') as this_file:
        this_file.write("THRESHOLD = %s\n"%THRESHOLD)
        this_file.write("N_PIX_MIN = %s\n"%N_PIX_MIN)
        this_file.write("GROW = %s\n"     %GROW)
        this_file.write("Background subtraction = DM\n")
        this_file.write('\n')
        this_file.write("amp" + '\t' + 'mean' + '\t' + 'mean_error' + '\t' + 'sigma' + '\t' + 'sigma_error' + '\n')
        
        
    # collect the files we want
    dircontents = listdir(input_path)
    file_list = []
    for thisfile in dircontents:
        if str(thisfile).find('coadded')!= -1: continue # skip coadd files
        if str(thisfile).find('.DS')    != -1: continue # skip weird files
        if str(thisfile).find('bias')   != -1: continue # skip bias  files
        if isfile(input_path + thisfile): file_list.append(thisfile) # skip dirs
    
    
    # make the list of lists
    amplist = []
    for i in range(N_AMPS):
        amplist.append([])
        
        
    # make bias images from all bias files in dir and put in an array
#    bias_images = [MakeBiasImage_SingleAmp(input_path, ampnum) for ampnum in range(N_AMPS)]
    
    
    # loop over all Fe55 files, getting spectrum from each and pickling
    # after background subtracting, the baseline spectrum is fitted and gaus fit parameters are save to text file 
    for i, filename in enumerate(file_list):
        if PROCESS_FILE_LIMIT != None:
            if i >= PROCESS_FILE_LIMIT: break
        print "Processing %s of %s files (%.2f %% done)" %(i, len(file_list), 100 * float(i) / float(len(file_list)))
        if not QUIET: print "Current file = %s..." %filename
        
        for amp in range(N_AMPS):
            ###########################################
            ##### DMStack background subtraction:
            image = GetImage_SingleAmp(input_path + filename, True, amp)

            ##### Bias 0File background subtraction:
#            image = afwImg.ImageF(input_path + filename, amp + 2)
#            image -= bias_images[amp]
            ###########################################

            maskedImg = afwImg.MaskedImageF(image)
            exposure = afwImg.ExposureF(maskedImg)
            
#            # histogram the background / fit the noise, write to file
##            c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
#            hist, d1, d2 = FastHistogramImage_JustData(image.getArray())
#            hist.GetXaxis().SetRangeUser(-50,3000)
#            hist.Fit('gaus')
#            fitfunc = hist.GetFunction('gaus')
##            fitfunc.SetNpx(1000) #draw it nicely
#            mean = fitfunc.GetParameter(1)
#            mean_error = fitfunc.GetParError(1)
#            sigma = fitfunc.GetParameter(2)
#            sigma_error = fitfunc.GetParError(2)
##            hist.Draw() #if you want to see the plot
##            c1.SaveAs(OUTPUT_PATH + "baseline_amp_" + str(amp) + ".pdf") #if you want to see the plot
#            with open(OUTFILE, 'a') as this_file:
#                this_file.write(str(amp) + '\t' + str(mean) + '\t' + str(mean_error) + '\t' + str(sigma) + '\t' + str(sigma_error) + '\n')

            
            # Find the clusters
            threshold = afwDetect.Threshold(THRESHOLD, afwDetect.Threshold.VALUE)
            footPrintSet = afwDetect.FootprintSet(exposure.getMaskedImage(), threshold, "DETECTED", N_PIX_MIN)
            footPrintSet = afwDetect.FootprintSet(footPrintSet, GROW, ISOTROPIC)
        
            footPrints = footPrintSet.getFootprints()
            if not QUIET: print "Found %s footprints in amp %s of file %s"%(footPrints.size(), amp, filename)
            total_found += footPrints.size()

            # loop over the clusters and append them to the lists, reading for pickling
            for footprint in footPrints:
                array = np.zeros(footprint.getArea(), dtype=image.getArray().dtype)#MERLIN1
                afwDetect.flattenArray(footprint, image.getArray(), array, image.getXY0())#MERLIN1
                flux = array.sum(dtype = 'f8') #MERLIN1
                amplist[amp].append(flux)
            # next cluster
        # next amp
    # next Fe55 File
    
    # all files now processed, report and pickle        
    dt = time.time() - t0
    print "Data analysed in %.2f seconds, %s total footprints found" %(dt,total_found) 
    
    t0 = time.time()
    pickle.dump(amplist, open(PICKLE_PATH + PICKLE_NAME, 'wb'))
    dt = time.time() - t0
    print "Data pickled in %.2f seconds" %dt 
#===============================================================================

def GetGains_Fe55(amplist):
    
    from root_functions import GetLeftRightBinsAtPercentOfMax

    histmin = 200
    histmax = 700
    nbins = 200
    fit_threshold_in_percent = 0.5
    
    K_Alphas = []
    K_Alpha_errors = []
    K_Alphas_widths = []
    K_Betas = []
    K_Betas_widths = []
    chisqrs = []
    
    for amp in range(N_AMPS):
        
        c3 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT) #create canvas
        hist = TH1F('hist', '^{55}Fe Spectrum - Amp ' + str(amp),nbins,histmin,histmax)
        for flux in amplist[amp]:
            hist.Fill(flux)
        hist.Draw()
        hist.GetXaxis().SetTitle('Charge (ADU)')
        hist.GetYaxis().SetTitle('Frequency')
        
        fitmin, fitmax = GetLeftRightBinsAtPercentOfMax(hist,fit_threshold_in_percent)            
        
        fitfunc, chisqr = DoubleGausFit(hist, fitmin, fitmax)
        fitfunc.Draw("same")
        
        K_Alphas.append(fitfunc.GetParameter(0))
        K_Alpha_errors.append(fitfunc.GetParError(0))
        K_Alphas_widths.append(fitfunc.GetParameter(1))
        K_Betas.append(fitfunc.GetParameter(3))
        K_Betas_widths.append(fitfunc.GetParameter(4))
        chisqrs.append(chisqr)
        
        legend = TPaveText(0.65,0.68,0.99,0.93,"NDC")
        legend.SetTextAlign(12) 
        legend.SetFillColor(0) 
        legend.AddText("K_{#alpha} peak = " + str(round(K_Alphas[amp],2)) + " #pm " + str(round(K_Alpha_errors[amp],2)) + " ADU")
        legend.AddText("Entries = " + str(len(amplist[amp])))
        legend.AddText("#chi^{2}_{red} = " + str(round(chisqrs[amp],2)))
        legend.Draw("same")
        c3.SaveAs(OUTPUT_PATH + "fe55_amp_" + str(zfill(str(amp),2)) +"sprectrum" + FILE_TYPE)
        c3.SetLogy()
        c3.SaveAs(OUTPUT_PATH + "fe55_amp_" + str(zfill(str(amp),2)) +"sprectrum_logy" + FILE_TYPE)
        del c3
        del hist

    print "amp \t K_a \t K_a_width \t K_b \t K_b_width \t K_a_error"
    for amp in range(N_AMPS):
        print "%s\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f" %(amp,K_Alphas[amp], K_Alphas_widths[amp], K_Betas[amp], K_Betas_widths[amp], K_Alpha_errors[amp])

    return K_Alphas, K_Alpha_errors, chisqrs


if __name__ == '__main__':
    start_time = time.time()
    print "Running Fe55 Gain Analysis for QE\n"
    

#===============================================================================

#     DoAnalysis(input_path)
#     exit()   


#= Fe55 - Get Gains =========================================================================
    if MAKE_FE55_SPECTRA:
        
        amplist = pickle.load(open(PICKLE_PATH + PICKLE_NAME, 'rb'))
        
        means, mean_errors, chisqrs = GetGains_Fe55(amplist)
    
        rel_errors = [(100 * (mean_errors[i]/means[i])) for i in range(N_AMPS)]
        average_error = np.asarray(rel_errors, dtype = 'f8').sum()/16.0
        
        print 'Avg fit error = %.4f%%' %average_error
        print 'Max error = %.4f%%' %max(rel_errors)


#===========================================================================



############## END CODE ##############
    
    all_time = time.time() - start_time
    for line in GLOBAL_OUT:
        print line
    print "All analysis done in %.2f seconds" %all_time 
    print '\n*** End code ***'
    
    
    
    
    
