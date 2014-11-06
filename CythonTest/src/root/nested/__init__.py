import os
from os.path import expanduser
import numpy as np
import pylab as pl
import string        
               
import time

from ROOT import TCanvas, TF1, TH1F
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import GetRawTimecodes_SingleFile
import cPickle as pickle
from root_functions import Browse


home_dir  = expanduser('~')
OUTPUT_PATH = "/home/mmmerlin/output/"
FILE_TYPE = ".pdf"
PICKLE_FILE = home_dir + '/output/datasets/NSLS_pickle'


def GetNpTimecodes(filename, winow_xmin = 0, winow_xmax = 999, winow_ymin = 0, winow_ymax = 999, offset_us = 0):
    datafile = open(filename)
    
    numcodes = 0
    for line in datafile.readlines():
        x,y,timecode = string.split(str(line),'\t')
        x = int(x)
        y = int(y)
        timecode = int(timecode)
        if x >= winow_xmin and x <= winow_xmax and y >= winow_ymin and y <= winow_ymax: 
            if timecode <> 11810:
                numcodes += 1 

    timecodes = np.ndarray(shape = numcodes, dtype = int)
    i = 0
    datafile = open(filename)

    for line in datafile.readlines():
        x,y,timecode = string.split(str(line),'\t')
        x = int(x)
        y = int(y)
        timecode = int(timecode)
        if x >= winow_xmin and x <= winow_xmax and y >= winow_ymin and y <= winow_ymax: 
            if timecode <> 11810:
                timecodes[i] = timecode
                i += 1 

    return timecodes


if __name__ == '__main__':
    print "Running Auto-correlation analysis\n "
     
    from DoStuff import Correlate
    
    DO_ANALYSIS = False
    PICKLE_FILE = home_dir + '/output/datasets/NSLS_pickle_pre_beamdump_9990'
    PICKLE_FILE = home_dir + '/output/datasets/NSLS_pickle_post_beamdump_9990'
    
    NFILES = 9990
    
    path = home_dir + '/Desktop/VMShared/Data/NSLS/pre-all/'

      
    timecodemin = 1
    timecodemax = 11809
    
    correlmax = timecodemax - timecodemin + 1
    correlmin = timecodemin - timecodemax + 1
    correl_nbins = correlmax - correlmin

    
    if DO_ANALYSIS:
        histarray = np.ndarray(shape = correl_nbins, dtype = int)
        histarray.fill(0)
           
        files = []
        for filename in os.listdir(path):
            files.append(path + filename)
        
        t0 = time.time()
        for numfiles, filename in enumerate(files):
            if numfiles >= NFILES: break
            
            timecodes = GetNpTimecodes(filename,15,240,15,240)
            Correlate(histarray, timecodes, correlmin)
            
            
        dt = time.time() - t0
        print "Correlated %s files in %.4f "%(NFILES,dt)
        
        pickle.dump(histarray, open(PICKLE_FILE, 'wb'))
            
    ########################################################
            
            
    if not DO_ANALYSIS:
        histarray = pickle.load(open(PICKLE_FILE, 'rb'))
    
    histmin = 0
    histmax = 1000
    
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    correl_hist = TH1F('', 'Timecodes',correl_nbins,correlmin,correlmax)
    binsize = correl_hist.GetBinLowEdge(3) - correl_hist.GetBinLowEdge(2)
    assert binsize == 1
    
    totalweight = 0
    for i in range(len(histarray)):
        correl_hist.SetBinContent(i+1, histarray[i])
        totalweight += histarray[i]
    print "Total corellation = %s"%totalweight
    
    correl_hist.Draw()
    correl_hist.GetXaxis().SetTitle('#Delta t')
    c1.SaveAs(OUTPUT_PATH + "correlation_histogram" + FILE_TYPE)
    
    
    
    
    
###############################
    histcenter = 11810
    histrange = 400 
    histmin = histcenter - histrange
    histmax = histcenter + histrange
    
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    correl_hist = TH1F('', 'Timecodes',histmax - histmin ,histmin,histmax)
    binsize = correl_hist.GetBinLowEdge(3) - correl_hist.GetBinLowEdge(2)
    assert binsize == 1
    
    totalweight = 0
    for i in range(histmin, histmax):
        correl_hist.SetBinContent(i+1 - histmin, histarray[i])
        totalweight += histarray[i]
    print "Total corellation = %s"%totalweight
    
    correl_hist.Draw()
    correl_hist.GetXaxis().SetTitle('#Delta t')
    c1.SaveAs(OUTPUT_PATH + "zoomed_correlation_histogram" + FILE_TYPE)   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#    Browse(c1)
    
    exit()
    
    for i in range(10):
        print "bin %s = %s"%(i,correl_hist.GetBinContent(i))
    for i in range(correl_hist.GetNbinsX() - 10, correl_hist.GetNbinsX()+1):
        print "bin %s = %s"%(i,correl_hist.GetBinContent(i))
    
    


    
    print '\n***End code***'      