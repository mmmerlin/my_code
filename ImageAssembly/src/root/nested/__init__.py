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
#     filename = '/home/mmmerlin/Desktop/VMShared/temp/phosim.fits'
#     filename = '/home/mmmerlin/Desktop/VMShared/data/temp/grid.fits'
#     filename = '/home/mmmerlin/Desktop/VMShared/temp/120.00sec_frame_103.1.fits.fixed'
    
    
    filename = '/home/user01/Desktop/example_files/e2v_fringes.fits'
    
    
#     try: # initialise DS9, deal with a bug in its launching
#     ds9.initDS9(False)
#     except ds9.Ds9Error:
#         print 'DS9 launch bug error thrown away (probably)'
#     print 'called ds9 to display' 
        
#    print "Processing %s..." %filename

    metadata_filename = '/home/user01/Desktop/example_files/e2v_herring_bone.fits'


#     gains = [3.863893926,3.889311364,3.839592821,3.880267774,3.829443828,3.859452995,3.8523837,3.826228492,3.913972084,3.952911679,3.844514444,3.9919436,3.897239172,3.957293714,3.879582217,3.888644858] #112-04 900 file set gains
    gains = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]


    image = AssembleImage(filename, metadata_filename, subtract_background = True, gain_correction_list=gains)


#     image = AssembleImage(filename, metadata_filename, True)
#     image = AssembleImage(filename, metadata_filename, True)
#     image = AssembleImage(filename, subtract_background=True)# make image, subtract background and assemble exposure
    
#     image = GetImage_SingleAmp(filename, False, 8)
    ds9.mtv(image)
    print 'done'
    
    exit()
    
    exposure = afwImg.ExposureF(filename)
    data = exposure.getMaskedImage().getImage().getArray()
    
#     print data.shape
#     data.transpose()
#     print data.shape
    
    
    
#    maskedImg = afwImg.MaskedImageF(image)
        
#     ds9.mtv(exposure.getMaskedImage().getImage())
    
    print "finished."
