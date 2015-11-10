def DrawFootprint(bbox,x,y):
    ds9.dot("x",x,y) # draw cross at the centroid
    displayUtils.drawBBox(bbox, borderWidth=0.5) # borderWidth of 0.5 set bbox to fully encompass footprint and no more


import lsst.afw.display.ds9 as ds9
from lsst.display.ds9 import ds9Cmd
from lsst.display.ds9 import initDS9
# import lsst.display.ds9.ds9 as ds9

import lsst.afw.image as afwImage
import lsst.afw.math as math
import lsst.afw.detection as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.afw.geom as afwGeom
from time import sleep

DISPLAY = True


suffix = '.0001.short.M.fits.old'
prefix = '/mnt/hgfs/VMShared/Data/lsst_calibration/1/t'
files = [prefix + str(i) + suffix for i in range(1,6)]
centroids = []
CROP = False





# suffix = '.fits'
# prefix = '/mnt/hgfs/VMShared/Data/lsst_calibration/2/t'
# files = [prefix + str(i) + suffix for i in range(1,6)]
# centroids = []
# CROP = True
# xy0 = [630,360]
# size = 70
#===============================================================================
# #     thresholdValue = (6*stdevclip)
# #     npixMin = 1
# #     grow = 2
# #     isotropic = True
#===============================================================================


# suffix = '.short.M.fits.old'
# prefix = '/mnt/hgfs/VMShared/Data/lsst_calibration/3/t1.000'
# files = [prefix + str(i) + suffix for i in range(1,10)]
# centroids = []
# CROP = True
# xy0 = [1662,1106]
# size = 100
#===============================================================================
# # #     thresholdValue = (6*stdevclip)
# # #     npixMin = 1
# # #     grow = 1
# # #     isotropic = True
#===============================================================================


# suffix = '.short.M.fits.old'
# prefix = '/mnt/hgfs/VMShared/Data/lsst_calibration/4/t3.000'
# files = [prefix + str(i) + suffix for i in range(1,10)]
# centroids = []
# CROP = False
#===============================================================================
# NB These settings may not be the *exact* ones used, but are close enough. Pixels of interest are saturated so threshold is not so important
# # #     thresholdValue = (100*stdevclip)
# # #     npixMin = 1
# # #     grow = 1
# # #     isotropic = True
#===============================================================================



files = ['/mnt/hgfs/VMShared/Data/lsst_calibration/3/t1.0001.short.M.fits.old']

for i, filename in enumerate(files):
    print 'Processing %s'%filename
    
    image = afwImage.ImageF_readFits(filename)
    
    #Define ROI
    if CROP:
#         xy0 = [1266,743]
#         size = 450
        image = image[xy0[0]:xy0[0]+size, xy0[1]:xy0[1]+size]
        image.setXY0(afwGeom.Point2I(0,0))
        
#         xy0 = afwGeom.Point2I(1266,743)
#         size = 450
#         bbox = afwGeom.Box2I(xy0, afwGeom.Extent2I(size,size))
#         image = afwImage.ImageF(image,bbox,afwImage.LOCAL, True)
#         image.setXY0(afwGeom.Point2I(0,0))
    
    
    statFlags = math.MEAN | math.MEANCLIP | math.STDEV | math.STDEVCLIP
    control = math.StatisticsControl()
    
    imageStats  = math.makeStatistics(image, statFlags, control)
    mean        = imageStats.getResult(math.MEAN)[0]
    mean_clip   = imageStats.getResult(math.MEANCLIP)[0]
    stdev       = imageStats.getResult(math.STDEV)[0]
    stdevclip   = imageStats.getResult(math.STDEVCLIP)[0]
    
    print 'Mean = %s\nMean_clip = %s\nstddev = %s\nstddev_clip = %s\n'%(mean, mean_clip,stdev, stdevclip)
    
    image -= mean_clip
    
    thresholdValue = (5*stdevclip)
    npixMin = 1
    grow = 2
    isotropic = True
    
    maskedIm = afwImage.MaskedImageF(image)
    
    threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
    footPrintSet = afwDetect.FootprintSet(maskedIm, threshold, "DETECTED", npixMin)
    footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
  
    footPrints = footPrintSet.getFootprints()
    print "Found %s footprints"%len(footPrints)
 
 
    if DISPLAY:
        initDS9()
        ds9.mtv(image)
 
 
    with ds9.Buffering():
        for footprint_num, footprint in enumerate(footPrints):
#             if footprint_num > 2: continue
            centroid_x, centroid_y = footprint.getCentroid()
            bbox = footprint.getBBox()
              
            if DISPLAY:
                DrawFootprint(bbox, centroid_x, centroid_y) 
          
            centroids.append(filename + '\t%s\t%s'%(centroid_x, centroid_y))
             
             
    arg = 'saveimage jpeg ' + '/mnt/hgfs/VMShared/Data/lsst_calibration/' + str(i) + '_no_crop.jpeg' + ' 100'
    ds9Cmd(arg)
    exit()
#     sleep(1)
    
# print 'done'
    
for data in centroids:
    print data
     
    
    
    
    
    
    
    
    
    
    