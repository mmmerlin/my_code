from __builtin__ import str, range, len # why does it put these in when that is unnecessary?!

import lsst.afw.detection     as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.meas.algorithms   as measAlg
import lsst.afw.image         as afwImg
import lsst.afw.display.ds9   as ds9

from os import listdir, system
from os.path import isfile
from string import zfill


if __name__ == '__main__':

    path = '/mnt/hgfs/VMShared/Data/des_darks/'
    files = [filename for filename in listdir(path) if isfile(path + filename)]
    overscan_script = '/mnt/hgfs/VMShared/Code/git/my_functions/overscanDECam.py'
    
    for filename in files:
        for i in range(1,32):
            argstring = ' -i ' + path + filename + ' -o ' + path + 'split/' + filename + '_ext_N' + zfill(i,2) + '.fits' + ' -e N' + str(i)
            system('python ' + overscan_script + argstring)
            argstring = ' -i ' + path + filename + ' -o ' + path + 'split/' + filename + '_ext_S' + zfill(i,2) + '.fits' + ' -e S' + str(i)
            system('python ' + overscan_script + argstring)
            
        
