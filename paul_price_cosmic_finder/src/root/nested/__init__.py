#!/usr/bin/env python
import argparse
import lsst.afw.image as afwImage
import lsst.afw.detection as afwDet
from lsst.pex.config import Config, Field, ConfigField, makePolicy
from lsst.meas.algorithms.detection import (SourceDetectionTask, estimateBackground, BackgroundConfig,)
import lsst.meas.algorithms as measAlg
import lsst.afw.display.utils as displayUtils
import lsst.afw.display.ds9 as ds9


from os.path import expanduser


class MuonConfig(Config):
    detection = ConfigField(dtype=SourceDetectionTask.ConfigClass, doc="Detection config")
    background = ConfigField(dtype=BackgroundConfig, doc="Background subtraction config")
    cosmicray = ConfigField(dtype=measAlg.FindCosmicRaysConfig, doc="Cosmic-ray config")
    psfSigma = Field(dtype=float, default=2.0, doc="PSF Gaussian sigma")
    psfSize = Field(dtype=int, default=21, doc="PSF size (pixels)")

    def setDefaults(self):
        super(MuonConfig, self).setDefaults()
        self.cosmicray.keepCRs = True # We like CRs!
        self.cosmicray.nCrPixelMax = 1000000
        self.cosmicray.minSigma = 5.0
        self.cosmicray.min_DN = 1.0
        self.cosmicray.cond3_fac2 = 0.4

def cosmicray(exp, config, display=False):
    bg = 0.0 # We background-subtracted, right?
    crList = measAlg.findCosmicRays(exp.getMaskedImage(), exp.getPsf(), bg, makePolicy(config), True)

    if crList is None:
        print "No CRs found"
        return

    mask = exp.getMaskedImage().getMask()
    crBit = mask.getPlaneBitMask("CR")
    afwDet.setMaskFromFootprintList(mask, crList, crBit)
    num = len(crList)

    print "Found %d CRs" % num

    if display:
        frame = 2
#        ds9.mtv(exp.getMaskedImage().getImage(), title="Exposure with CRs")
#        ds9.mtv(exp.getMaskedImage().getMask(), frame = frame, title="Exposure with CRs")

#        with ds9.Buffering():
#            for cr in crList:
#                print "Drawing bbox......"
#                displayUtils.drawFootprint(cr, borderWidth = 2.5)
##                displayUtils.drawBBox(cr.getBBox(), borderWidth=5.55)



def main(expName, config, display=False):
    exp = afwImage.ExposureF(expName)

    # Assume exposure is bias-subtracted, CCD-assembled, has variance and mask plane.
    # If not, put code here to fix what's lacking.

    bg, bgSubExp = estimateBackground(exp, config.background, subtract=True)

    detection = SourceDetectionTask(config=config.detection)
    detResults = detection.detectFootprints(bgSubExp, sigma=config.psfSigma)

    fpSet = detResults.positive

    print "Found %d positive footprints" % len(fpSet.getFootprints())

    if display:
        print "Displaying results..."
        frame = 0
        ds9.mtv(bgSubExp.getMaskedImage().getImage(), frame=frame, title="Background-subtracted exposure")
        with ds9.Buffering():
            for fp in fpSet.getFootprints():
                print "x = %s" %(fp.getBBox())
                displayUtils.drawBBox(fp.getBBox(), borderWidth = 0.55)
                peakList = fp.getPeaks()
                for p in peakList:
                    ds9.dot("x", p.getFx(), p.getFy(), frame=frame)
        

    # XXX Work with footprints here

    psf = measAlg.SingleGaussianPsf(config.psfSize, config.psfSize, config.psfSigma)
    exp.setPsf(psf)

    cosmicray(exp, config.cosmicray, display=display)


if __name__ == "__main__":
    print "Running Cosmic Finder"
    home_dir = expanduser("~")

    DISPLAY = True

#    datafile = "q.fits"
    datafile = "~/dl/darks/from ccdtest.e2v.CCD250.112-04.dark.20140419-190507/000-00_dark_dark_500.00_001_20140420034133.fits"
    config_path = home_dir + "/workspace/paul_price_cosmic_finder/src/root/nested/config.py"


    config = MuonConfig()
#    config.load(config_path)

    main(datafile, config, DISPLAY)
#    main(datafile, display = DISPLAY)
    
    print "Finished."
