import lsst.afw.detection   as afwDetect
import lsst.afw.display.utils as displayUtils
#from lsst.pex.config import Config, Field, ConfigField, makePolicy
from lsst.meas.algorithms.detection import (SourceDetectionTask, estimateBackground, BackgroundConfig,)
import lsst.meas.algorithms as measAlg


from ROOT import TCanvas,TF1, TH1F, TGraph
import numpy as np
from os.path import expanduser
import lsst.afw.image       as afwImg
import lsst.afw.display.ds9 as ds9

from TrackFitting import *
from image_assembly import AssembleImage, MakeBiasImage, GetImage_SingleAmp
from os import listdir
from os.path import isfile

from PlotProduction import OUTPUT_PATH, FILE_TYPE
from timeit import itertools
import TrackFitting
from ImageStat import Stat

import time
#t0 = time.time()
#dt = time.time() - t0
#print "Time was %.2f seconds" %dt 

FILE_LIMIT = 99999
# SKIP_N_FILES = FILE_LIMIT -1

DISPLAY_LEVEL = 1
SINGLE_FILE = False
SINGLE_POINT = False
SPECIFIC_FILE = None
#SPECIFIC_FILE = '/home/mmmerlin/Desktop/VMShared/Data/all_darks/113-03_dark_dark_999.00_035_20140709120811.fits'

pickle_file = '/mnt/hgfs/VMShared/output/datasets/temp'
# pickle_file = '/mnt/hgfs/VMShared/output/datasets/edge_large_grow'
# pickle_file = '/mnt/hgfs/VMShared/output/datasets/edge_tracks_200thr_gr2_px2_gain_corrected'
input_path = '/mnt/hgfs/VMShared/Data/all_darks/'


#SPECIFIC_FILE = home_dir + '/Desktop/VMShared/Data/small_fe55_set/113-03_fe55_fe55_010.00_022_20140709224009.fits'


#===============================================================================


def DoAnalysis(input_path, pickle_file, SINGLE_FILE = True, SPECIFIC_FILE = None, SINGLE_POINT = False):
    t0 = time.time()
    
    thresholdValue = 200
    npixMin = 10
    grow = 2
    isotropic = True
    
    if DISPLAY_LEVEL >= 1:
        try: # initialise DS9, deal with a bug in its launching
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'
        print 'called ds9 to display' 
        
#= Open image, assemble, background subtract ===============================================================
    
    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'
#    bias_input_path = input_path + 'bias/'
#    bias_image  = MakeBiasImage(bias_input_path, metadata_filename)
    
    dircontents = listdir(input_path)
    file_list = []
    for thisfile in dircontents:
        filename = input_path + thisfile
        if str(filename).find('coadded') != -1: continue # skip coadd file
        if isfile(filename): file_list.append(filename) # skip bias dir
    
    if SPECIFIC_FILE != None:
        file_list = []
        file_list.append(SPECIFIC_FILE)
        SINGLE_FILE = True
    
    if not SINGLE_FILE: print "Processing %s files..." %len(file_list)

    nleft, nright, ntop, nbottom, nmidline = 0,0,0,0,0
    statslist = []
    
    for i,filename in enumerate(file_list):
#         if i < SKIP_N_FILES: continue
        if i >= FILE_LIMIT: continue
        print "Processing %s..." %filename
        
        gains = [3.315808402,3.327915473,3.378822094,3.344825272,3.32604176,3.380261393,3.339747603,3.357838184,3.294004911,3.245531036,3.219743995,3.225160702,3.254285149,3.294630888,3.231197772,3.25006113] #113-03 gains
        
        image = AssembleImage(filename, metadata_filename, True, gain_correction_list=gains)# make image, subtract background and assemble exposure
        maskedImg = afwImg.MaskedImageF(image)
        exposure = afwImg.ExposureF(maskedImg)
        
        if DISPLAY_LEVEL >= 1 and SINGLE_FILE == True: ds9.mtv(image)
    
    # = Do finding ====================================================================
        threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
        footPrintSet = afwDetect.FootprintSet(exposure.getMaskedImage(), threshold, "DETECTED", npixMin)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
    
        footPrints = footPrintSet.getFootprints()
    
#        if footPrints.size() >= 800: # files with bright defects cause all sorts of problems
#            print "Bad file - skipping..."
#            continue
    
        print "Found %s footprints"%len(footPrints)
    
        footprint_skip = 2
        count = 0
    
        for footprint in footPrints:
            heavy_footprint = afwDetect.HeavyFootprintF(footprint, maskedImg)
            stat = GetTrackStats(heavy_footprint, image, filename, save_track_data = True)
#             statslist.append(stat)
#             DrawStat(stat)
            
#             if GetEdgeType(stat) == "left":
#                 count += 1
#                 if stat.length_true_um < 200: continue
#                 if count < (footprint_skip + 1): continue
#                 ds9.mtv(image)
#                 print "Found " + GetEdgeType(stat)
#                 DrawStat(stat)
#                 
#                 statslist.append(stat)
# #                 exit()
#                 break
            
            
#             if stat.left_track == True or stat.right_track == True:
#             if stat.bottom_track == True or stat.top_track == True:
            if True:
#                 if stat.length_x_um > 250: #and stat.length_y_um > stat.length_x_um:
#                 if stat.length_true_um > 4000:# and stat.length_y_um > 1000:
                if stat.length_true_um > 1000 and stat.discriminator > 100000:# and stat.length_y_um > 1000:
                    count += 1
                    if count <= footprint_skip: continue
                    ds9.mtv(image)
                    
                    DrawStat(stat)
                    exit()
                    
                nleft += 1
                statslist.append(stat)
            
             
             
#             if stat.left_track == True:
# #                 DrawStat(stat)
#                 nleft += 1
#                 statslist.append(stat)
#                     
#             if stat.right_track == True:
# #                 DrawStat(stat)
#                 nright += 1
#                 statslist.append(stat)
#                     
#             if stat.top_track == True:
# #                 DrawStat(stat)
#                 ntop += 1
#                 statslist.append(stat)
#                     
#             if stat.bottom_track == True:
# #                 DrawStat(stat)
#                 nbottom += 1
#                 statslist.append(stat)
#     
#             if stat.midline_track == True:
# #                 DrawStat(stat)
#                 nmidline += 1
#                 statslist.append(stat)
                 
                
            if SINGLE_POINT == True: break
        
        if SINGLE_FILE == True:
            break
        else:
            print '%s footprints found in %s' %(footPrints.size(), filename)
             
             
    dt = time.time() - t0
    print "Data analysed in %.2f seconds" %dt 
    
    print "n midline %s" %nmidline
    print "n left %s" %nleft
    print "n right %s" %nright
    print "n top %s" %ntop
    print "n bottom %s" %nbottom
    
    t0 = time.time()
    pickle.dump(statslist, open(pickle_file, 'wb'))
    dt = time.time() - t0
    print "Pickled %s tracks in %.2f seconds" %(len(statslist),dt) 
#===============================================================================



def DrawStat(stat):
    if stat.ellipse_b == 0:
        ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
        
    argstring = "@:"+str(4*stat.ellipse_Ixx)+','+str(4*stat.ellipse_Ixy)+','+str(4*stat.ellipse_Iyy) #multiply by four just to make it more exaggerated otherwise they all look like cirlces
    ds9.dot(argstring,stat.centroid_x,stat.centroid_y) #ellipse around the centroid
    ds9.dot("x",stat.centroid_x,stat.centroid_y)# cross on the peak
    displayUtils.drawBBox(stat.BBox, borderWidth=0.5) # border to fully encompass the bbox and no more
    ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
    print 'length (diag,px) = %s, length (3D,true,um) = %s, flux = %s, npix = %s, dedx = %s' %(stat.diagonal_length_pixels, stat.length_true_um, stat.flux, stat.npix, stat.de_dx)


#===============================================================================

def DrawStatFromScratch(stat, bgsubtract):
    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'
    image = AssembleImage(stat.filename, metadata_filename, bgsubtract)
    print "track at %s,%s in %s"%(stat.centroid_x,stat.centroid_y,stat.filename)
    ds9.mtv(image)
#    exit()
    argstring = "@:"+str(4*stat.ellipse_Ixx)+','+str(4*stat.ellipse_Ixy)+','+str(4*stat.ellipse_Iyy) #multiply by four just to make it more exaggerated otherwise they all look like cirlces
    ds9.dot(argstring,stat.centroid_x,stat.centroid_y) #ellipse around the centroid
    ds9.dot("x",stat.centroid_x,stat.centroid_y)# cross on the peak
    displayUtils.drawBBox(stat.BBox, borderWidth=0.5) # border to fully encompass the bbox and no more
    ds9.zoom(22, stat.centroid_x,stat.centroid_y, 0) # use to zoom to a single point
#    print 'length (diag,px) = %s, length (3D,true,um) = %s, flux = %s, npix = %s, dedx = %s' %(stat.diagonal_length_pixels, stat.length_true_um, stat.flux, stat.npix, stat.de_dx)



def DrawStatCustom(stat,x,y):
    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'
    image = AssembleImage(stat.filename, metadata_filename, True)
    print "track at %s,%s in %s"%(stat.centroid_x,stat.centroid_y,stat.filename)
    ds9.mtv(image)
#    exit()
#    ds9.dot(argstring,stat.centroid_x,stat.centroid_y) #ellipse around the centroid
#    ds9.dot("x",stat.centroid_x,stat.centroid_y)# cross on the peak
#    displayUtils.drawBBox(stat.BBox, borderWidth=0.5) # border to fully encompass the bbox and no more
    ds9.zoom(22, x,y, 0) # use to zoom to a single point
#    print 'length (diag,px) = %s, length (3D,true,um) = %s, flux = %s, npix = %s, dedx = %s' %(stat.diagonal_length_pixels, stat.length_true_um, stat.flux, stat.npix, stat.de_dx)

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


if __name__ == '__main__':
    import pickle
    print "Running cosmic analysis\n"


#===============================================================================

    if SPECIFIC_FILE != None: SINGLE_FILE = True
    
    DoAnalysis(input_path, pickle_file, SINGLE_FILE, SPECIFIC_FILE=SPECIFIC_FILE, SINGLE_POINT=SINGLE_POINT)
    
    exit()
    
    t0 = time.time()
    rawlist = pickle.load(open(pickle_file, 'rb'))
    dt = time.time() - t0
    print "%s stats unpickled in %.2f seconds" %(len(rawlist),dt) 
    
    
    if DISPLAY_LEVEL > 1 and SINGLE_FILE == True:
        for stat in rawlist:
            DrawStat(stat)
 
    
    #for edge tracks:
    ntracks = 0
    skip = 3
    for stat in rawlist:
#        if IsEdgeTrack(stat):
#            DrawStatFromScratch(stat)
#            exit()
        
        if GetEdgeType(stat) == "left":
            if stat.diagonal_length_pixels >= 70:
#                if stat.filename == '/home/mmmerlin/Desktop/VMShared/Data/all_darks/113-03_dark_dark_999.00_001_20140710002405.fits': continue
                if not Cut_Ellipticity(stat, 4): continue
                if (stat.length_x_um/stat.length_y_um) > 1.05 or (stat.length_x_um/stat.length_y_um) < 0.95: continue
                
                if skip <> 0:
                    skip -= 1
                else:
                    DrawStatFromScratch(stat, False)
                    exit()
                    
#                DrawStatCustom(stat,2260,2001)
                ntracks += 1
            
    print ntracks
    exit()
 
 
 
    #apply cuts:
    statslist = []
#    statslist = rawlist # <-- no cuts

    for stat in rawlist:
        if Cut_Length(stat, 150):
            if Cut_Ellipticity(stat, 3):
                statslist.append(stat)

    print "%s after cuts" %len(statslist)



# == ROOT STUFF =============================================================================
    histmin = 0
    histmax = 100
    nbins = 100

    c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    landau_hist = TH1F('dE/dx', 'dE/dx',nbins,histmin,histmax)
    for stat in statslist:
        landau_hist.Fill(stat.de_dx)
    landau_hist.Draw()
    landau_hist.GetXaxis().SetTitle('dE/dx (ADU/#mum)')
    landau_hist.GetYaxis().SetTitle('Frequency')
    
    
    from root_functions import LanGausFit, LandauFit
    langaus_func = LanGausFit(landau_hist, 10,65)
    langaus_func.SetNpx(1000)
    langaus_func.Draw("same")
    
   
    landau_func = LandauFit(landau_hist, 10,65, True)
    landau_func.SetNpx(1000)
    landau_func.SetLineStyle(5)
    landau_func.SetLineColor(4)
    landau_func.SetLineWidth(5)
#    landau_func.Draw("same")
    
    
    c3.SaveAs(OUTPUT_PATH + "dedx_hist" + FILE_TYPE)
    del c3
    del landau_hist

    
    
    #===========================================================================
    histmin = 0
    histmax = 1000
    nbins = 50

    c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    landau_hist = TH1F('Track Length', 'Track Length',nbins,histmin,histmax)
    for stat in statslist:
        landau_hist.Fill(stat.length_true_um)
    landau_hist.Draw()
    c3.SaveAs(OUTPUT_PATH + "length" + FILE_TYPE)
    landau_hist.GetXaxis().SetTitle('Track Length (#mum)')
    landau_hist.GetYaxis().SetTitle('Frequency')
    del c3
    del landau_hist
    
    
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
    histmin = 0
    histmax = 50000
    nbins = 50

    c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    landau_hist = TH1F('landauhist', 'landauhist',nbins,histmin,histmax)
    for stat in statslist:
        landau_hist.Fill(stat.flux)
    landau_hist.Draw()
    landau_hist.GetXaxis().SetTitle('Footprint Flux (ADU)')
    landau_hist.GetYaxis().SetTitle('Frequency')
    c3.SaveAs(OUTPUT_PATH + "flux_hist" + FILE_TYPE)
    del c3
    del landau_hist
   
    
    #===========================================================================
    histmin = 0
    histmax = 5000
    nbins = 50

    c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    landau_hist = TH1F('landauhist', 'landauhist',nbins,histmin,histmax)
    for stat in statslist:
        landau_hist.Fill(stat.flux / stat.diagonal_length_pixels)
    landau_hist.Draw()
    landau_hist.GetXaxis().SetTitle('Flux per pixel (ADU)')
    landau_hist.GetYaxis().SetTitle('Frequency')
    c3.SaveAs(OUTPUT_PATH + "flux_per_projected_pixel" + FILE_TYPE)
    del c3
    del landau_hist
    
    
    
    #===========================================================================
    histmin = 0
    histmax = 100
    nbins = 100

    c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    landau_hist = TH1F('landauhist', 'landauhist',nbins,histmin,histmax)
    for stat in rawlist:
        landau_hist.Fill(stat.de_dx)
    landau_hist.GetXaxis().SetTitle('dE/dx (ADU/#mum)')
    landau_hist.GetYaxis().SetTitle('Frequency')
    landau_hist.Draw()
    c3.SaveAs(OUTPUT_PATH + "raw_de_dx" + FILE_TYPE)
    del c3
    del landau_hist
    
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
