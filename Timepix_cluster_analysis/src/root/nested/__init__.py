import os
from os.path import expanduser, join
from os import listdir
import numpy as np
import string        
               
from ROOT import TCanvas, TF1, TH1F, TGraph
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import GetXYTarray_SingleFile, MakeCompositeImage_Timepix
from math import floor

glitch_threshold = 5000


OUTPUT_PATH = '/mnt/hgfs/VMShared/output/chem_new_sensors_first_light/'
FILE_TYPE = ".png"


if __name__ == '__main__':
    print "Running QE analysis\n "
    path     = '/mnt/hgfs/VMShared/Data/chem_new_sensors_first_light/7343-6(50nm)/'
    
    
    #########################
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    
    n_glitches = 0
    n_goodframes = 0
    n_pix_hits = 0
    nfiles = 0.
    
    templist = []
    for filename in os.listdir(path):
        xs, ys, ts = GetXYTarray_SingleFile(path + filename, 1, 254, 1, 254)
        assert len(xs) == len(ys) == len(ts)
        if len(xs) >= glitch_threshold: print "skipped glitch frame"; n_glitches +=1; continue
        n_goodframes += 1
        nfiles += 1
        n_pix_hits += len(ts)
        
    pixels_per_frame = float(n_pix_hits) / float(n_goodframes)
    print "av. pixels per frame = %.2f"%pixels_per_frame
    
    intensity_array = MakeCompositeImage_Timepix(path, 1, 253, 1, 253, 0, 9999, -99999, 99999, return_raw_array=True)
    
    print 'nfiles = %s'%nfiles
#     print 'badpixel_threshold = %s'%badpixel_threshold
    
    for thr_range in range(1,1001):
        badpixel_threshold = (float(thr_range)/1000.)*(nfiles)
        index = np.where(intensity_array <= badpixel_threshold)
        intensity_sum = intensity_array[index].sum(dtype = np.float64)
        print str(thr_range/10.) + '\t' + str(intensity_sum/nfiles)
    
#     print intensity_sum
#     print intensity_sum / float(nfiles)
    
#    from root_functions import ListToHist
#    ListToHist(templist, path + "ts_hist.pdf", nbins = 300, histmin = 0, histmax = 300)
#    exit()
    

    
    
    
    
    
    
    print '\n***End code***'      