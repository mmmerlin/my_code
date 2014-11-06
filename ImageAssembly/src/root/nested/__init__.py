import lsst.afw.detection   as afwDetect
import lsst.afw.display.utils as displayUtils
from lsst.meas.algorithms.detection import (SourceDetectionTask, estimateBackground, BackgroundConfig,)
import lsst.meas.algorithms as measAlg

import numpy as np
from os.path import expanduser
import lsst.afw.image as afwImg
import lsst.afw.display.ds9 as ds9

from image_assembly import AssembleImage, MakeBiasImage, GetImage_SingleAmp


if __name__ == '__main__':
#    filename = '/home/mmmerlin/Desktop/VMShared/temp/ITL.fits'
    filename = '/home/mmmerlin/Desktop/VMShared/temp/phosim.fits'
    
    try: # initialise DS9, deal with a bug in its launching
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'
    print 'called ds9 to display' 
        
#    print "Processing %s..." %filename

#    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'
#    image = AssembleImage(filename, subtract_background=True)# make image, subtract background and assemble exposure

    exposure = afwImg.ExposureF(filename)
    data = exposure.getMaskedImage().getImage().getArray()
    
    print data.shape
    data.transpose()
    print data.shape
    
    
    
#    maskedImg = afwImg.MaskedImageF(image)
        
#    ds9.mtv(exposure.getMaskedImage())
    
    print "finished."
