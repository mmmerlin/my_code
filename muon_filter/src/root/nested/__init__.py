import lsst.afw.math        as math
import lsst.afw.image       as afwImg
import lsst.afw.detection   as afwDetect
import lsst.afw.display.ds9 as ds9
import lsst.afw.geom.ellipses as Ellipses
import lsst.afw.display.utils as displayUtils
from lsst.pex.config import Config, Field, ConfigField, makePolicy
import lsst.pipe.base as pipeBase



import  numpy as np
import  pylab as pl
from os.path import expanduser

from RejectWorms import ShowImage


if __name__ == '__main__':
    print "Running ellipticity comparison\n"
 
#===============================================================================
# Load and display   
   
    #0 = display nothing, 1 = just display the fits file, 2 = draw boxes around footprints, mark centroids
    DISPLAY_LEVEL = 0

    home_dir = expanduser("~")
    output_path = home_dir + '/output/'
    input_path = home_dir + '/dl/darks/from ccdtest.e2v.CCD250.112-04.dark.20140419-190507/'
    input_file = '000-00_dark_dark_500.00_002_20140420035006.fits'

    exposure = afwImg.ExposureF(input_path + input_file)
    mi = exposure.getMaskedImage()
    image = mi.getImage()

            
#===============================================================================
#   Stats
    statFlags = math.NPOINT | math.MEAN | math.STDEV | math.MAX | math.MIN | math.ERRORS | math.STDEVCLIP | math.MEANCLIP
    control = math.StatisticsControl()
    SAT = afwImg.MaskU_getPlaneBitMask("SAT")
    control.setAndMask(SAT)

    imageStats = math.makeStatistics(mi, statFlags, control)
    numBins = imageStats.getResult(math.NPOINT)[0]
    mean = imageStats.getResult(math.MEAN)[0]
    maxval = imageStats.getResult(math.MAX)[0]
    sigma = imageStats.getResult(math.STDEV)[0]
    sigma_clip = imageStats.getResult(math.STDEVCLIP)[0]
    mean_clip = imageStats.getResult(math.MEANCLIP)[0]
    print "Mean = %s" % mean
    print "Max = %s" % maxval
    print "nPx = %s" % numBins
    print "sigma = %s" % sigma
    print "sigma clip = %s" % sigma_clip
    print

#===============================================================================
    # set up finding parameters
    thresholdValue = mean + (5* sigma_clip)
    npixMin = 3
    grow = 0
    isotropic = False
    
#    bg_conf = BackgroundConfig()
#    bg_conf.setDefaults()
#    bg, bgSubExp = estimateBackground(exposure, bg_conf, subtract=True)

    threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
    footPrintSet = afwDetect.FootprintSet(exposure.getMaskedImage(), threshold, "DETECTED", npixMin)
    footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)

    footPrints = footPrintSet.getFootprints()
    footPrintSet.setMask(mi.getMask(), "DETECTED")
    print footPrints.size(), "footPrint(s) found\n"

    
    mask = mi.getMask()
    mask.addMaskPlane('MUON')
    mask.addMaskPlane('WORM')
    mask.addMaskPlane('SPOT')
    mask.printMaskPlanes()
    muon_bit, worm_bit, spot_bit = mask.getPlaneBitMask('MUON'), mask.getPlaneBitMask('WORM'), mask.getPlaneBitMask('SPOT')
#    print muon_bit, worm_bit, spot_bit
    
    afwDetect.setMaskFromFootprint(mask, footPrints[9], muon_bit)
    
    ShowImage(mi, ROI_Bbox = footPrints[9].getBBox(), border = 0)
    
    

#    exit()




#===============================================================================
# Shape extraction
    if DISPLAY_LEVEL >= 1:
        try: # initialise DS9, deal with a bug in its launching
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'
       
        
        ds9.setMaskPlaneVisibility('BAD', False)
        ds9.setMaskPlaneVisibility('CR', False)
        ds9.setMaskPlaneVisibility('DETECTED', False)
        ds9.setMaskPlaneVisibility('DETECTED_NEGATIVE', False)
        ds9.setMaskPlaneVisibility('EDGE', False)
        ds9.setMaskPlaneVisibility('INTRP', False)
        ds9.setMaskPlaneVisibility('MUON', True)
        ds9.setMaskPlaneVisibility('SAT', False)
        ds9.setMaskPlaneVisibility('SPOT', False)
        ds9.setMaskPlaneVisibility('SUSPECT', False)
        ds9.setMaskPlaneVisibility('WORM', False)
#        ds9.mtv(exposure.getMaskedImage())
    

        ds9.setMaskPlaneVisibility('MUON', True)

    
        ds9.mtv(mi.getImage(), frame = 0, isMask = False, title = 'Image data')
#        ds9.mtv(mi.getImage(), frame = 1, isMask = False, title = 'Image data2')
#        ds9.mtv(mi.getMask(), frame = 1, isMask = False, title = 'Mask')
     
#        cmd = "-mask mark 0"
#        ds9.ds9Cmd(cmd)
     
        displayUtils.drawBBox(footPrints[9].getBBox(), frame = 1, borderWidth=0.0)
        
    
    
    footprint = afwDetect.Footprint()
    xcoords, ycoords = [], []
    majors, minors, thetas = [], [], []
    ixxs, iyys, ixys = [], [], []

    for footprint in footPrints:
        quadshape = footprint.getShape()
        ixxs.append(quadshape.getIxx())
        iyys.append(quadshape.getIyy())
        ixys.append(quadshape.getIxy())

        axesshape = Ellipses.Axes(quadshape)
        majors.append(axesshape.getA())
        minors.append(axesshape.getB())
        thetas.append(axesshape.getTheta())
        
        centroid_x, centroid_y = footprint.getCentroid()
        xcoords.append(centroid_x)
        ycoords.append(centroid_y)
        
#        print "#px = %s" %footprint.getNpix()

        if DISPLAY_LEVEL >= 2:
#            argstring = "@:"+str(4*quadshape.getIxx())+','+str(4*quadshape.getIxy())+','+str(4*quadshape.getIyy()) #multiply by four just to make it more exaggerated otherwise they all look like cirlces
#            ds9.dot(argstring,centroid_x,centroid_y) #ellipse around the centroid
            ds9.dot("x",centroid_x,centroid_y)# cross on the peak
            displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.0)

#    ds9.zoom(10, 2000, 2035)
#===============================================================================
  
    
           

    print '\n*** End code ***'














