import os
from os.path import expanduser

import  pylab as pl
import  numpy as np

def GetHitPixels_AllFilesInDir(path, winow_xmin = 0, winow_xmax = 999, winow_ymin = 0, winow_ymax = 999, offset_us = 0, tmin = -999999, tmax = 999999):
    import string
    
    files = []
    timecodes = []
    hitpixels = []
    
    for filename in os.listdir(path):
        files.append(path + filename)
   
    for filename in files:
        datafile = open(filename)
        for line in datafile.readlines():
            x,y,timecode = string.split(str(line),'\t')
            x = int(x)
            y = int(y)
            timecode = int(timecode)
            if x>=winow_xmin and x<=winow_xmax and y>=winow_ymin and y<=winow_ymax:
                intrinsic_offset = 136.6
                actual_offset_us = intrinsic_offset - offset_us
                time_s = (11810. - timecode) * 20e-9
                time_us = (time_s * 1e6)- actual_offset_us
                if time_us >= tmin and time_us <= tmax:
                    timecodes.append(time_us)
         
        hit_pixels = len(timecodes)
        if hit_pixels < 60000: 
            hitpixels.append(hit_pixels)
        if hit_pixels == 280: print len(hitpixels)
        timecodes = []
   
    return hitpixels


if __name__ == '__main__':
    print "Running Hit Pixels/Frame Analysis\n"

Averages = []

expected = []

threshold_values = [260, 270, 280, 290, 300, 310, 320, 325, 330, 336]

for threshold in threshold_values:
    
    if threshold != 336: continue
    
    home_dir = expanduser("~")

    path = home_dir + '/Desktop/DMStack VM Shared/Chem/threshold/Butanone_2us_'+str(threshold)+'/'

    hitpixels = GetHitPixels_AllFilesInDir(path, 15, 240, 15, 240, 2)

    histmin = np.amin(hitpixels)
    histmax = np.amax(hitpixels)
    print histmax
    histrange = int(histmax - histmin)
    
    nbins = histrange
    
    array, bin_edges = np.histogram(hitpixels, bins = nbins, range = [histmin, histmax], normed = True)
    
    Expected = 0

    for i in range(len(array)):
        Expected = Expected + array[i] * bin_edges[i]
    print (Expected)
    expected.append(Expected)
    
    pl.figure()
    pl.hist(hitpixels, bins = nbins, range = [histmin,histmax], normed = True)
    pl.title('Hit Pixels/Frame - Threshold '+str(threshold)+'')

    pl.show()

    total = 0
    for hits in hitpixels:
        total = total + hits

    averhits = total/len(hitpixels)
    print 'Average Hits = ', averhits
    Averages.append(averhits)
    
pl.figure()
pl.plot(threshold_values, Averages, 'o')
pl.title('Average Hit Pixels vs. Threshold')
pl.show()
    
print '\n***End code***'