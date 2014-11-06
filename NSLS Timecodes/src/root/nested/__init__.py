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

OUTPUT_PATH = "/home/mmmerlin/output/"
FILE_TYPE = ".pdf"


def GetTimecodes_AllFilesinDir(path, xmin, xmax, ymin, ymax):
    
    timecodes = []
    files = []
    
    for filename in os.listdir(path):
        files.append(path + filename)
    
    for filename in files:
        datafile = open(filename)
        for line in datafile.readlines():
            x,y,timecode = string.split(str(line))
            x = int(x)
            y = int(y)
            timecode = int(timecode)
#            if x >= xmin and x <= xmax and y >= ymin and y <= ymax: 
            if timecode <> 11810:
                timecodes.append(timecode) 
            
    return timecodes


if __name__ == '__main__':
    print "Running Auto-correlation analysis\n "
      
    home_dir  = expanduser('~')
#    path = home_dir + '/Desktop/VMShared/Data/NSLS/Post-beamdump/Run_00_thr_325/'
    path = home_dir + '/Desktop/VMShared/Data/NSLS/OneFile/'
#    path = home_dir + '/Desktop/VMShared/Data/NSLS/post-all/'
    
    
    t0 = time.time()
    timecodes  = GetTimecodes_AllFilesinDir(path, 15, 240, 15, 240)
    dt = time.time() - t0
    print "Loaded %s timecodes in %.2f seconds" %(len(timecodes),dt) 
       
       
    histmin = 1
    histmax = 11809
    nbins = int(histmax - histmin) + 1
#    histmin = np.amin(timecodes) #values are always these so OK to hardcode, just saves searching a large array
#    histmax = np.amax(timecodes)
    
    
    
    
    
    ###########
    if False:
        t0 = time.time()
        correl = []
        for i in range(len(timecodes)):
            for j in range(i+1,len(timecodes)):
                correl.append(timecodes[i]-timecodes[j])
        dt = time.time() - t0
        print "%s combinations calculated in %.2f s"%(len(correl),dt)
        
    #    histrange = int(histmax - histmin)
    #    nbins = histrange
    #    pl.figure()
    #    pl.hist(timecodes, bins = nbins, range = [histmin, histmax])
    #    pl.title('Timecodes')
    #    pl.show()
    
        correlmax = histmax - histmin
        correlmin = histmin - histmax
        correl_nbins = histmax - histmin + 1
    
        correlange = int(correlmax - correlmin)
        pl.figure()
        pl.hist(correl, bins = correl_nbins, range = [correlmin, correlmax])
        pl.title('Correlation')
        pl.show()
        
        
        exit()
        
    
    
    
    
    if False:
    
        c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        timecode_hist = TH1F('', 'Timecodes',nbins,histmin,histmax)
        
        for i, timecode in enumerate(timecodes):
            timecode_hist.Fill(timecode)
        timecode_hist.Draw()
        timecode_hist.GetXaxis().SetTitle('Timecode')
    
    #    c1.SaveAs(OUTPUT_PATH + "timecode_histogram" + FILE_TYPE)
        
        
        t0 = time.time()
        histmin = 1
        histmax = 11809
        nbins = int(histmax - histmin) + 1
        
        correlmax = histmax - histmin
        correlmin = histmin - histmax
        correl_nbins = histmax - histmin + 1
    
        c2 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
        correlation_hist = TH1F('', 'Timecodes',correl_nbins,correlmin,correlmax)
       
        weightsum = 0
        for i in range(nbins):
            if i % 100 == 0: print i
            for j in range(nbins):
                if i == j:
                    value = timecode_hist.GetBinLowEdge(i)
                    content = int(timecode_hist.GetBinContent(i))
                    weight = content * (content - 1)/2
                else:
                    value = timecode_hist.GetBinLowEdge(i) - timecode_hist.GetBinLowEdge(j)
                    weight = timecode_hist.GetBinContent(i) * timecode_hist.GetBinContent(j)
                
                correlation_hist.Fill(value, weight)
                weightsum += weight
                
        dt = time.time() - t0
        print "Correlation histogram produced %.2f s"%dt
        print "weightsum = %s "%weightsum
    
        correlation_hist.Draw()
        c2.SaveAs(OUTPUT_PATH + "correlation_new_better_bins_low_edge" + FILE_TYPE)
        
        exit()
        
    
    
    
    
    #########################
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    timecode_hist = TH1F('', 'Timecodes',nbins,histmin,histmax)
    
    for i, timecode in enumerate(timecodes):
        timecode_hist.Fill(timecode)
    timecode_hist.Draw()
    timecode_hist.GetXaxis().SetTitle('Timecode')
    print 'made timecode hist'
    
    c1.SaveAs(OUTPUT_PATH + "asdasd" + FILE_TYPE)
    
    
    t0 = time.time()

    correlmax = histmax - histmin
    correlmin = histmin - histmax
    correl_nbins = correlmax - correlmin + 1

#    print correlmax
#    print correlmin
#    print correl_nbins
    
#    time_binedges = [-1.] * nbins
    time_binvalues = [0.] * (nbins)
    correlation_values = [0.] * correl_nbins
    
    for i in range(nbins):
        time_binvalues[i] = timecode_hist.GetBinContent(i+1)
    print time_binvalues
    
    weightsum = 0
    for i in range(nbins):
        if i % 100 == 0: print i
        for j in range(nbins):
            if i == j:
                content = time_binvalues[i]
                if content >= 1:
                    weight = content * (content - 1)/2
                else:
                    weight = 0.
            else:
                weight = time_binvalues[i] * time_binvalues[j]

            correlation_values[i + j] += weight
            weightsum += weight
    
        
    c3 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    quick_hist = TH1F('', 'Timecodes',correl_nbins,correlmin,correlmax)
    for i in range(correl_nbins):
        quick_hist.SetBinContent(i+1, correlation_values[i])
    
    quick_hist.Fill(-100000)
    quick_hist.Fill(-100000)
    quick_hist.Fill(-100000)
    quick_hist.Fill(100000)
    quick_hist.Fill(100000)
    quick_hist.Fill(100000)
    quick_hist.Fill(100000)
    quick_hist.Fill(100000)
    
    
    print
    print "nbins = %s"%quick_hist.GetNbinsX()
    print "bin 0 = %s" %quick_hist.GetBinContent(0)
    print "bin 1 = %s" %quick_hist.GetBinContent(1)
    print "bin 2 = %s" %quick_hist.GetBinContent(2)
    print "bin 2nd last = %s" %quick_hist.GetBinContent(quick_hist.GetNbinsX()-1)
    print "bin last = %s" %quick_hist.GetBinContent(quick_hist.GetNbinsX())
    print "bin overflow = %s" %quick_hist.GetBinContent(quick_hist.GetNbinsX()+1)
   
   
    dt = time.time() - t0
    print "Quick way finished in %.2f s"%dt
    print "weightsum = %s "%weightsum
   
    quick_hist.Draw()
    c3.SaveAs(OUTPUT_PATH + "quick_way_1" + FILE_TYPE)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#    histrange = int(histmax - histmin)
#    nbins = histrange
#    pl.figure()
#    pl.hist(timecodes, bins = nbins, range = [histmin, histmax])
#    pl.title('Timecodes')
#    pl.show()
#
#
#    correlmin = np.amin(correl)
#    correlmax = np.amax(correl)
#
#    correlange = int(correlmax - correlmin)
#    nbins = correlange
#    pl.figure()
#    pl.hist(correl, bins = nbins, range = [correlmin, correlmax])
#    pl.title('Correlation')
#    pl.show()


    
    print '\n***End code***'      