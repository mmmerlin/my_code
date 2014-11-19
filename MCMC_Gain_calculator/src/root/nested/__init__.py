import ROOT
from ROOT import TCanvas, TF1, TH1F, TGraph, TLegend, TGraphErrors, TPaveText
from root_functions import CANVAS_HEIGHT, CANVAS_WIDTH
import numpy as np
from numpy.core.defchararray import zfill

import cPickle as pickle
import ngmix
from fit_constraints import ExamplePrior
from imprint import imprint

import lsst.afw.math        as math
import lsst.afw.detection     as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.afw.display.ds9   as ds9
import lsst.afw.image as afwImg

from __builtin__ import str, range, len # why does it put these in when that is unnecessary?!
from os.path import expanduser, isfile, os
from os import listdir
import time



# my stuff
from root_functions import DoubleGausFit, CANVAS_HEIGHT, CANVAS_WIDTH
from image_assembly import GetImage_SingleAmp, MakeBiasImage_SingleAmp
from my_image_tools import FastHistogramImageData

##########################################################################################
# path options

# INPUT_PATH =      '/mnt/hgfs/VMShared/Data/fe55/device112-04_march13_750_files/'
# PICKLE_PATH =     '/mnt/hgfs/VMShared/Data/fe55/device112-04_march13_750_files/pickles_1/'

INPUT_PATH =        '/mnt/hgfs/VMShared/Data/fe55/device112-04_sept13_900_files/'
PICKLE_PATH =       '/mnt/hgfs/VMShared/Data/fe55/device112-04_sept13_900_files/pickles/'

DM_PICKLE_PREFIX = 'DM_'
NG_PICKLE_PREFIX = 'NG_'

OUTPUT_PATH = '/mnt/hgfs/VMShared/output/MCMC_Gain_test/'

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
QUIET = True
PROCESS_FILE_LIMIT = 25


# Post processing options
MAKE_FE55_SPECTRA = True
GLOBAL_OUT = []


def DoAnalysis(input_path):
    t0 = time.time()
    Ntotal = 0
    Nfitted = 0
    
    # write header for noise file
#     with open(OUTFILE, 'w') as this_file:
#         this_file.write("THRESHOLD = %s\n"%THRESHOLD)
#         this_file.write("N_PIX_MIN = %s\n"%N_PIX_MIN)
#         this_file.write("GROW = %s\n"     %GROW)
#         this_file.write("Background subtraction = DM\n")
#         this_file.write('\n')
#         this_file.write("amp" + '\t' + 'mean' + '\t' + 'mean_error' + '\t' + 'sigma' + '\t' + 'sigma_error' + '\n')
        
        
    # collect the files we want
    dircontents = listdir(input_path)
    file_list = []
    for thisfile in dircontents:
        if str(thisfile).find('coadded')!= -1: continue # skip coadd files
        if str(thisfile).find('.DS')    != -1: continue # skip weird files
        if str(thisfile).find('bias')   != -1: continue # skip bias  files
        if str(thisfile).find('dark')   != -1: continue # skip bias  files
        if isfile(input_path + thisfile): file_list.append(thisfile) # skip dirs
    
    
    # make the list of lists
    DM_amplist = []
    NG_amplist = []
    for i in range(N_AMPS):
        DM_amplist.append([])
        NG_amplist.append([])
        
        
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

            maskedImg = afwImg.MaskedImageF(image)
            exposure = afwImg.ExposureF(maskedImg)
            
#             # histogram the background / fit the noise, write to file
#             c1 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT) #create canvas
#             hist, d1, d2 = FastHistogramImageData(image.getArray(),-100000)
#             hist.GetXaxis().SetRangeUser(-50,50)
#             hist.Fit('gaus')
#             fitfunc = hist.GetFunction('gaus')
#             fitfunc.SetNpx(1000) #draw it nicely
#             mean = fitfunc.GetParameter(1)
#             mean_error = fitfunc.GetParError(1)
#             sigma = fitfunc.GetParameter(2)
#             sigma_error = fitfunc.GetParError(2)
#             hist.Draw() #if you want to see the plot
#             c1.SaveAs(OUTPUT_PATH + "baseline_amp_" + str(amp) + ".png") #if you want to see the plot
#             del hist, c1, fitfunc
#             with open(OUTFILE, 'a') as this_file:
#                 this_file.write(str(amp) + '\t' + str(mean) + '\t' + str(mean_error) + '\t' + str(sigma) + '\t' + str(sigma_error) + '\n')
#             continue
   
            
            #stats
            statFlags = math.NPOINT | math.MEAN | math.STDEV | math.MAX | math.MIN | math.ERRORS| math.STDEVCLIP
            control = math.StatisticsControl()
            SAT = afwImg.MaskU_getPlaneBitMask("SAT")
            control.setAndMask(SAT)
            
            imageStats = math.makeStatistics(maskedImg, statFlags, control)
            mean = imageStats.getResult(math.MEAN)[0]
            stdevclip = imageStats.getResult(math.STDEVCLIP)[0]
            
            
            # Find the clusters
            threshold = afwDetect.Threshold(THRESHOLD, afwDetect.Threshold.VALUE)
            footPrintSet = afwDetect.FootprintSet(exposure.getMaskedImage(), threshold, "DETECTED", N_PIX_MIN)
            footPrintSet = afwDetect.FootprintSet(footPrintSet, GROW, ISOTROPIC)
        
            footPrints = footPrintSet.getFootprints()
            print "Found %s footprints in amp %s of file %s"%(footPrints.size(), amp, filename)

            # loop over the clusters and append them to the lists, reading for pickling
            for footprint in footPrints:
                Ntotal += 1
                array = np.zeros(footprint.getArea(), dtype=image.getArray().dtype)#MERLIN1
                afwDetect.flattenArray(footprint, image.getArray(), array, image.getXY0())#MERLIN1
                flux = array.sum(dtype = 'f8') #MERLIN1
                DM_amplist[amp].append(flux)
                
                
    # calculate shapes using vanilla DM
                centroid_x, centroid_y = footprint.getCentroid()
    
    # another piece of magic from Jim B to evaluate the flux
                array = np.zeros(footprint.getArea(), dtype=image.getArray().dtype)
                afwDetect.flattenArray(footprint, image.getArray(), array, image.getXY0())
                intens = array.sum()
                
    # get stamps for Erin's sub-sampling
                box = footprint.getBBox()
                xmin = box.getMinX()
                xmax = box.getMaxX()
                ymin = box.getMinY()
                ymax = box.getMaxY()
    #                im = image.getArray()
    #                stamp = im[ymin:ymax+1, xmin:xmax+1]
                im = image.getArray().transpose()
                stamp = im[xmin:xmax+1, ymin:ymax+1]
    
    # start using Erin's package               
                model="gauss"
        
    # create a weight map (just 1/noise^2 for all pixels for now)
                noise = 0*stamp + stdevclip
                weight_map = 1/noise**2
               
    # create an Observation object.  Only image and weight for now
                obs = ngmix.observation.Observation(stamp, weight=weight_map)
                
    # fit with 16x16 sub-pixel sampling
                nsub=16
        
    # parameters for the maximum likelihood fitter
                lm_pars={'maxfev':500,
                         'ftol':1.0e-6,
                         'xtol':1.0e-6,
                         'epsfcn': 1.0e-6}
    
    # do not constrain        
                prior=None
                fitter=ngmix.fitting.LMSimple(obs, model, nsub=nsub, lm_pars=lm_pars, prior=prior)
                        
    # make a guess for [cen1,cen2,g1,g2,T,flux] where T is 2*sigma**2
                cen1 = centroid_x - xmin + 0.1 * (np.random.random()-0.5)
                cen2 = centroid_y - ymin + 0.1 * (np.random.random()-0.5)
                g1=0.
                g2=0.
                T_guess = 0.32 # = 2*(0.4)**2
                flux_guess=intens
    #                guess=np.array( [cen1,cen2,g1,g2,log10(T_guess),log10(flux_guess)] )
                guess=np.array( [cen1,cen2,g1,g2,T_guess,flux_guess] )
        
    # run the fitter
                fitter.run_lm(guess)
                result=fitter.get_result()
    
                if not QUIET: print "event", Ntotal
               
                if result['flags'] != 0:
                    print " *****  something went wrong ******"
                else:
                    Nfitted = Nfitted + 1
        #            print("best fit parameters:",result['pars'])
        #            print("err on parameters:  ",result['pars_err'])
        
    # also get the linear parameters
    #                    lin_res=fitter.get_lin_result()
                    if not QUIET:
                        print "best fit lin pars:",result['pars']
                        print "err on lin pars:  ",result['pars_err']
                        print "chi2:  ",result['chi2per']
        
                    chi2 = result['chi2per']
        
                    xx  = result['pars'][0]
                    yy  = result['pars'][1]
                    gg1 = result['pars'][2]
                    gg2 = result['pars'][3]
                    tt  = result['pars'][4]
                    ff  = result['pars'][5]
    
                    exx  = result['pars_err'][0]
                    eyy  = result['pars_err'][1]
                    egg1 = result['pars_err'][2]
                    egg2 = result['pars_err'][3]
                    ett  = result['pars_err'][4]
                    eff  = result['pars_err'][5]
    
                    ixx = int(xx + 0.5)
                    iyy = int(yy + 0.5)
    
                    if not QUIET:
                        imprint(stamp, fmt='%7.1f')
                        print "xmin, xmax, ymin, ymax"
                        print xmin, xmax, ymin, ymax
                        print "cen1, cen2", cen1, cen2
                        print "xx, yy, ixx, iyy, XX, YY"
                        print xx, yy, ixx, iyy, xx+0.5-ixx, yy+0.5-iyy
                        print "stamp size" 
                        print stamp.shape[0], stamp.shape[1]
                    
                    if ixx < stamp.shape[0]-1 and ixx > 0 and iyy < stamp.shape[1]-1 and iyy > 0:
                        stamp_c = stamp[ixx][iyy]
                        stamp_t = stamp[ixx][iyy+1]
                        stamp_b = stamp[ixx][iyy-1]
                        stamp_l = stamp[ixx-1][iyy]
                        stamp_r = stamp[ixx+1][iyy]
                    else:
                        stamp_c = 1
                        stamp_t = 0
                        stamp_b = 0
                        stamp_l = 0
                        stamp_r = 0
                                            
                    if not QUIET:
                        print "center, top, bottom, left, right"
                        print stamp_c, stamp_t, stamp_b, stamp_l, stamp_r                                      
                    
                    
#                     print "DM_flux = %s, intens = %s"%(flux, intens)
                    DM_amplist[amp].append(flux)
                    NG_amplist[amp].append(ff)
                    

                    if Ntotal % 100 == 0: 
                        print "Analysed %s clusters of %s (%s%%) in %s"%(Ntotal, footPrints.size(), round((100 * float(Ntotal)/float(footPrints.size())),2), filename)                    
            # next cluster
        # next amp
    # next Fe55 File
    
    # all files now processed, report and pickle        
    dt = time.time() - t0
    print "Data analysed in %.2f seconds, %s total footprints found" %(dt,Ntotal) 
    
    t0 = time.time()
    pickle.dump(DM_amplist, open(PICKLE_PATH + DM_PICKLE_PREFIX, 'wb'))
    pickle.dump(NG_amplist, open(PICKLE_PATH + NG_PICKLE_PREFIX, 'wb'))
    dt = time.time() - t0
    print "Data pickled in %.2f seconds" %dt 
#===============================================================================

def GetGains_Fe55(amplist, file_prefix = ''):
    
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
#         if amp != 11: continue
        
        c3 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT) #create canvas
        hist = TH1F('hist', '^{55}Fe Spectrum - Amp ' + str(amp),nbins,histmin,histmax)
        for flux in amplist[amp]:
            hist.Fill(flux)
        hist.Draw()
        hist.GetXaxis().SetTitle('Charge (ADU)')
        hist.GetYaxis().SetTitle('Frequency')
        
####### manual gaus fit
#         hist.Fit('gaus','gaus','',390.,418.)
#         mean = hist.GetFunction('gaus').GetParameter(1)
#         print mean
#         exit()
        
         
        fitmin, fitmax = GetLeftRightBinsAtPercentOfMax(hist,fit_threshold_in_percent)            
#         fitmin, fitmax = 390.,480.   

### fit range overrides for 112-04 900 file dataset
#         if amp == 6:
#             fitmax = 475.
#         if amp == 12:
#             fitmin = 393.
#         if amp == 13:
#             fitmin = 390.
#         if amp == 10:
#             fitmin = 403.
          
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
        c3.SaveAs(OUTPUT_PATH + file_prefix + "fe55_amp_" + str(zfill(str(amp),2)) +"sprectrum" + FILE_TYPE)
        c3.SetLogy()
        c3.SaveAs(OUTPUT_PATH + file_prefix + "fe55_amp_" + str(zfill(str(amp),2)) +"sprectrum_logy" + FILE_TYPE)
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

#     DoAnalysis(INPUT_PATH)
#     exit()   


#= Fe55 - Get Gains =========================================================================
    if MAKE_FE55_SPECTRA:
        
#         DM_amplist = pickle.load(open(PICKLE_PATH + 'DM_', 'rb'))
#         DM_means, DM_mean_errors, DM_chisqrs = GetGains_Fe55(DM_amplist, 'DM')
#         DM_rel_errors = [(100 * (DM_mean_errors[i]/DM_means[i])) for i in range(N_AMPS)]
#         DM_average_error = np.asarray(DM_rel_errors, dtype = 'f8').sum()/16.0

        NG_amplist = pickle.load(open(PICKLE_PATH + 'NG_', 'rb'))
        NG_means, NG_mean_errors, NG_chisqrs = GetGains_Fe55(NG_amplist, 'NG')
        NG_rel_errors = [(100 * (NG_mean_errors[i]/NG_means[i])) for i in range(N_AMPS)]
        NG_average_error = np.asarray(NG_rel_errors, dtype = 'f8').sum()/16.0

#         exit()
        
        
#         print 'Avg DM fit error = %.4f%%' %DM_average_error
#         print 'Max DM error = %.4f%%' %max(DM_rel_errors)
        print
        print 'Avg NG fit error = %.4f%%' %NG_average_error
        print 'Max NG error = %.4f%%' %max(NG_rel_errors)

        for i in range(16):
#             print str(i) + '\t' + str(DM_means[i]) + '\t' + str(NG_means[i])
#             print str(i) + '\t' + str(DM_means[i])
            print str(i) + '\t' + str(NG_means[i])

    exit()


############## END CODE ##############
    
    all_time = time.time() - start_time
    for line in GLOBAL_OUT:
        print line
    print "All analysis done in %.2f seconds" %all_time 
    print '\n*** End code ***'
    
    
    
    
    
