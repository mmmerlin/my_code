import lsst.afw.math        as math
import lsst.afw.table       as afwTable
import lsst.afw.image       as afwImg
import lsst.afw.detection   as afwDetect
import lsst.afw.display.ds9 as ds9

import os
from os.path import expanduser
import time

if __name__ == '__main__':
    print "Running Paul's analysis"
    DEBUG = False

    # set up paths and get files
    home_dir = expanduser("~")
    input_path = home_dir + '/dl/pauls_data/'
#    outputfilename = home_dir + '/output/midlinescan.txt'
    outputfilename = home_dir + '/Desktop/DMStack VM Shared/midlinescan.txt'

    filelist = []
    for name in os.listdir(input_path):
        if os.path.isfile(os.path.join(input_path, name)): filelist.append(os.path.join(input_path, name))




#===============================================================================
    #for doing a single file for debug
#    filelist = []
#    filelist.append(home_dir + '/dl/pauls_data/20130104221032-986.fits')
##==============================================================================

    

    laser_xs = []; laser_ys = []; centroid_xs = []; centroid_ys = []

    t0 = time.time()
    n_Processed = 0
    n_Clean = 0
    n_Multiple = 0
    n_Zero = 0
    for filename in filelist:
        # image from FITS file
        exposure = afwImg.ExposureF(filename)
        maskedImage = exposure.getMaskedImage()
        

        # setup stats
        statFlags = math.NPOINT | math.MEAN | math.STDEV | math.STDEVCLIP | math.MAX | math.MIN | math.ERRORS
        control = math.StatisticsControl()
        SAT = afwImg.MaskU_getPlaneBitMask("SAT")
        control.setAndMask(SAT)


        # Get the stats and print them out
        imageStats = math.makeStatistics(maskedImage, statFlags, control)
        mean = imageStats.getResult(math.MEAN)[0]
        stddev = imageStats.getResult(math.STDEV)[0]
        stddev_clip = imageStats.getResult(math.STDEVCLIP)[0]
        maxval = imageStats.getResult(math.MAX)[0]


        #set up finding parameters
        thresholdValue = mean + (6 * stddev_clip)
        npixMin = 5
        grow = 0
        isotropic = False


        # do the finding
        threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
        footPrintSet = afwDetect.FootprintSet(maskedImage, threshold, "DETECTED", npixMin)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)

        footPrints = footPrintSet.getFootprints()
        footPrintSet.setMask(maskedImage.getMask(), "DETECTED")

        n_Processed += 1
        if (footPrints.size() >  1):
            print "MULTIPLE FOOTPRINT WARNING - ", footPrints.size(), " footPrints found in image %s" % filename
            n_Multiple += 1
        elif (footPrints.size() == 0):
            print "ZERO FOOTPRINT WARNING - ", footPrints.size(), " footPrints found in image %s" % filename
            print "Skipping %s due to lack of footprint" % filename
            n_Zero += 1
            continue
        else:
            n_Clean += 1
        

        footprint = afwDetect.Footprint()
        footprint = footPrints[0]

        peak_x = footprint.getPeaks()[0].getFx()
        peak_y = footprint.getPeaks()[0].getFy()
        centroid_x, centroid_y = footprint.getCentroid()

        if DEBUG:
            print "Mean = %s" % mean
            print "Max = %s" % maxval
            print "sigma = %s" % stddev
            print "sigma_clip = %s" % stddev_clip
            print "footprint contains %s pixels" % footprint.getNpix()
            print "centroid at x=%s , y=%s" % (centroid_x, centroid_y)

            try:  #    initialise DS9, deal with a bug in its launching
                ds9.initDS9(False)
            except ds9.Ds9Error:
                print 'DS9 launch bug error thrown away (probably)'
            ds9.mtv(maskedImage.getImage())
            ds9.dot("x", centroid_x, centroid_y) #ellipse around the centroid
            ds9.zoom(7, centroid_x, centroid_y)


        #get laser spot location from metadata
        metaData    = exposure.getMetadata()
#        print "Metadata printout of ", metaData.nameCount(), "items."
#        for name in metaData.names():
#            print name, "\t", metaData.get(name)
#        
        laser_xs.append(metaData.get('AXIS.AX1'))
        laser_ys.append(metaData.get('AXIS.AX2'))
        centroid_xs.append(centroid_x)
        centroid_ys.append(centroid_y)
        



    t1 = time.time()
    print "Processing took %s seconds" % (t1 - t0)
    print "Number processed = %s" % n_Processed
    print "Number of zero hit frames = %s" % n_Zero
    print "Number of single hit frames = %s" % n_Clean
    print "Number of multiple hit frames = %s" % n_Multiple
    
    
    outfile = open(outputfilename, 'w')
    sep = '\t'
    
    outfile.write('laser_x' + sep + ' laser_y' + sep + ' centroid_x' + sep + ' centroid_y\n')
    for i in range(len(laser_xs)):
        if (centroid_ys[i] > 1450 and centroid_ys[i] <1550):
            outstring = str(laser_xs[i]) +sep+ str(laser_ys[i]) +sep+ str(centroid_xs[i]) +sep+ str(centroid_ys[i]) +'\n'
            outfile.write(outstring)
    outfile.close()
    
    

    print '\n***End code***'







