import lsst.afw.detection   as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.meas.algorithms as measAlg


from ROOT import TCanvas,TF1, TH1F, TGraph
import numpy as np
from os.path import expanduser
import lsst.afw.image       as afwImg
import lsst.afw.display.ds9 as ds9


from PlotProduction import OUTPUT_PATH, FILE_TYPE
from timeit import itertools
import TrackFitting
from ImageStat import Stat

from time import sleep

from image_assembly import AssembleImage, MakeBiasImage, GetImage_SingleAmp
from os import listdir
from os.path import isfile
from numpy.core.defchararray import zfill

#===============================================================================




if __name__ == '__main__':
    print "Running background analysis\n"
    DISPLAY_LEVEL = 0
    SINGLE_FILE = False
    SINGLE_POINT = False
    SPECIFIC_FILE = None
#    SPECIFIC_FILE = '/home/mmmerlin/Desktop/VMShared/Data/all_darks/113-03_dark_dark_999.00_035_20140709120811.fits'

    home_dir = expanduser("~")
    input_path = home_dir + '/Desktop/VMShared/Data/all_darks/'
#    SPECIFIC_FILE = home_dir + '/Desktop/VMShared/Data/long_darks_20140708/113-03_dark_dark_999.00_035_20140709120811.fits'

    if SPECIFIC_FILE != None: SINGLE_FILE = True


#===============================================================================


    


    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'

    dircontents = listdir(input_path)
    file_list = []
    for thisfile in dircontents:
        filename = input_path + thisfile
        if str(filename).find('coadded') != -1: continue # skip coadd file
        if isfile(filename): file_list.append(filename) # skip directories
    
    if SPECIFIC_FILE != None:
        file_list = []
        file_list.append(SPECIFIC_FILE)
        SINGLE_FILE = True
    
    if not SINGLE_FILE: print "Processing %s files..." %len(file_list)

    hist_array = []
    
    for filenum,filename in enumerate(file_list):
        print "Processing %s..." %filename
        
        image = AssembleImage(filename, metadata_filename, True)# make image, subtract background and assemble exposure
        maskedImg = afwImg.MaskedImageF(image)
        exposure = afwImg.ExposureF(maskedImg)
    
    
        #===========================================================================
        histmin = 0
        histmax = 50000
        nbins = 201
    
    
        c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        hist_array.append(TH1F('myhist' + str(zfill(str(filenum),3)), 'myhist' + str(zfill(str(filenum),3)),nbins,histmin,histmax))
        print "filenum = " + str(filenum)
        for value in image.getArray().flatten():
            hist_array[filenum].Fill(value)
        hist_array[filenum].Draw()
        hist_filename = OUTPUT_PATH + "without_background" + str(zfill(str(filenum),3)) + FILE_TYPE
        c1.SetLogy()
        c1.SaveAs(hist_filename)
        del c1

#        if filenum == 1:
#            break
    
#===========================================================================
    
    histmin = 0
    histmax = 50000
    nbins = 201
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    master_hist = TH1F('myhist', 'myhist',nbins,histmin,histmax)
    for hist in hist_array:
        master_hist.Add(hist)
    master_hist.Draw()
    c1.SaveAs(OUTPUT_PATH + "without_background_masterhist_no_log" + FILE_TYPE)
    c1.SetLogy()
    c1.SaveAs(OUTPUT_PATH + "without_background_masterhist_with_log" + FILE_TYPE)
    del c1


    #===========================================================================

    

    print '\n*** End code ***'
    exit()
    
