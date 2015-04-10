import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils
import lsst.afw.detection as afwDetect
import lsst.afw.image as afwImage
from lsst.afw.image import makeImageFromArray
import time
import numpy as np
import lsst.afw.math        as math

# filename  = '/mnt/hgfs/VMShared/Data/arthur/sub_pic_9.txt'
# filename  = '/mnt/hgfs/VMShared/Data/arthur/sub_pic_14.txt'
filename  = '/mnt/hgfs/VMShared/Data/arthur/sub_pic_15.txt'

if __name__ == '__main__':
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'

    t_total = 0
    
    t0 = time.time()
    data = np.loadtxt(filename, dtype=np.int32, delimiter=',')#, converters, skiprows, usecols, unpack, ndmin)
    dt = time.time() - t0
    print "Load time = %.2f us" %(dt*1e6) 
    
    t0 = time.time()
    t_start = time.time()
    image = makeImageFromArray(data)
    dt = time.time() - t0
    print "DM image made in = %.2f us" %(dt*1e6) 
    t_total += dt
    
    
    t0 = time.time()
    sigma = 0.75
#     kWidth = (int(sigma * 7 + 0.5) // 2) * 2 + 1 # make sure it is odd
    kWidth = 5

####### discrete method
    gaussFunc = math.GaussianFunction1D(sigma)
    gaussKernel = math.SeparableKernel(kWidth, kWidth, gaussFunc, gaussFunc)
    math.convolve(image, image, gaussKernel, math.ConvolutionControl())
       
####### analytical method
#     kernel = math.AnalyticKernel(kWidth, kWidth, math.GaussianFunction2D(sigma, sigma, 0))
#     math.convolve(image, image, kernel, True, True)
   
    dt = time.time() - t0
    print "image smoothed in = %.2f us" %(dt*1e6) 
    t_total += dt

    ds9.mtv(image)
    
    #calculate basic stats
    t0 = time.time()
    basic_mean = np.std(data)
    basic_stddev = np.mean(data)
    dt = time.time() - t0
    print "Basic stats calculated in = %.2f us" %(dt*1e6) 
    t_total += dt


    #calculate advanced stats
    t0 = time.time()
    statFlags = math.STDEVCLIP | math.MEANCLIP | math.MEAN |math.STDEV
    control = math.StatisticsControl()
    imageStats = math.makeStatistics(image, statFlags, control)
    mean_clip = imageStats.getResult(math.MEANCLIP)[0]
    sigma_clip = imageStats.getResult(math.STDEVCLIP)[0] 
    mean = imageStats.getResult(math.MEAN)[0]
    sigma = imageStats.getResult(math.STDEV)[0]    
    dt = time.time() - t0
    print "Stats calculated in %.2f us" %(dt*1e6) 
    t_total += dt
    
    
    #find ions hits
    t0 = time.time()
#     thresholdValue = 50
    thresholdValue = mean_clip + (6*sigma_clip)
    npixMin = 5
    grow = 0
    isotropic = True
    
    threshold = afwDetect.Threshold(thresholdValue)
    footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
    footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
    footPrints = footPrintSet.getFootprints()
    dt = time.time() - t0
    print "Source finding took %.2f us" %(dt*1e6) 
    print "Found %s footprints in %s"%(len(footPrints), filename)
    t_total += dt


    t0 = time.time()
    centroids = []
    for footprintnum, footprint in enumerate(footPrints):
        centroids.append([footprint.getCentroid()])
        
        centroid_x, centroid_y = footprint.getCentroid()
        ds9.dot("x",centroid_x,centroid_y)# cross on the peak
        displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more
    
    dt = time.time() - t0
    print "Centroid listing took %.2f us" %(dt*1e6) 
    
    
    print "Total time was %.2f us" %(t_total*1e6) 

    print '\n***End code***'      
    
    
    
    
    
