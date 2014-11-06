#import the DMstack stuff
import lsst.afw.math                    as math
import lsst.afw.table                   as afwTable
import lsst.afw.image                   as afwImg
import lsst.pex.policy                  as pexPol
import lsst.afw.display.ds9             as ds9
import lsst.meas.algorithms.detection   as sDet
import lsst.meas.algorithms             as measAlg
import lsst.afw.detection               as afwDet

#import lsst.ip.isr.isr.createPsf        as createPsf #createPsf function has been moved from lsst.meas.algorithms to lsst.ip.isr.isr
#import lsst.ip.isr.isr.createPsf as createPsf

from lsst.ip.isr import createPsf

#import lsst.meas.algorithms.measurement.SourceMeasurementConfig as sourceMeasConf


from os.path import expanduser



#import stuff for plotting
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.colors import LogNorm
# import pylab as P


import matplotlib.mlab as mlab


if __name__ == '__main__':

    print "Running Merlin's DM_Sextractor"


#   setup paths for ease of use
    home_dir = expanduser("~")
    input_path = home_dir + '/dl/'
    output_path = home_dir + '/output/'
    input_file = 'starfield_1.fits.gz'

#   load the file and create a masked image
    exposure = afwImg.ExposureF(input_path + input_file)
    masked_image = afwImg.ExposureF.getMaskedImage(exposure)

#   configure a background policy. Unnecessary for us at this point, but good to do for later to show how it's done
#    bgPol = pexPol.Policy()
#    bgPol.add('binsize', 30)
#    bgPol.add('algorithm', 'NATURAL_SPLINE')


#    bgPol.add('source', 'astrom')
#    bgPol.add('astrometry', 'SDSS')
#    bgPol.add('shape', 'SDSS')
#    bgPol.add('photometry', 'NAIVE')
#    bgPol.add('centroidAlgorithm', 'SDSS')
#    bgPol.add('shapeAlgorithm', 'SDSS')
#    bgPol.add('photometryAlgorithm', 'NAIVE')
#    bgPol.add('apRadius', 3.0)

#    errors = 1
#    errors = bgPol.validate()
#     "Errors = ", str(errors)



#   calculate background and perform background subtraction
#    background, subtractedImg = sDet.estimateBackground(exposure, bgPol, True)
#    masked_image = afwImg.ExposureF.getMaskedImage(subtractedImg)
#    img = afwImg.MaskedImageF.getImage(masked_image)
#    ds9.mtv(img)

#   configure a detection policy - this is what is required to count as a star (or an ion cluster)
    detPol = pexPol.Policy()
    detPol.add('minPixels', 10) ## The source must have at least this many pixels
    detPol.add('nGrow', 1)
    detPol.add('thresholdValue', 30)
    detPol.add('thresholdType', 'value')
    detPol.add('thresholdPolarity', 'both')

#   width of the double gaussian smearing kernel used in the PSF
    FWHM = 2 ## stands for full-width half-max of the Gaussian which models the PSF
#   psf = measAlg.createPSF("DoubleGaussian", 15, 15, FWHM/(2*math.sqrt(2*math.log(2))))
    psf = createPsf(FWHM) #not equivalent to the example code as this function returns the equivalent of calling measAlg.createPSF("DoubleGaussian", 9, 9, FWHM/(2*math.sqrt(2*math.log(2))))


#   find the sources
#   dsPos,dsNeg = sDet.detectSources(subtractedImg,psf,detPol) ## Returns the positive and negative detections, but
    sDetConf = sDet.SourceDetectionConfig()
    sDetTask = sDet.SourceDetectionTask()



#   objects = dsPos.getFootprints()
#    objects = sDetTask.detectFootprints()
#    print len(objects) ## Prints how many sources were found in your image


    sourcePol = pexPol.Policy()
    sourcePol.add('source', 'astrom')
    sourcePol.add('astrometry', 'SDSS')
    sourcePol.add('shape', 'SDSS')
    sourcePol.add('photometry', 'NAIVE')
    sourcePol.add('centroidAlgorithm', 'SDSS')
    sourcePol.add('shapeAlgorithm', 'SDSS')
    sourcePol.add('photometryAlgorithm', 'NAIVE')
    sourcePol.add('apRadius', 3.0)
    
    print sourcePol.names()
    print sourcePol.canValidate()
    
#    measureSources = measAlg.measurement.SourceMeasurementConfig.makeMeasureSources(exposure, sourcePol, psf)
    sDetTask.detectFootprints(exposure, sigma = 25)


    
    dsPos = objects.positive()
    
    print str(objects.numPos)
    print str(objects.numPos)
    print str(objects.numPos)
  
    
  
  
  
  
# # #    sourceList = afwDet.SourceSet()
# # #    for i in range(len(objects)):
# # #        source = afwDet.Source()
# # # 
# # #        measureSources.apply(source, objects[i])
# # #        sourceList.append(source)
# # #        source.setId(i)
# # #        print source
# # #        ## Locate the center of each source and display a red +
# # #        xc, yc = source.getXAstrom() - masked_image.getX0(), source.getYAstrom() - masked_image.getY0()
# # #        ds9.dot("+", xc, yc, size=5, ctype=ds9.RED)


#
#    for footprint in objects:
#        source = afwDet.Source()
#
#        measureSources.apply(source, objects[i])
#        sourceList.append(source)
#        source.setId(i)
#        print source
#        ## Locate the center of each source and display a red +
#        xc, yc = source.getXAstrom() - masked_image.getX0(), source.getYAstrom() - masked_image.getY0()
#        ds9.dot("+", xc, yc, size=5, ctype=ds9.RED)
#
#
#
#    threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
#    footPrintSet = afwDetect.FootprintSet(maskedImage, threshold, "DETECTED", npixMin)
#    footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
#
#    footPrints = footPrintSet.getFootprints()
#
#
#    footPrintSet.setMask(maskedImage.getMask(), "DETECTED")
#    
#    for i in range(0, footPrints.size()):
#        print "Footprint:", i
#
#        peak = footPrints[i].getPeaks()[0]
#        print "A peak of value", peak.getPeakValue()
#        print "was found at X =", peak.getFx(), "Y =", peak.getFy()
#
#
#    footPrints = footPrintSet.getFootprints()
#
#
#    for footprint in footPrints:
#        print footprint.getPeaks()[0].getFx(), ",", footprint.getPeaks()[0].getFy(), ",", footprint.getPeaks()[0].getPeakValue()
#        peakvalues.append(footprint.getPeaks()[0].getPeakValue())
#
#




























    print '\n***End code***'






