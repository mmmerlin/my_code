import os
from os.path import expanduser

import lsst.afw.image       as afwImg
import lsst.afw.detection   as afwDetect
import lsst.afw.display.ds9 as ds9

import numpy as np
import pylab as pl

from lsst.afw.image import makeImageFromArray

def TimepixToExposure(filename, xmin, xmax, ymin, ymax):
    
    data = np.loadtxt(filename)

    my_array = np.zeros((256,256), dtype = np.int32)
    
    if data.shape == (0,):
        my_image = makeImageFromArray(my_array)
        
    elif data.shape == (3,):
        x = data[0] 
        y = data[1] 
        t = data[2]
        
        if x >= xmin and x <= xmax and y >= ymin and y <= ymax:
            my_array[y,x] = t
      
        my_image = makeImageFromArray(my_array)
    
    else:   
        x = data[:, 0] 
        y = data[:, 1] 
        t = data[:, 2]
    
        for pointnum in range(len(x)):
            if x[pointnum] >= xmin and x[pointnum] <= xmax and y[pointnum] >= ymin and y[pointnum] <= ymax:
                my_array[y[pointnum],x[pointnum]] = t[pointnum]
            
        my_image = makeImageFromArray(my_array)
    
    return my_image


if __name__ == '__main__':
    print "Running Code\n"
    
npix_footprint = []

for trial in range(1,11):
    
    files = [] 
    
    home_dir = expanduser("~") 
    path = home_dir + '/Desktop/DMStack VM Shared/Phoenix lab data/Timepix/timepix 400hz 330 thr 250us window '+str(trial)+'/'
    
    for filename in os.listdir(path):
        files.append(path + filename)
           
    for filename in files:
       
        image = TimepixToExposure(filename, 15, 240, 15, 240)
        
        # find some clusters - set up some finding parameters
            
        thresholdValue = 1
        npixMin = 1
        grow = 0
        isotropic = False
        
        # do the finding
            
        threshold = afwDetect.Threshold(thresholdValue)
        footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
        
        footPrints = footPrintSet.getFootprints()
            
        #find the number of pixels per footprint
            
        for footprint in footPrints:
            Npix_footprint = afwDetect.Footprint.getNpix(footprint)
            npix_footprint.append(Npix_footprint)

count = 0

for element in npix_footprint:
    if element == 2:
        count = count + 1
        
print 'Number of two pixel clusters = ', count

#plot histogram

histmin = np.amin(npix_footprint)
histmax = np.amax(npix_footprint)

histrange = int(histmax - histmin)
    
nbins = 2

pl.figure()
pl.hist(npix_footprint, bins = nbins, range = [histmin, histmax])
pl.title('Number of Hit Pixels/Footprint')
pl.xlabel('Number of Hit Pixels/Footprint')
pl.ylabel('Frequency')
pl.show()

print '\n***End code***' 