# from scipy.signal import convolve2d
# import lsst.afw.math.convolve as convolve
import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils
import lsst.afw.detection as afwDetect
import lsst.afw.image as afwImage
from lsst.afw.image import makeImageFromArray
import time
import numpy as np
import lsst.afw.math        as math
#t0 = time.time()
#dt = time.time() - t0
#print "Time was %.2f seconds" %dt 

filename  = '/mnt/hgfs/VMShared/Data/arthur/sub_pic_14.txt'

if __name__ == '__main__':
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'

    t0 = time.time()
    data = np.loadtxt(filename, dtype=np.int32, delimiter=',')#, converters, skiprows, usecols, unpack, ndmin)
    dt = time.time() - t0
    print "Load time = %.2f us" %(dt*1e6) 
    
    t0 = time.time()
    image = makeImageFromArray(data)
    dt = time.time() - t0
    print "DM image made in = %.2f us" %(dt*1e6) 
    
    t0 = time.time()
    sigma = 1
#     kWidth = (int(sigma * 7 + 0.5) // 2) * 2 + 1 # make sure it is odd
    kWidth = 5
    gaussFunc = math.GaussianFunction1D(sigma)
    gaussKernel = math.SeparableKernel(kWidth, kWidth, gaussFunc, gaussFunc)
    math.convolve(image, image, gaussKernel, math.ConvolutionControl())
    dt = time.time() - t0
    print "image smoothed in = %.2f us" %(dt*1e6) 

    ds9.mtv(image)


#   394             goodBBox = gaussKernel.shrinkBBox(convolvedImage.getBBox())
#   395             middle = convolvedImage.Factory(convolvedImage, goodBBox, afwImage.PARENT, False)
    
    
    
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
    
    
    t0 = time.time()
#     thresholdValue = 50
    thresholdValue = mean_clip + (5*sigma_clip)
    print thresholdValue
    npixMin = 5
    grow = 0
    isotropic = True
    
    threshold = afwDetect.Threshold(thresholdValue)
    footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
    footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
    footPrints = footPrintSet.getFootprints()
    print "Found %s footprints in %s"%(len(footPrints), filename)
    dt = time.time() - t0
    print "Time was %.2f us" %(dt*1e6) 
#     exit()
    
    for footprintnum, footprint in enumerate(footPrints):
#         npix = afwDetect.Footprint.getNpix(footprint)
        
        box = footprint.getBBox()
        centroid_x, centroid_y = footprint.getCentroid()
        ds9.dot("x",centroid_x,centroid_y)# cross on the peak
        displayUtils.drawBBox(box, borderWidth=0.5) # border to fully encompass the bbox and no more
    

    print '\n***End code***'      
    
    
    
    
    
