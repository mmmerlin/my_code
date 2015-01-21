import os
from os.path import expanduser
import numpy as np
import pylab as pl
import string        
               
import time
from __builtin__ import len

from ROOT import TCanvas, TF1, TH1F
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import GetRawTimecodes_SingleFile
import cPickle as pickle
from root_functions import Browse



OUTPUT_PATH = '/mnt/hgfs/VMShared/NSLS_temp/'
FILE_TYPE = ".pdf"

if __name__ == '__main__':
    print "Running Auto-correlation analysis\n "
    
    NFILES = 1
    
    path = '/mnt/hgfs/VMShared/Data/NSLS/Pre-beamdump/Run_00_thr_325/'

      
    timecodemin = 0
    timecodemax = 11809
    nbins = timecodemax - timecodemin
    
    correl_hist = TH1F('', 'Timecodes',nbins,timecodemin,timecodemax)
    binsize = correl_hist.GetBinLowEdge(3) - correl_hist.GetBinLowEdge(2)
    assert binsize == 1
    
    
    files = []
    for filename in os.listdir(path):
        files.append(path + filename)

    
    for numfiles, filename in enumerate(files):
        if numfiles >= NFILES: break
        
        c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        filehist = TH1F('', 'Timecodes',nbins,timecodemin,timecodemax)
        
        timecodes = GetRawTimecodes_SingleFile(filename,15,240,15,240)
        for code in timecodes:
            if code != 11810:
                filehist.Fill(code)
        
        for i in range(11810):
        
        
        filehist.Draw()
        c1.SaveAs(OUTPUT_PATH + "temp.png")
        print "loaded %s timecodes from file %s"%(len(timecodes),numfiles)
        
        exit()
            
            
    
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    
    
    correl_hist.Draw()
    correl_hist.GetXaxis().SetTitle('#Delta t')
    c1.SaveAs(OUTPUT_PATH + "correlation_histogram" + FILE_TYPE)
    
    
    
    
    


    
    print '\n***End code***'      