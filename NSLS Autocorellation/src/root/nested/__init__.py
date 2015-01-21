import os
from os.path import expanduser
import numpy as np
import pylab as pl
import string        
               
import time
from __builtin__ import len
#t0 = time.time()
#dt = time.time() - t0
#print "Time was %.2f seconds" %dt 

from ROOT import TCanvas, TF1, TH1F
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import GetRawTimecodes_SingleFile
import cPickle as pickle
from root_functions import Browse



home_dir  = expanduser('~')
OUTPUT_PATH = "/home/mmmerlin/output/"
FILE_TYPE = ".pdf"
PICKLE_FILE = home_dir + '/output/datasets/NSLS_pickle'

if __name__ == '__main__':
    print "Running Auto-correlation analysis\n "
      
    DO_ANALYSIS = False
    PICKLE_FILE = home_dir + '/output/datasets/NSLS_pickle_3330'
    
    NFILES = 1
    
    #    path = home_dir + '/Desktop/VMShared/Data/NSLS/Post-beamdump/Run_00_thr_325/'
    path = home_dir + '/Desktop/VMShared/Data/NSLS/post-all/'

      
    timecodemin = 1
    timecodemax = 11809
    
    correlmax = timecodemax - timecodemin + 1
    correlmin = timecodemin - timecodemax + 1
    correl_nbins = correlmax - correlmin

    
    if DO_ANALYSIS:
        print "correct code"
        histarray = np.zeros(correl_nbins)
           
        files = []
        for filename in os.listdir(path):
            files.append(path + filename)
        
        
        for numfiles, filename in enumerate(files):
            if numfiles >= NFILES: break
            
            timecodes = GetRawTimecodes_SingleFile(filename,15,240,15,240)
            print "loaded %s timecodes from file %s"%(len(timecodes),numfiles)
            
            t0 = time.time()
            weight = 0
            for i in range(len(timecodes)):
                for j in range(i+1,len(timecodes)):
                    histarray[(timecodes[i]-timecodes[j]) - correlmin] += 1
#                    weight += 1



                    ####working
#                    value = timecodes[i]-timecodes[j]
#                    histarray[int(value) - correlmin] += 1
#                    weight += 1
                    
            dt = time.time() - t0
            print "%s combinations calculated in %.2f s"%(0,dt)
            
        
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
    histrange = 100 
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
    
    
    
    
    
    
    
    
    
    

        
        
        
    


#
#    weightsum = 0
#    for i in range(nbins):
#        if i % 100 == 0: print i
#        for j in range(nbins):
#            if i == j:
#                value = timecode_hist.GetBinLowEdge(i)
#                content = int(timecode_hist.GetBinContent(i))
#                weight = content * (content - 1)/2
#            else:
#                value = timecode_hist.GetBinLowEdge(i) - timecode_hist.GetBinLowEdge(j)
#                weight = timecode_hist.GetBinContent(i) * timecode_hist.GetBinContent(j)
#            
#            correlation_hist.Fill(value, weight)
#            weightsum += weight
#            
#    dt = time.time() - t0
#    print "Correlation histogram produced %.2f s"%dt
#    print "weightsum = %s "%weightsum
#
#    correlation_hist.Draw()
#    c2.SaveAs(OUTPUT_PATH + "correlation_new_better_bins_low_edge" + FILE_TYPE)
#    
#    exit()
#    
#    
#    
#    
#    
#    for i in range(nbins):
#        time_binvalues[i] = timecode_hist.GetBinContent(i+1)
#    print time_binvalues
#    
#    weightsum = 0
#    for i in range(nbins):
#        if i % 100 == 0: print i
#        for j in range(nbins):
#            if i == j:
#                content = time_binvalues[i]
#                if content >= 1:
#                    weight = content * (content - 1)/2
#                else:
#                    weight = 0.
#            else:
#                weight = time_binvalues[i] * time_binvalues[j]
#
#            correlation_values[i + j] += weight
#            weightsum += weight
#    
#        
#    c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
#    quick_hist = TH1F('', 'Timecodes',correl_nbins,correlmin,correlmax)
#    for i in range(correl_nbins):
#        quick_hist.SetBinContent(i+1, correlation_values[i])
#    
#    quick_hist.Fill(-100000)
#    quick_hist.Fill(-100000)
#    quick_hist.Fill(-100000)
#    quick_hist.Fill(100000)
#    quick_hist.Fill(100000)
#    quick_hist.Fill(100000)
#    quick_hist.Fill(100000)
#    quick_hist.Fill(100000)
#    
#    
#    print
#    print "nbins = %s"%quick_hist.GetNbinsX()
#    print "bin 0 = %s" %quick_hist.GetBinContent(0)
#    print "bin 1 = %s" %quick_hist.GetBinContent(1)
#    print "bin 2 = %s" %quick_hist.GetBinContent(2)
#    print "bin 2nd last = %s" %quick_hist.GetBinContent(quick_hist.GetNbinsX()-1)
#    print "bin last = %s" %quick_hist.GetBinContent(quick_hist.GetNbinsX())
#    print "bin overflow = %s" %quick_hist.GetBinContent(quick_hist.GetNbinsX()+1)
#   
#   
#    dt = time.time() - t0
#    print "Quick way finished in %.2f s"%dt
#    print "weightsum = %s "%weightsum
#   
#    quick_hist.Draw()
#    c3.SaveAs(OUTPUT_PATH + "quick_way_1" + FILE_TYPE)
#    
#    
#    
#    
    
    
    
    


    
    print '\n***End code***'      