import os
from os.path import expanduser
import numpy as np
import pylab as pl
import string        
               
import time

from ROOT import TCanvas, TF1, TH1F, TGraph
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import GetRawTimecodes_SingleFile
import cPickle as pickle
from root_functions import Browse
import ROOT
from numpy import ndarray

        # bin < 0 = underflow
        # bin 0 = underflow
        
        # bin 1 = timecode = 0
        # bin timecodemax = timecodemax -1
        # bin timecodemax +1 = timecodemax
        
        # bin timecodemax +2 = overflow
        # bin timecodemax + >2 = overflow

FILE_TYPE = ".png"
path =          '/mnt/hgfs/VMShared/Data/NSLS-II/2015_07_31/run1/'
OUTPUT_PATH = '/mnt/hgfs/VMShared/output/NSLS-II/2015_07_31/run1/'


if __name__ == '__main__':
    print "Running Auto-correlation analysis\n "
    
    NFILES = 100
    
      
    timecodemin = 0
    timecodemax = 11809#11809
    rebin_factor = 1
    nbins = ((timecodemax - timecodemin))/ rebin_factor +1
    print 'nbins = %s'%nbins

    
    #TODO: reinstate this check
    correl_hist_file   = TH1F('', 'Timecodes',nbins,timecodemin,timecodemax+1)
    correl_hist_master = TH1F('', 'Timecodes',nbins,timecodemin,timecodemax+1)
    binsize = correl_hist_master.GetBinLowEdge(3) - correl_hist_master.GetBinLowEdge(2)
    print binsize
    assert binsize == rebin_factor
    
    correl_graph = TGraph(nbins)
    
    files = []
    for filename in os.listdir(path):
        files.append(path + filename)

    old_value = ROOT.Double()
    dummy = ROOT.Double()

    normalisation = 0.
    autocorrellation = np.zeros([nbins])
    autocorrellation_sum = np.zeros([nbins])

    for numfiles, filename in enumerate(files):
        print "File #%s"%numfiles
        if numfiles >= NFILES: break
        
        c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        filehist = TH1F('', 'Timecodes',nbins,timecodemin,timecodemax+1)
        binsize = filehist.GetBinLowEdge(3) - filehist.GetBinLowEdge(2)
        assert binsize == rebin_factor
#         for i in range(2):
#             for bin in range(nbins):
#                 filehist.Fill(bin)
#         filehist.Draw()  
#         c1.SaveAs(OUTPUT_PATH + "filehist.png")
#         exit()  

        timecodes = GetRawTimecodes_SingleFile(filename,15,240,15,240)
        for code in timecodes:
            if code != 11810:
                filehist.Fill(code)
#         filehist.Draw()  
#         c1.SaveAs(OUTPUT_PATH + "filehist.png")      
#         exit()
        
        contents = np.zeros([nbins], dtype = np.int32)
        for i in range(nbins):
            contents[i] = filehist.GetBinContent(i)
        
        denominator = 0.
        for i in range(1, timecodemax + 2):
            denominator += filehist.GetBinContent(i) ** 2
        
        result = np.correlate(contents, contents, mode = 'full')
        autocorrellation = result[result.size/2:]
        
        autocorrellation_sum += autocorrellation
        normalisation += denominator
        
#         autocorrellation /= denominator
#         print autocorrellation
#         exit()
        
    for pointnum, value in enumerate(autocorrellation_sum):
        correl_graph.SetPoint(pointnum,pointnum, value/ normalisation)
    
    correl_graph.Draw('AP')
    c1.SaveAs(OUTPUT_PATH + "autocorellation.png")
    
    
    outfile = open(OUTPUT_PATH + 'data.txt', 'w')
    for i in range(nbins):
        correl_graph.GetPoint(i,dummy,old_value)
        outfile.write(str(i) + '\t' + str(old_value) + '\n')
    outfile.close()
    
#     exit()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        ######################
        
    denominator = 0.
    for i in range(1, timecodemax + 2):
        denominator += filehist.GetBinContent(i) ** 2
    

    for j in range(0,timecodemax + 2):
    
        numerator = 0.
        for i in range(1, timecodemax + 2 - j): # from 1 to exclude underflow bin, up to end of histogram
            numerator += filehist.GetBinContent(i) * filehist.GetBinContent(i+j)
            
#             print "Filling:" + str(j) + ',' + str(numerator/denominator)
        
        correl_graph.GetPoint(j,dummy,old_value)
        correl_graph.SetPoint(j,j, old_value + (numerator/denominator))
        
#             if j >500: break
        
        
        
    #normalise:
    for i in range(nbins):
        correl_graph.GetPoint(i,dummy,old_value)
        correl_graph.SetPoint(i,i, old_value/float(NFILES))
    
    correl_graph.Draw('AP')
    c1.SaveAs(OUTPUT_PATH + "corellation.pdf")
#     exit()
            
            
    outfile = open(OUTPUT_PATH + 'corellation_data.txt', 'w')
    for i in range(nbins):
        correl_graph.GetPoint(i,dummy,old_value)
        outfile.write(str(i) + '\t' + str(old_value) + '\n')
    outfile.close()
    


    
    print '\n***End code***'      