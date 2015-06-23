import os
from os.path import expanduser

import numpy as np
import pylab as pl

import string        
               
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
            if x >= xmin and x <= xmax and y >= ymin and y <= ymax: 
                timecodes.append(timecode) 
            
    return timecodes


if __name__ == '__main__':
    print "Running Code\n"
      
timecodes_lists = []

timecodes_flatten = []
   
for trial in range(1,11):
    
    home_dir  = expanduser('~')
    path = home_dir + '/Desktop/DMStack VM Shared/Phoenix lab data/Timepix/timepix 400hz 330 thr 250us window '+str(trial)+'/'
        
    timecodes  = GetTimecodes_AllFilesinDir(path, 15, 240, 15, 240)
    timecodes_lists.append(timecodes)
    
for timecodes_list in timecodes_lists:
    for timecodes in timecodes_list:
        timecodes_flatten.append(timecodes) 

print timecodes_flatten
   
histmin = np.amin(timecodes_flatten)
histmax = np.amax(timecodes_flatten)

histrange = int(histmax - histmin)
    
nbins = histrange
      
pl.figure()
pl.hist(timecodes_flatten, bins = 50, range = [histmin, histmax])
pl.title('Timecodes')
pl.xlabel('Timecodes')
pl.ylabel('Frequency')
pl.show()

print '\n***End code***'      