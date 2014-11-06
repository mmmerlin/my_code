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


if __name__ == '__main__':
    print "Running ellipticity comparison\n"
 
#===============================================================================
# Load and display   
   
    #0 = display nothing, 1 = just display the fits file, 2 = draw boxes around footprints, mark centroids
    DISPLAY_LEVEL = 2 

    home_dir = expanduser("~")
    output_path = home_dir + '/output/'
    input_path = home_dir + '/dl/'

    input_file = 'sparse_tree_rings.fits'
    exposure = afwImg.ExposureF(input_path + input_file)

    maskedImage = exposure.getMaskedImage()
    image = maskedImage.getImage()

            
#===============================================================================
#   Stats
    statFlags = math.NPOINT | math.MEAN | math.STDEV | math.MAX | math.MIN | math.ERRORS
    control = math.StatisticsControl()
    SAT = afwImg.MaskU_getPlaneBitMask("SAT")
    control.setAndMask(SAT)

    imageStats = math.makeStatistics(maskedImage, statFlags, control)
    numBins = imageStats.getResult(math.NPOINT)[0]
    mean = imageStats.getResult(math.MEAN)[0]
    maxval = imageStats.getResult(math.MAX)[0]
    sigma = imageStats.getResult(math.STDEV)[0]
    print "Mean = %s" % mean
    print "Max = %s" % maxval
    print "nPx = %s" % numBins
    print "sigma = %s" % sigma
    print


#===============================================================================
    # set up finding parameters
    thresholdValue = 100
    npixMin = 5
    grow = 1
    isotropic = False

    
#    bg_conf = BackgroundConfig()
#    bg_conf.setDefaults()
#    bg, bgSubExp = estimateBackground(exposure, bg_conf, subtract=True)

    threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
    footPrintSet = afwDetect.FootprintSet(exposure.getMaskedImage(), threshold, "DETECTED", npixMin)
    footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)

    footPrints = footPrintSet.getFootprints()
    footPrintSet.setMask(maskedImage.getMask(), "DETECTED")
    print footPrints.size(), "footPrint(s) found\n"


#===============================================================================
# Shape extraction
    if DISPLAY_LEVEL >= 1:
        try: # initialise DS9, deal with a bug in its launching
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'
        ds9.mtv(exposure.getMaskedImage().getImage())
    
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
        
        print "#px = %s" %footprint.getNpix()

        if DISPLAY_LEVEL >= 2:
            argstring = "@:"+str(4*quadshape.getIxx())+','+str(4*quadshape.getIxy())+','+str(4*quadshape.getIyy()) #multiply by four just to make it more exaggerated otherwise they all look like cirlces
            ds9.dot(argstring,centroid_x,centroid_y) #ellipse around the centroid
            ds9.dot("x",centroid_x,centroid_y)# cross on the peak
            displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.0)

    ds9.zoom(10, 2000, 2035)
#===============================================================================
    

#    for t in thetas:
#        print "theta = %s" %(t*180./np.pi)




#===============================================================================
# Now make a bunch of plots
#===============================================================================
#===============================================================================
# Plot options
#===============================================================================
    ANGLES='uv'
    UNITS = 'xy'
    PIVOT = 'middle'
    WIDTH = 0.5
    HEADWIDTH = 0
    XMIN = 1536
    XMAX = 2436
    YMIN = 1600
    YMAX = 2450
#===============================================================================


#===============================================================================
# Sextractor - 2nd moments
#===============================================================================
    data = np.loadtxt(input_path + "sparse_tree_rings.cat")
    x = data[:, 2] #x pos
    y = data[:, 3] #y pos
    x2 = data[:, 4] #x pos variance
    y2 = data[:, 5] #y pos variance
    xy = data[:, 6] # x-y covariance
    aa = data[:, 7] #major axis RMS
    bb = data[:, 8] #minor axis RMS
    angle = data[:, 9] #theta in degrees

    e1 = (x2 - y2) / (x2 + y2)
    e2 = (2 * xy) / (x2 + y2)

    theta = np.arctan2(e2, e1) / 2.
    r = np.sqrt(e1 ** 2 + e2 ** 2)
    u = r * np.cos(theta)
    v = r * np.sin(theta)

    pl.figure()
    sex_moments = pl.quiver(x, y, u, v, angles=ANGLES, units=UNITS, pivot=PIVOT, width=WIDTH, headwidth=HEADWIDTH , scale=1./500. )
    pl.axis([XMIN, XMAX, YMIN, YMAX])
    pl.title('Sextractor - second moments')
#===============================================================================


#===============================================================================
# Sextractor - a,b,theta
#===============================================================================
    sex_ellipticity = (aa - bb)/(aa)

    xvectors = sex_ellipticity * np.cos(angle * np.pi /180.) 
    yvectors = sex_ellipticity * np.sin(angle * np.pi /180.)
    
    pl.figure()
    sex_abt = pl.quiver(x, y, xvectors, yvectors, angles=ANGLES, units=UNITS, pivot=PIVOT, width=WIDTH, headwidth=HEADWIDTH , scale=1./500. )
    pl.axis([XMIN, XMAX, YMIN, YMAX])
    pl.title('Sextractor - a, b, theta')
#===============================================================================


#===============================================================================
# DM data - 2nd moments
#===============================================================================
    my_e1 = (np.array(ixxs) - np.array(iyys)) / (np.array(ixxs) + np.array(iyys))
    my_e2 = (2 * np.array(ixys)) / (np.array(ixxs) + np.array(iyys))

    my_theta = np.arctan2(my_e2, my_e1) / 2.
    my_r = np.sqrt(my_e1 ** 2 + my_e2 ** 2)
    my_u = my_r * np.cos(my_theta)
    my_v = my_r * np.sin(my_theta)

    pl.figure()
    dm_moments = pl.quiver(xcoords, ycoords, my_u, my_v, angles=ANGLES, units=UNITS, pivot=PIVOT, width=WIDTH, headwidth=HEADWIDTH , scale=1./200. )
    pl.axis([XMIN, XMAX, YMIN, YMAX])
    pl.title('DM stack - 2nd moments')
#===============================================================================


#===============================================================================
# DM data - a, b, theta
#===============================================================================
    npmajors = np.array(majors)
    npminors = np.array(minors)
    npthetas = np.array(thetas)
    
    dm_ellipticity = (npmajors - npminors) / (npmajors)
    
    dm_abt_xvectors = dm_ellipticity * np.cos(npthetas) 
    dm_abt_yvectors = dm_ellipticity * np.sin(npthetas)

    pl.figure()
    dm_abt = pl.quiver(xcoords, ycoords, dm_abt_xvectors, dm_abt_yvectors, angles=ANGLES, units=UNITS, pivot=PIVOT, width=WIDTH, headwidth=HEADWIDTH , scale=1./200. )
    pl.axis([XMIN, XMAX, YMIN, YMAX])
    pl.title('DM stack - a, b, theta')
#===============================================================================


#===============================================================================
# Distributions of angles
#===============================================================================
    
    pl.figure()
    pl.hist(angle, bins = 180)
    pl.title('Sextractor angle histogram')
#===============================================================================
  
    pl.figure()
    pl.hist(np.array(thetas) *180/np.pi , bins = 180)
    pl.title('DM angle histogram')
#===============================================================================

    pl.figure()
    pl.scatter(range(len(angle)),angle)
    pl.title('Sextractor angle sequence')
#===============================================================================

    pl.figure()
    pl.scatter(range(len(thetas)),np.array(thetas) * 180/np.pi)
    pl.title('DM angle sequence')
#===============================================================================


    pl.show()
    print '\n*** End code ***'














