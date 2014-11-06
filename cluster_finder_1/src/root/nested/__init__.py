# import the DMstack stuff
import lsst.afw.math        as math
import lsst.afw.table       as afwTable
import lsst.afw.image       as afwImg
import lsst.afw.detection   as afwDetect
import lsst.afw.display.ds9 as ds9

# import stuff for plotting
import  numpy as np
import  matplotlib.pyplot as plt
from    matplotlib.colors import LogNorm
import  matplotlib.mlab as mlab
import  pylab as pl

from os.path import expanduser
from numpy import meshgrid, sin
from Image import QUAD

import lsst.afw.geom.ellipses as Ellipses

#from lsst.afw.geom import ellipses
#from lsst.afw.geom.geomLib import Point2D
#from lsst.afw.detection.detectionLib import Footprint
#from lsst.afw.geom.ellipses.ellipsesLib import BaseCore



if __name__ == '__main__':
    print "Running basic cluster finder"

# set up some paths for convenience
    home_dir = expanduser("~")
    output_path = home_dir + '/output/'
    input_path = home_dir + '/dl/'

#    input_file = 'starfield_1.fits.gz' # small array, no tree rings
#    input_file = '20_9_100_rings_420big.fits' # big tree ring data
#    input_file = '8_9_100_rings_420.fits' #small tree ring data
#    input_file = 'ben/ellipse2.fits.gz' # just an ellipse from Ben
    input_file = "darks/from ccdtest.e2v.CCD250.112-04.dark.20140419-190507/000-00_dark_dark_500.00_001_20140420034133.fits"


    exposure = afwImg.ExposureF(input_path + input_file)
    maskedImage = exposure.getMaskedImage()


    image = maskedImage.getImage()
    mask = maskedImage.getMask()
    variance = maskedImage.getVariance()

    # initialise DS9, deal with a bug in its launching
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'

    # show the file
    ds9.mtv(image)



    # stats
    statFlags = math.NPOINT | math.MEAN | math.STDEV | math.MAX | math.MIN | math.ERRORS | math.STDEVCLIP
    control = math.StatisticsControl()
    SAT = afwImg.MaskU_getPlaneBitMask("SAT")
    control.setAndMask(SAT)

    # Get the stats and print them out
    imageStats = math.makeStatistics(maskedImage, statFlags, control)
    numBins = imageStats.getResult(math.NPOINT)[0]
    mean = imageStats.getResult(math.MEAN)[0]
    _max = imageStats.getResult(math.MAX)[0]
    sigmaclip = imageStats.getResult(math.STDEVCLIP)[0]
    print "The image has dimensions %i x %i pixels" % (maskedImage.getWidth(), maskedImage.getHeight())
    print "Mean = %s" % mean
    print "Max = %s" % _max
    print "nPx = %s\n" % numBins
    print "sigmaclip = %s\n" % sigmaclip




    # let's find some clusters!
    # set up some finding parameters
    thresholdValue = mean
    npixMin = 5
    grow = 1
    isotropic = False

    # do the finding
    threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
    footPrintSet = afwDetect.FootprintSet(maskedImage, threshold, "DETECTED", npixMin)
    footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)

    footPrints = footPrintSet.getFootprints()
    footPrintSet.setMask(maskedImage.getMask(), "DETECTED")
    print footPrints.size(), "footPrint(s) found\n"



    
    footprint = afwDetect.Footprint()
    xcoords, ycoords = [], []
    majors, minors, thetas = [], [], []
    xvectors, yvectors = [], []
    ixxs, iyys, ixys = [], [], []

    for footprint in footPrints:
        #peaks, NOT centroids
#        xcoord = footprint.getPeaks()[0].getFx()
#        ycoord = footprint.getPeaks()[0].getFy()
#        ds9.dot('X', xcoord, ycoord)

        quadshape = footprint.getShape()

        axesshape = Ellipses.Axes(quadshape)

        a = axesshape.getA()
        b = axesshape.getB()
        theta = axesshape.getTheta()

        majors.append(a)
        minors.append(b)
        thetas.append(theta)
#        
#        print 'a', a
#        print 'b', b
#        print 'theta', theta

        xvectors.append (a * np.cos(theta* (3.1415926 / 180)))
        yvectors.append (b * np.sin(theta* (3.1415926 / 180)))
                                 
        centroid_x, centroid_y = footprint.getCentroid()
#        centroid_y = footprint.getCentroid()[1]
        xcoords.append(centroid_x)
        ycoords.append(centroid_y)
        ds9.dot("x",centroid_x,centroid_y)# cross on the peak
    
    
        Ixx = quadshape.getIxx()
        Iyy = quadshape.getIyy()
        Ixy = quadshape.getIxy()
#        print 'Ixx', quadshape.getIxx()
#        print 'Iyy', quadshape.getIyy()
#        print 'Ixy', quadshape.getIxy()
        ixxs.append(Ixx)
        iyys.append(Iyy)
        ixys.append(Ixy)
        argstring = "@:"+str(Ixx)+','+str(Ixy)+','+str(Iyy)
#        ds9.dot(argstring,centroid_x,centroid_y) #ellipse around the centroid


#    ds9.zoom(5, footPrints[0].getPeaks()[0].getFx(), footPrints[0].getPeaks()[0].getFy())
#    ds9.zoom(4, 2050, 2060)
    ds9.zoom(6, 2000, 2035)


#
#    data = np.loadtxt(input_path + "/cat/mystars_420_20140430.cat")
#
#    o = data[:, 0] #number
#    a = data[:, 1] #flux
#    area = data[:, 2] #flux above threshold
#    x = data[:, 3] #x pos
#    y = data[:, 4] #y pos
#    x2 = data[:, 5] #x pos variance
#    y2 = data[:, 6] #y pos variance
#    xy = data[:, 7] # x-y covariance
#    aa = data[:, 8] #major axis RMS
#    bb = data[:, 9] #minor axis RMS
#    angle = data[:, 10] #theta in degrees
#
#    e1 = (x2 - y2) / (x2 + y2)
#    e2 = (2 * xy) / (x2 + y2)
#
#    theta = np.arctan2(e2, e1) / 2.
#    r = np.sqrt(e1 ** 2 + e2 ** 2)
#    u = r * np.cos(theta)
#    v = r * np.sin(theta)
#
#    #convert LSST pixels to arcsec
#    x1 = x / 5.
#    y1 = y / 5.
#
#
#
#    #arrow plot
#    #xa,ya = meshgrid( arange(0.,41.,1.),arange(0.,41.,1.) )
#    pl.figure()
#    sexQ = pl.quiver(x, y, u, v, angles='uv', scale=1)#, headlength=0, headaxislength=0, headwidth=0, pivot='middle')
#    pl.title('Tree ring ellipticity - sextractor')
#
#
#
#
#
#    my_e1 = (np.array(ixxs) - np.array(iyys)) / (np.array(ixxs) + np.array(iyys))
#    my_e2 = (2 * np.array(ixys)) / (np.array(ixxs) + np.array(iyys))
#
#    my_theta = np.arctan2(my_e2, my_e1) / 2.
#    my_r = np.sqrt(my_e1 ** 2 + my_e2 ** 2)
#    my_u = my_r * np.cos(my_theta)
#    my_v = my_r * np.sin(my_theta)
#
#
#    print "My theta"
#    for t in my_theta:
#        print t
#
#    #convert LSST pixels to arcsec
#    my_x1 = x / 5.
#    my_y1 = y / 5.
#
#
#    #arrow plot
#    #xa,ya = meshgrid( arange(0.,41.,1.),arange(0.,41.,1.) )
#    pl.figure()
#    #  sexQ = pl.quiver(x, y, u, v, angles='uv', scale=1)#, headlength=0, headaxislength=0, headwidth=0, pivot='middle')
#    my_sexQ = pl.quiver(xcoords, ycoords, my_u, my_v, angles='uv', scale=5)#, headlength=0, headaxislength=0, headwidth=0, pivot='middle')
#    pl.axis([1700, 2300, 1800, 2250])
#    pl.title('DMStack Ellipticity measurement')
#    pl.show()
















#    n, bins, pathches = plt.hist(peakvalues, bins=10)
#    plt.xlabel("Peak Brightness")
#    plt.savefig(output_path + 'peak_histo.png')
#    plt.show()



    ###########################################

    # zoom to ROI
#    plt.xlim(2000, 2100)
#    plt.ylim(2000, 2100)

    # open the image window
#    plt.show()

    # save the image to a file
#     plt.savefig(output_path + 'testplot.png')

    print '\n***End code***'







