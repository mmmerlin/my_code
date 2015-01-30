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
from lsst.afw.image import makeImageFromArray


from ROOT import TCanvas, TF1, TH1F, TGraph, TLegend, TGraphErrors, TPaveText
from array import array
import numpy as np
from numpy.core.defchararray import zfill
from root_functions import ListToHist
import gc

# my stuff
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from TrackFitting_DES import *
import TrackViewer as TV
import TrackFitting_DES


##########################################################################################
##########################################################################################
# things that won't really change
FILE_TYPE = ".png"
N_AMPS = 1

############

DISPLAY_LEVEL = 0
QUIET = False
#PROCESS_FILE_LIMIT = None
PROCESS_FILE_LIMIT = 999999

# Track finding options
THRESHOLD = 50
N_PIX_MIN = 2
GROW = 1
ISOTROPIC = True


XSIZE = 2160
YSIZE = 4146

b_trim = 20
t_trim = 20
l_trim = 80
r_trim = 80

# Cut options
TRACK_LENGTH_CUT = 150
ELLIPTICITY_CUT  = 3
CHISQ_CUT        = 10
R2_CUT           = 0.8

# Post processing options
MAKE_LANDAUS = True
GLOBAL_OUT = []

#===============================================================================


def DoAnalysis(input_path, pickle_file, SINGLE_FILE = True, SPECIFIC_FILE = None, SINGLE_POINT = False):
    dircontents = listdir(input_path)
    file_list = []
    for filename in dircontents:
        if str(input_path + filename).find('coadded') != -1: continue # skip coadd file
        if str(input_path + filename).find('.DS') != -1: continue
#         if str(input_path + filename).find('N10') == -1: continue
#         if filename != 'DECam_00134929.fits.fz_ext_N15.fits': continue
#         if filename != 'DECam_00134299.fits.fz_ext_N01.fits': continue
        if isfile(pickle_stem + filename + '.pickle'): continue # skip finished files
        if isfile(input_path + filename): file_list.append(filename) # skip directories
    
    
    if SPECIFIC_FILE != None:
        file_list = []
        file_list.append(SPECIFIC_FILE)
        SINGLE_FILE = True
    
    print "Processing %s files using settings:" %min(len(file_list), PROCESS_FILE_LIMIT)
    print "THRESHOLD = %s" %THRESHOLD
    print "N_PIX_MIN = %s" %N_PIX_MIN
    print "GROW = %s" %GROW
    print "ISOTROPIC = %s" %ISOTROPIC
    print
    print "Image Trimming:"
    print "L_trim: %s"%l_trim
    print "R_trim: %s"%r_trim
    print "T_trim: %s"%t_trim
    print "B_trim: %s\n"%b_trim

    for i, filename in enumerate(file_list):
        if PROCESS_FILE_LIMIT != None:
            if i >= PROCESS_FILE_LIMIT: break
        print "Processing %s of %s files (%.2f %% done)" %(i, len(file_list), 100 * float(i) / float(len(file_list)))
        if not QUIET: print "Current file = %s..." %filename

        pickle_filname = pickle_stem + filename + '.pickle'
        temp_image = afwImg.ImageF(input_path + filename)
        image = makeImageFromArray(temp_image.getArray()[b_trim:YSIZE-t_trim,l_trim:XSIZE - r_trim])
        del temp_image
#         ds9.mtv(image)
        
        maskedImg = afwImg.MaskedImageF(image)
        exposure = afwImg.ExposureF(maskedImg)
        
    # = Do finding ====================================================================
        threshold = afwDetect.Threshold(THRESHOLD, afwDetect.Threshold.VALUE)
        footPrintSet = afwDetect.FootprintSet(exposure.getMaskedImage(), threshold, "DETECTED", N_PIX_MIN)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, GROW, ISOTROPIC)
    
        footPrints = footPrintSet.getFootprints()
        if not QUIET: print "Found %s footprints in file %s"%(footPrints.size(), filename)
   
        tracklist = []
        if footPrints.size() >= 5000: # files with bright defects cause all sorts of problems
            print "Bad file - skipping..."
            continue
        else:
#            pointlist = [1,7,11,12,13,14,23]
#            pointlist = np.arange(20)
            for pointnum, footprint in enumerate(footPrints):
#                if pointnum in pointlist:
                heavy_footprint = afwDetect.HeavyFootprintF(footprint, maskedImg)
                stat = GetTrackStats(heavy_footprint, image, filename, save_track_data = True)
                tracklist.append(stat)
                del stat, heavy_footprint
#                 DrawStat(stat, True)
#                if SINGLE_POINT == True: exit()

        pickle.dump(tracklist, open(pickle_filname, 'wb'), pickle.HIGHEST_PROTOCOL)
        del maskedImg, exposure, threshold, footPrintSet, footPrints, tracklist
        gc.collect()
        if SINGLE_FILE == True: exit()
            
            

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

    for i in range(N_AMPS):
        print "Amp " + str(i) + " MPV = \t" + str(mpvs[i])

#    print "Worst cosmic fit has Chisq_red of %.2f" %chisqrs.sort[0]
#    chisqrs.sort(cmp=None, key=None, reverse=False)

    return mpvs, mpvs_errors, chisqrs


def DrawStat(stat, zoom_to_point = False):
#    if stat.ellipse_b == 0:
#        ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
    argstring = "@:"+str(4*stat.ellipse_Ixx)+','+str(4*stat.ellipse_Ixy)+','+str(4*stat.ellipse_Iyy) #multiply by four just to make it more exaggerated otherwise they all look like cirlces
    ds9.dot(argstring,stat.centroid_x,stat.centroid_y) #ellipse around the centroid
    ds9.dot("x",stat.centroid_x,stat.centroid_y)# cross on the peak
    displayUtils.drawBBox(stat.BBox, borderWidth=0.5) # border to fully encompass the bbox and no more
    if zoom_to_point: ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
    print 'length (diag,px) = %s, length (3D,true,um) = %s, flux = %s, npix = %s, dedx = %s' %(stat.diagonal_length_pixels, stat.length_true_um, stat.flux, stat.npix, stat.de_dx)
    print 'length x = %s, length_y = %s ' %(stat.xsize, stat.ysize)

#===============================================================================

def CollatePickles():
#     filter_list = ['N01','N02','N03','N04','N05','N06','N07','N08','N09','N10','N11','N12','N13','N14','N15','N16','N17','N18','N19','N20','N21','N22','N23','N24','N25','N26','N27','N28','N29','N30','N31','S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12','S13','S14','S15','S16','S17','S18','S19','S20','S21','S22','S23','S24','S25','S26','S27','S28','S29','S30','S31']
    filter_list = ['N03','N04','N05','N08','N12']
    in_path = "/mnt/hgfs/VMShared/Data/DES_analysis/20208080_thr50_gr2/"
    out_path = "/mnt/hgfs/VMShared/Data/DES_analysis/collated/"

    dirlist = listdir(in_path)

    for filter in filter_list:
        nfiles = 0
        datalist = []
        for filename in dirlist:
            if str.find(str(in_path + filename),filter) != -1:
                print "Loading %s"%(in_path + filename)
                nfiles += 1 
                for item in pickle.load(open(in_path + filename, 'rb')):
                    datalist.append(item)
        
        print "Unpickled %s tracks for sensor %s"%(len(datalist),filter)
        pickle.dump(datalist, open(out_path + filter + '.pickle', 'wb'), pickle.HIGHEST_PROTOCOL)
        print "Finished collating %s"%filter
        message = '%s files for sensor %s containing %s tracks'%(nfiles, filter, len(datalist))
        print message
        GLOBAL_OUT.append(message)
        del datalist
        
    for line in GLOBAL_OUT: print line
    print "Finished."


def DoPSF_Analysis(collated_pickle, sensor_name):
    from os import sys
    stdout = sys.stdout
    
    sys.stdout = open(OUTPUT_PATH + sensor_name + '.txt','w')
    rawlist = []
    for item in pickle.load(open(collated_pickle, 'rb')):
        rawlist.append(item)
    print "Unpickled %s tracks for sensor %s"%(len(rawlist),filter) 

    post_cuts = []
    nstats = 0
    rawstats = 0
    
    TRACK_LENGTH_CUT = 50
    DISCRIMINATOR_CUT = 600
    R2_CUT = 0.95
    N_SECS_PSF = 7
    
    ###################################################
####     Applying cuts
    
    for stat in rawlist:
        if GetEdgeType(stat) != "none" and GetEdgeType(stat) != "midline": continue
        
        if stat.diagonal_length_pixels >= TRACK_LENGTH_CUT:
            if stat.LineOfBestFit.R2 >= R2_CUT:
                if stat.discriminator < DISCRIMINATOR_CUT:
                    post_cuts.append(stat); nstats += 1
    
    print "%s stats loaded" %len(rawlist)
    print "%s after cuts" %len(post_cuts) 
    

    ######################################################
    #do analysis, deal with averaging and compiling return values
    xpoints, sigmas, sigma_errors = [], [], []
    av_sigma = [0.] * N_SECS_PSF
    av_sigma_error = [0.] * N_SECS_PSF
    npts = 0
    
    for i,stat in enumerate(post_cuts): 
        xs,s,se = MeasurePSF_in_Sections(stat.data, stat.LineOfBestFit, N_SECS_PSF, tgraph_filename=OUTPUT_PATH + str(i) + FILE_TYPE)
        assert N_SECS_PSF == len(xs) or len(xs) == 0
        for j in range(len(xs)):
            xpoints.append(xs[j])
            sigmas.append(s[j])
            sigma_errors.append(se[j])
            av_sigma[j] += s[j]
            av_sigma_error[j] += se[j]**2
        npts += 1
    
    for j in range(N_SECS_PSF): #make averages into averages
        av_sigma[j] /= float(npts)
        av_sigma_error[j] = (av_sigma_error[j]/float(npts))**0.5


    ######################################################
    # Averaged points
    c3 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT)
    gr2 = TGraphErrors()
    for i in range(N_SECS_PSF):
        gr2.SetPoint(int(i), float(xpoints[i]), av_sigma[i])   
        gr2.SetPointError(int(i), float(0), av_sigma_error[i])   
        
    fit_func = TF1("line","[1]*x + [0]", 0,100)
#     fit_func = TF1("line","TMath::Sqrt([1]*x) + [0]", 0, 100)
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
    
    gr2.GetYaxis().SetRangeUser(0,10)
    gr2.GetXaxis().SetRangeUser(0,250)
    
    legend_text = []
    legend_text.append('grad = ' + str(round(a,4)) + ' #pm ' + str(round(a_error,4)))
    legend_text.append('intercept = ' + str(round(y_int,2)) + ' #pm ' + str(round(y_int_error,2)) + ' #mum')
    legend_text.append('R^{2} = ' + str(round(R2,3)))
    textbox = TPaveText(0.5,0.25,0.85,0.5,"NDC")
    for line in legend_text: textbox.AddText(line)
    textbox.SetFillColor(0)
    textbox.SetTextSize(1.4* textbox.GetTextSize())
    textbox.Draw("same")
    
    c3.SaveAs(OUTPUT_PATH + sensor_name + '_' + str(N_SECS_PSF) + '_sections.png')
    c3.SaveAs(OUTPUT_PATH + sensor_name + '_' + str(N_SECS_PSF) + '_sections.pdf')
 
    ######################################################
    # y-intercept removed in quadrature
    c3 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT)
    gr3 = TGraphErrors()
    for i in range(N_SECS_PSF):
        gr3.SetPoint(int(i), float(xpoints[i]), (av_sigma[i]**2 - y_int**2)**0.5 )  
        gr3.SetPointError(int(i), float(0), (av_sigma_error[i]**2 + y_int_error**2)**0.5)    
#        gr3.SetPointError(int(i), float(0), abs(av_sigma_error[i]**2 - y_int_error**2)**0.5)    
      
    xmin = 0.
    xmax = 250.
    ymin = 0.
    ymax = float(10.)
    gr_scale_dummy = TGraph()
    gr_scale_dummy.SetPoint(0,xmin,ymin)
    gr_scale_dummy.SetPoint(1,xmax,ymax)
    gr_scale_dummy.SetMarkerColor(0)
    gr_scale_dummy.SetMarkerSize(0)
    gr_scale_dummy.Draw("AP") 
        
#     fit_func_2 = TF1("line","[1]*x + [0]", 0, 100)
    fit_func_2 = TF1("line","TMath::Sqrt([1]*x) + [0]", xmin, xmax)
#     fit_func_2 = TF1("line","TMath::Sqrt([1]*x)", 0, 100)
    fit_func_2.SetParameter(0,0.1)
    fit_func_2.SetParameter(1,2.0)
    fit_func_2.SetNpx(1000)
    gr3.Fit(fit_func_2, "ME0", "")
#     a = fit_func_2.GetParameter(1) 
#     a_error = fit_func_2.GetParError(1)
#     b = fit_func_2.GetParameter(0) 
#     b_error = fit_func_2.GetParError(0)
#     R2 = gr3.GetCorrelationFactor()**2
             
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
    legend_text.append('Intercept = ' + str(round(y_int,2)) + ' #pm ' + str(round(y_int_error,2)) + ' #mum')
#     legend_text.append('Slope = ' + str(round(a,4)) + ' #pm ' + str(round(a_error,4)))
#     legend_text.append('R^{2} = ' + str(round(R2,3)))
    textbox = TPaveText(0.15,0.65,0.5,0.85,"NDC")
    for line in legend_text:
        print line
        textbox.AddText(line)
    textbox.SetFillColor(0)
    textbox.SetTextColor(2)
    textbox.SetTextSize(1.4* textbox.GetTextSize())
#     textbox.Draw("same")
    
    chisqred = fit_func_2.GetChisquare() / fit_func_2.GetNDF()
    
    legend_text = []
    legend_text.append('Sqrt dependence:')
    legend_text.append('#chi^{2}_{Red} = ' + str(round(chisqred,3)))
    textbox2 = TPaveText(0.5,0.2,0.85,0.40,"NDC")
    for line in legend_text:
        print line
        textbox2.AddText(line)
    textbox2.SetFillColor(0)
    textbox2.SetTextColor(4)
#     textbox2.SetTextSize(1.4* textbox2.GetTextSize())
    textbox2.Draw("same")
    
    gr_scale_dummy.GetXaxis().SetRangeUser(0,250)
    
    gr_scale_dummy.GetXaxis().SetTitle('Average sensor depth (#mum)')
    gr_scale_dummy.GetYaxis().SetTitle('PSF #sigma (#mum)')
    
    c3.SaveAs(OUTPUT_PATH + sensor_name + '_quad_subtracted_' + str(N_SECS_PSF) + '_sections.png')
    c3.SaveAs(OUTPUT_PATH + sensor_name + '_quad_subtracted_' + str(N_SECS_PSF) + '_sections.pdf')
   
    print "Finished %s"%sensor_name
    sys.stdout = stdout



if __name__ == '__main__':
    start_time = time.time()
    import cPickle as pickle
    print "Running DES Analysis\n"
    SINGLE_FILE = False
    SINGLE_POINT = False
#     SPECIFIC_FILE = '/mnt/hgfs/VMShared/Data/DES_test/DECam_00134300.fits.fz_ext_S14.fits'
    SPECIFIC_FILE = None

#     pickle_stem = '/mnt/hgfs/VMShared/Data/DES_test/pickles/'
#     input_path = '/mnt/hgfs/VMShared/Data/DES_test/'


#     pickle_stem = '/mnt/hgfs/VMShared/Data/DES_analysis/20208080_thr50_gr2_N10_only/'
    pickle_stem = '/mnt/hgfs/VMShared/Data/DES_analysis/20208080_thr50_gr2/'
    input_path  = '/mnt/hgfs/VMShared/Data/DES_darks/split/'


#===============================================================================

    if SPECIFIC_FILE != None: SINGLE_FILE = True
     
#     DoAnalysis(input_path, pickle_stem, SINGLE_FILE, SPECIFIC_FILE=SPECIFIC_FILE, SINGLE_POINT=SINGLE_POINT)
#     for line in GLOBAL_OUT: print line
#     print 'Finished analysis'
#     exit()   
    
#     CollatePickles()
#     exit()
    
    
    OUTPUT_PATH = '/mnt/hgfs/VMShared/output/DES_analysis/Sensorwise_analysis/'
    
#     filter_list = ['N01','N02','N03','N04','N05','N06','N07','N08','N09','N10','N11','N12','N13','N14','N15','N16','N17','N18','N19','N20','N21','N22','N23','N24','N25','N26','N27','N28','N29','N30','N31','S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12','S13','S14','S15','S16','S17','S18','S19','S20','S21','S22','S23','S24','S25','S26','S27','S28','S29','S30','S31']
#     filter_list = ['N03','N04','N05','N06','N07','N08','N09','N10','N11','N12','N13','N14','N15','N16','N17','N18','N19','N20','N21','N22','N23','N24','N25','N26','N27','N28','N29','N30','N31','S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12','S13','S14','S15','S16','S17','S18','S19','S20','S21','S22','S23','S24','S25','S26','S27','S28','S29','S30','S31']
#     filter_list = ['S24','S25','S26','S27','S28','S29','S30','S31']
    filter_list = ['N03','N04','N05','N08','N12']
    for filter in filter_list:
        try:
            DoPSF_Analysis('/mnt/hgfs/VMShared/Data/DES_analysis/collated/' + filter + '.pickle', filter)
        except:
            GLOBAL_OUT.append('Failed %s'%filter)
    
    for line in GLOBAL_OUT: print line
    print "Finished all"
    exit()
    
    
    rawlist = []
    filter = 'N10'
#     file_list = []
#     for filename in listdir(pickle_stem):
#         if str.find(str(pickle_stem + filename),filter) != -1:
#             print "Loading %s"%(pickle_stem + filename)
#             for item in pickle.load(open(pickle_stem + filename, 'rb')):
#                 rawlist.append(item)
#     print "Unpickled %s tracks for sensor %s"%(len(rawlist),filter)
# 
#     pickle.dump(rawlist, open(pickle_stem + 'all_tracks.pickle', 'wb'), pickle.HIGHEST_PROTOCOL)
    
    
    for item in pickle.load(open(pickle_stem + 'all_tracks.pickle', 'rb')):
        rawlist.append(item)
    print "Unpickled %s tracks for sensor %s"%(len(rawlist),filter) 

#     exit()
    
    post_cuts = []
    nstats = 0
    rawstats = 0
    
    TRACK_LENGTH_CUT = 50
    DISCRIMINATOR_CUT = 600
    R2_CUT = 0.95
    N_SECS_PSF = 6
    
    ###################################################
####     Applying cuts
    dummy = TrackStats()
    dummy.diagonal_length_pixels
    
    for stat in rawlist:
        rawstats +=1
        if GetEdgeType(stat) != "none" and GetEdgeType(stat) != "midline": continue
        
        if stat.diagonal_length_pixels >= TRACK_LENGTH_CUT:
            if stat.LineOfBestFit.R2 >= R2_CUT:
                if stat.discriminator < DISCRIMINATOR_CUT:
                    post_cuts.append(stat); nstats += 1
    
    print "%s stats loaded" %len(rawlist)
    print "%s after cuts" %len(post_cuts) 
    
    ###################################################
    # Produce indivual track profiles
#     for i in range(1,2):
#         stat = post_cuts[i]
#         legend_text = []
#         legend_text.append('R^{2} = ' + str(round(stat.LineOfBestFit.R2,5)))
#         legend_text.append('Disc = ' + str(round(stat.discriminator,0)))
#         legend_text.append('Chisq = ' + str(stat.LineOfBestFit.chisq_red))
#         TV.TrackToFile_ROOT_2D_3D(stat.data, OUTPUT_PATH + str(i) + FILE_TYPE, fitline=stat.LineOfBestFit, legend_text=legend_text )
# #                     TrackFitting.MeasurePSF_Whole_track(stat.data, stat.LineOfBestFit)
#         TrackFitting_DES.MeasurePSF_in_Sections(stat.data, stat.LineOfBestFit, N_SECS_PSF, OUTPUT_PATH + str(i) + 'psf_vs_depth'  + '.png')
#     
#     exit()


    ############################################
##### Generating some plots
#     make_n_plots = 0
#     for i,stat in enumerate(post_cuts):
#         if i >= make_n_plots: break
#         legend_text = []
#        legend_text.append('R^{2} = ' + str(round(stat.LineOfBestFit.R2,5)))
#        legend_text.append('Disc = ' + str(round(stat.discriminator,0)))
#        legend_text.append('Chisq = ' + str(stat.LineOfBestFit.chisq_red))
#         TV.TrackToFile_ROOT_2D_3D(stat.data, OUTPUT_PATH + str(i) + 'both.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
#         TV.TrackToFile_ROOT_2D(stat.data, OUTPUT_PATH + 'colz_' + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit, plot_opt = 'colz' )
#         TV.TrackToFile_ROOT(stat.data, OUTPUT_PATH + 'lego20_' + str(i) + '.png', legend_text=legend_text, plot_opt = 'lego2 0' )



    ######################################################
    #do analysis, deal with averaging and compiling return values
    xpoints, sigmas, sigma_errors = [], [], []
    av_sigma = [0.] * N_SECS_PSF
    av_sigma_error = [0.] * N_SECS_PSF
    npts = 0
    
    for i,stat in enumerate(post_cuts): 
        xs,s,se = MeasurePSF_in_Sections(stat.data, stat.LineOfBestFit, N_SECS_PSF, tgraph_filename=OUTPUT_PATH + str(i) + FILE_TYPE)
        assert N_SECS_PSF == len(xs) or len(xs) == 0
        for j in range(len(xs)):
            xpoints.append(xs[j])
            sigmas.append(s[j])
            sigma_errors.append(se[j])
            av_sigma[j] += s[j]
            av_sigma_error[j] += se[j]**2
        npts += 1
    
    for j in range(N_SECS_PSF): #make averages into averages
        av_sigma[j] /= float(npts)
        av_sigma_error[j] = (av_sigma_error[j]/float(npts))**0.5

    
    
    ######################################################
##### All points on top of each other graph
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
    for i in range(N_SECS_PSF):
        gr2.SetPoint(int(i), float(xpoints[i]), av_sigma[i])   
        gr2.SetPointError(int(i), float(0), av_sigma_error[i])   
        
    fit_func = TF1("line","[1]*x + [0]", 0,100)
#     fit_func = TF1("line","TMath::Sqrt([1]*x) + [0]", 0, 100)
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
    
    gr2.GetYaxis().SetRangeUser(0,10)
    
    legend_text = []
    legend_text.append('grad = ' + str(round(a,4)) + ' #pm ' + str(round(a_error,4)))
    legend_text.append('intercept = ' + str(round(y_int,2)) + ' #pm ' + str(round(y_int_error,2)))
    legend_text.append('R^{2} = ' + str(round(R2,3)))
    textbox = TPaveText(0.5,0.25,0.85,0.5,"NDC")
    for line in legend_text: textbox.AddText(line)
    textbox.SetFillColor(0)
    textbox.SetTextSize(1.4* textbox.GetTextSize())
    textbox.Draw("same")
    
    c3.SaveAs(OUTPUT_PATH + '/psf_graph_averaged_' + str(N_SECS_PSF) + FILE_TYPE)
 
    ######################################################
    # y-intercept removed in quadrature
    c3 = TCanvas( 'canvas', 'canvas', CANVAS_WIDTH, CANVAS_HEIGHT)
    gr3 = TGraphErrors()
    for i in range(N_SECS_PSF):
        gr3.SetPoint(int(i), float(xpoints[i]), (av_sigma[i]**2 - y_int**2)**0.5 )  
        gr3.SetPointError(int(i), float(0), (av_sigma_error[i]**2 + y_int_error**2)**0.5)    
#        gr3.SetPointError(int(i), float(0), abs(av_sigma_error[i]**2 - y_int_error**2)**0.5)    
      
    xmin = 0.
    xmax = 250.
    ymin = 0.
    ymax = float(10.)
    gr_scale_dummy = TGraph()
    gr_scale_dummy.SetPoint(0,xmin,ymin)
    gr_scale_dummy.SetPoint(1,xmax,ymax)
    gr_scale_dummy.SetMarkerColor(0)
    gr_scale_dummy.SetMarkerSize(0)
    gr_scale_dummy.Draw("AP") 
        
#     fit_func_2 = TF1("line","[1]*x + [0]", 0, 100)
    fit_func_2 = TF1("line","TMath::Sqrt([1]*x) + [0]", xmin, xmax)
#     fit_func_2 = TF1("line","TMath::Sqrt([1]*x)", 0, 100)
    fit_func_2.SetParameter(0,0.1)
    fit_func_2.SetParameter(1,2.0)
    fit_func_2.SetNpx(1000)
    gr3.Fit(fit_func_2, "ME0", "")
#     a = fit_func_2.GetParameter(1) 
#     a_error = fit_func_2.GetParError(1)
#     b = fit_func_2.GetParameter(0) 
#     b_error = fit_func_2.GetParError(0)
#     R2 = gr3.GetCorrelationFactor()**2
             
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
    legend_text.append('Intercept = ' + str(round(y_int,2)) + ' #pm ' + str(round(y_int_error,2)) + ' #mum')
#     legend_text.append('Slope = ' + str(round(a,4)) + ' #pm ' + str(round(a_error,4)))
#     legend_text.append('R^{2} = ' + str(round(R2,3)))
    textbox = TPaveText(0.15,0.65,0.5,0.85,"NDC")
    for line in legend_text:
        print line
        textbox.AddText(line)
    textbox.SetFillColor(0)
    textbox.SetTextColor(2)
    textbox.SetTextSize(1.4* textbox.GetTextSize())
#     textbox.Draw("same")
    
    chisqred = fit_func_2.GetChisquare() / fit_func_2.GetNDF()
    
    legend_text = []
    legend_text.append('Sqrt dependence:')
    legend_text.append('#chi^{2}_{Red} = ' + str(round(chisqred,3)))
    textbox2 = TPaveText(0.5,0.2,0.85,0.40,"NDC")
    for line in legend_text:
        print line
        textbox2.AddText(line)
    textbox2.SetFillColor(0)
    textbox2.SetTextColor(4)
#     textbox2.SetTextSize(1.4* textbox2.GetTextSize())
    textbox2.Draw("same")
    
    
    gr_scale_dummy.GetXaxis().SetTitle('Average sensor depth (#mum)')
    gr_scale_dummy.GetYaxis().SetTitle('PSF #sigma (#mum)')
    
    c3.SaveAs(OUTPUT_PATH + 'psf_graph_averaged_quad_subtracted' + str(N_SECS_PSF) + FILE_TYPE)
   
    print "Finished"
    exit()
    
    
#    OUTPUT_PATH = '/home/mmmerlin/output/PSF/'
#    i = 0
#    for stat in rawlist:
#        if stat.npix <= 50:
#            i += 1
#            legend_text = []
#            legend_text.append('npix = ' + str(stat.npix))
#            TV.TrackToFile_ROOT_2D(stat.data, OUTPUT_PATH + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
#            if i >25: break
#            
    
    for i,stat in enumerate(post_cuts):
#        if i <> 3: continue
        legend_text = []
        legend_text.append('R^{2} = ' + str(round(stat.LineOfBestFit.R2,5)))
        legend_text.append('Disc = ' + str(round(stat.discriminator,0)))
#        legend_text.append('Chisq = ' + str(stat.LineOfBestFit.chisq_red))
#        TV.TrackToFile_ROOT_2D_3D(stat.data, OUTPUT_PATH + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
    
    
    ListToHist([stat.discriminator for stat in rawlist], '/home/mmmerlin/output/PSF/raw_disc.pdf', histmax = 5000)
    ListToHist([stat.discriminator for stat in post_cuts], '/home/mmmerlin/output/PSF/post_cut_disc.pdf', histmin = 0, histmax = 500, nbins = 50)
    ListToHist([stat.npix for stat in rawlist], '/home/mmmerlin/output/PSF/npx_hist.pdf', histmin = 0, histmax = 100, nbins = 100)
        



############## END CODE ##############
    
    all_time = time.time() - start_time
    for line in GLOBAL_OUT:
        print line
    print "All analysis done in %.2f seconds" %all_time 
    exit()
    
############# DONE ################
  


