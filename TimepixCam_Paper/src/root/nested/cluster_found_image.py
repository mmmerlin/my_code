from my_functions import *
import lsst.afw.detection     as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.meas.algorithms   as measAlg
import lsst.afw.image         as afwImg
import lsst.afw.display.ds9   as ds9
from TrackFitting import *

    
if __name__ == '__main__':
    
    tracklist = []
    
    timepix_path_1 = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/4-9-15/100V_TOF/'
    filename = timepix_path_1 + 'eight_0001.txt'

    out_path = '/mnt/hgfs/VMShared/output/TimepixCam_paper/'


#     OpenTimepixInDS9(filename, binary=False)

    
    image, npix = TimepixToExposure_binary(filename,  1, 254, 1, 254)
            
    ds9.mtv(image)
            
    
    THRESHOLD = 1
    GROW = 0
    ISOTROPIC = False
    N_PIX_MIN = 1


    threshold = afwDetect.Threshold(THRESHOLD)
    footPrintSet = afwDetect.FootprintSet(image, threshold, N_PIX_MIN)
    footPrintSet = afwDetect.FootprintSet(footPrintSet, GROW, ISOTROPIC)
    footPrints = footPrintSet.getFootprints()


    footPrints = footPrintSet.getFootprints()
    print "Found %s footprints in file %s"%(footPrints.size(),  filename)


    for pointnum, footprint in enumerate(footPrints):
        displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5)


    arg = 'saveimage jpeg ' + str(out_path + str(1) + '_example_frame.jpeg') + ' 100'
    ds9.ds9Cmd(arg)
    
    exit()
    













