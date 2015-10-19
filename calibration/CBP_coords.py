def DrawFootprint(bbox,x,y):
    ds9.dot("x",x,y) # draw cross at the centroid
    displayUtils.drawBBox(bbox, borderWidth=0.5) # borderWidth of 0.5 set bbox to fully encompass footprint and no more


import lsst.afw.display.ds9 as ds9
import lsst.afw.image as afwImage
import lsst.afw.math as math
import lsst.afw.detection as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.afw.geom as afwGeom
from time import sleep

CROP = False
DISPLAY = True

suffix = '.0001.short.M.fits.old'
prefix = '/mnt/hgfs/VMShared/Data/lsst_calibration/t'

files = [prefix + str(i) + suffix for i in range(8)]
centroids = []

for filename in files:
    print 'Processing %s'%filename
    
    image = afwImage.ImageF_readFits(filename)
    
    #Define ROI
    if CROP:
        xy0 = [1266,743]
        size = 450
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
    npixMin = 3
    grow = 1
    isotropic = True
    
    maskedIm = afwImage.MaskedImageF(image)
    
#     threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
#     footPrintSet = afwDetect.FootprintSet(maskedIm, threshold, "DETECTED", npixMin)
#     footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
#  
#     footPrints = footPrintSet.getFootprints()
#     print "Found %s footprints"%len(footPrints)
 
    if DISPLAY:
        ds9.mtv(image)
 
    arg = 'saveimage jpeg ' + '/mnt/hgfs/VMShared/Data/lsst_calibration/t_example_frame.jpeg' + ' 100'
    ds9.ds9Cmd(arg)
 
#     for footprint_num, footprint in enumerate(footPrints):
#         centroid_x, centroid_y = footprint.getCentroid()
#         bbox = footprint.getBBox()
#         
#         if DISPLAY:
#             ds9.mtv(image)
#             print centroid_x, centroid_y
#             DrawFootprint(bbox, centroid_x, centroid_y) 
#     
#         centroids.append([centroid_x, centroid_y])
    
    sleep(10)
    
#     exit()
    
for data in centroids:
    print data
    
    
    
    
    
    
    
    
    
    
    