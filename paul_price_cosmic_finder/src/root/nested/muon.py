#!/usr/bin/env python

import argparse
import lsst.afw.image as afwImage
import lsst.afw.detection as afwDet
from lsst.pex.config import Config, Field, ConfigField, makePolicy
from lsst.meas.algorithms.detection import (SourceDetectionTask, estimateBackground, BackgroundConfig,)
import lsst.meas.algorithms as measAlg


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
        import lsst.afw.display.ds9 as ds9
        import lsst.afw.display.utils as displayUtils

        ds9.mtv(exp, title="Exposure with CRs")

        with ds9.Buffering():
            for cr in crList:
                displayUtils.drawBBox(cr.getBBox(), borderWidth=0.55)



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
        import lsst.afw.display.ds9 as ds9
        frame = 1
        ds9.mtv(bgSubExp, frame=frame, title="Background-subtracted exposure")
        with ds9.Buffering():
            for fp in fpSet.getFootprints():
                peakList = fp.getPeaks()
                for p in peakList:
                    ds9.dot("x", p.getFx(), p.getFy(), frame=frame)

    # XXX Work with footprints here

    psf = measAlg.SingleGaussianPsf(config.psfSize, config.psfSize, config.psfSigma)
    exp.setPsf(psf)

    cosmicray(exp, config.cosmicray, display=display)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("exposureName", help="Name of exposure")
    parser.add_argument("-C", "--config-file", dest="configFile", help="Name of config override file")
    parser.add_argument("--display", default=False, action="store_true", help="Display results?")
    args = parser.parse_args()

    config = MuonConfig()
    if args.configFile:
        config.load(args.configFile)

    main(args.exposureName, config, display=args.display)

