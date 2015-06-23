import os
from os.path import expanduser

import  pylab as pl
import  numpy as np

import string

def GetHitPixels_AllFilesinDir(path, xmin, xmax, ymin, ymax):
    
    hitpixels = 0
    
    hitpixels_per_frame  = []
    
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
            if x >= xmin and x <= xmax and y >= ymin and y <= ymax: 
                hitpixels = hitpixels + 1
        
        hitpixels_per_frame.append(hitpixels)
        hitpixels = 0
        
    return hitpixels_per_frame


if __name__ == '__main__':
    print "Running Code\n"

hitpixels_lists = []

hitpixels_flatten = []

for trial in range(1,11):
        
    home_dir  = expanduser('~')
    path = home_dir + '/Desktop/DMStack VM Shared/Phoenix lab data/Timepix/timepix 400hz 330 thr 250us window '+str(trial)+'/'
    
    hitpixels = GetHitPixels_AllFilesinDir(path, 15, 240, 15, 240)
    hitpixels_lists.append(hitpixels)
    print hitpixels
    
for hitpixels_list in hitpixels_lists:
    for hitpixels in hitpixels_list:
        hitpixels_flatten.append(hitpixels)
        
print '\n', hitpixels_flatten

histmin = np.amin(hitpixels_flatten)
histmax = np.amax(hitpixels_flatten)

histrange = int(histmax - histmin)
    
nbins = histrange

pl.figure()
pl.hist(hitpixels_flatten, bins = nbins, range = [histmin, histmax])
pl.title('Number of Hit Pixels/Frame')
pl.xlabel('Number of Hit Pixels/Frame')
pl.ylabel('Frequency')
pl.show()

print '\n***End code***'   