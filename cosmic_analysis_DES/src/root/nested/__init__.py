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

# my stuff
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from TrackFitting_DES import *


##########################################################################################
##########################################################################################
# things that won't really change
OUTPUT_PATH = "/mnt/hgfs/VMShared/Data/DES_test/"
FILE_TYPE = ".pdf"
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
t_trim = 16
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
        


def DoAnalysis(input_path, pickle_file, SINGLE_FILE = True, SPECIFIC_FILE = None, SINGLE_POINT = False):
    dircontents = listdir(input_path)
    file_list = []
    for filename in dircontents:
        if str(input_path + filename).find('coadded') != -1: continue # skip coadd file
        if str(input_path + filename).find('.DS') != -1: continue
#         if str(input_path + filename).find('N10') == -1: continue
        if isfile(input_path + filename): file_list.append(filename) # skip bias dir
    
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
        if footPrints.size() >= 2000: # files with bright defects cause all sorts of problems
            print "Bad file - skipping..."
            continue
        else:
#            pointlist = [1,7,11,12,13,14,23]
#            pointlist = np.arange(20)
            for pointnum, footprint in enumerate(footPrints):
#                if pointnum in pointlist:
                heavy_footprint = afwDetect.HeavyFootprintF(footprint, maskedImg)
                stat = GetTrackStats(heavy_footprint, image, filename, save_track_data = True)
#                 if stat.xsize - (XSIZE - l_trim - r_trim) == 0: continue #skip bad rows (also tracks which traverse whole sensor)
#                 if stat.ysize - (YSIZE - t_trim - b_trim) == 0: continue #skip bad columns (also tracks which traverse whole sensor)
                tracklist.append(stat)
#                 DrawStat(stat, True)
#                if SINGLE_POINT == True: exit()

        pickle.dump(tracklist, open(pickle_filname, 'wb'))
        if SINGLE_FILE == True: exit()
    

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
    print "Running DES Analysis\n"
    SINGLE_FILE = False
    SINGLE_POINT = False
#     SPECIFIC_FILE = '/mnt/hgfs/VMShared/Data/DES_test/DECam_00134299.fits.fz_ext_S18.fits'
#     SPECIFIC_FILE = '/mnt/hgfs/VMShared/Data/DES_test/DECam_00134300.fits.fz_ext_N24.fits'
#     SPECIFIC_FILE = '/mnt/hgfs/VMShared/Data/DES_test/DECam_00134300.fits.fz_ext_S14.fits'
    SPECIFIC_FILE = None

#     pickle_stem = '/mnt/hgfs/VMShared/Data/DES_test/pickles/'
#     input_path = '/mnt/hgfs/VMShared/Data/DES_test/'


    pickle_stem = '/mnt/hgfs/VMShared/Data/DES_darks/split/pickles/'
    input_path  = '/mnt/hgfs/VMShared/Data/DES_darks/split/'


#===============================================================================

    if SPECIFIC_FILE != None: SINGLE_FILE = True
    
    DoAnalysis(input_path, pickle_stem, SINGLE_FILE, SPECIFIC_FILE=SPECIFIC_FILE, SINGLE_POINT=SINGLE_POINT)
    print 'Finished analysis'
    exit()   
    
    
    rawlist = []
    filter = 'N10'
    file_list = []
    for filename in listdir(pickle_stem):
        if str.find(str(pickle_stem + filename),filter) != -1:
            print "Loading %s"%(pickle_stem + filename)
            for item in pickle.load(open(pickle_stem + filename, 'rb')):
                rawlist.append(item)
            
    print "Unpickled %s tracks for sensor %s"%(len(rawlist),filter)
    exit()
    
    post_cuts = []
    nstats = 0
    rawstats = 0
    
    TRACK_LENGTH_CUT = 1000
    aspect_limit = 1
    aspect_rejected = 0

    ###################################################
####     Applying cuts, optionally re-saving dataset
    for stat in rawlist:
        rawstats +=1
        if stat.length_true_um >= TRACK_LENGTH_CUT:
            if stat.LineOfBestFit.R2 > 0.95:
                if stat.discriminator < 500:
                    if GetEdgeType(stat) != "none" and GetEdgeType(stat) != "midline": continue
#                    aspect_ratio = (stat.length_x_um / stat.length_y_um)
#                    if aspect_ratio > aspect_limit or aspect_ratio < (1/aspect_limit):
#                        TV.TrackToFile_ROOT_2D_3D(stat.data, OUTPUT_PATH + '/aspect' + str(aspect_rejected) + '.png', fitline=stat.LineOfBestFit )
#                        aspect_rejected += 1
#                    else:
                    post_cuts.append(stat); nstats += 1
    
    ###################################################
    # Produce indivual track profiles
    if True:
        for stat in rawlist:
            rawstats +=1
            if stat.length_true_um >= 800:
                if stat.discriminator > 2000:
                        aspect_ratio = (stat.length_x_um / stat.length_y_um)
                        if aspect_ratio < 0.05:
#                             if aspect_rejected == 13:
                
                            TV.TrackToFile_ROOT_2D_3D(stat.data, OUTPUT_PATH + '/delta' + str(aspect_rejected) + '.png', fitline=stat.LineOfBestFit )
    #                TrackFitting.MeasurePSF_Whole_track(stat.data, stat.LineOfBestFit)
    #                TrackFitting.MeasurePSF_in_Sections(stat.data, stat.LineOfBestFit, 6, OUTPUT_PATH + '/aspect13Tgraph' + '.png')
                
                
#                     aspect_rejected += 1
                        
                        
                        
#            else:
#                post_cuts.append(stat); nstats += 1
#     exit()    
    
    print "%s stats loaded" %len(rawlist)
    print "%s after cuts" %nstats

#    cosmic_pickle_file = home_dir + '/output/datasets/clean_cosmics_L400_R095_D500'
#    pickle.dump(post_cuts, open(cosmic_pickle_file, 'wb'), pickle.HIGHEST_PROTOCOL)
#    exit()


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
    textbox.Draw("same")
    
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
    
    c3.SaveAs(OUTPUT_PATH + 'psf_graph_averaged_quad_subtracted' + str(nsecs) + '.pdf')
   
    
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
  

