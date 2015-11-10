import lsst.afw.image as afwImage
import lsst.afw.display.ds9 as ds9
import lsst.obs.lsstSim as obs_lsstSim

import numpy as np
import scipy.ndimage


# DISPLAY = False
DISPLAY = True

def _warpFuncWidth(x,xmax,a,c):
    return x + (a*np.exp(-b*(xmax-x) - c*np.exp(-d*x)))


def UnwarpEdge(filename, a,b,c,d, output_filename):
    rebin_factor = 3
    
    a = 21.5
    b = 0.03297
    c = a
    d = b
    
    original_image = afwImage.ImageF(filename)
    pixels = original_image.getArray()
    height,width = pixels.shape

    print 'FYI, you are messing with %s pixels in python :S'%(width*height)
    

    fine_pixels = scipy.ndimage.zoom(pixels,rebin_factor,order=3)
   
    fine_image = afwImage.ImageF(fine_pixels)
    fine_height, fine_width = fine_image.getArray().shape
    assert fine_height == height * rebin_factor
    assert fine_width == width * rebin_factor
    
    fine_pixels = scipy.ndimage.zoom(pixels,0.333,order=3)
    
    fine_pixels_original = fine_pixels.clone()
    
#     exit()

    for x in xrange(fine_height):
        for y in xrange(fine_width):
            value = fine_pixels_original[y,x]
            x_prime = _warpFunc(value, height,a,b,c,d)
            
    
    
    
    
    
    
    if DISPLAY: ds9.mtv(original_image, frame = 0)
    if DISPLAY: ds9.mtv(fine_image, frame = 1)
    
    
     
#     new_image = afwImage.ImageF(pixels*2)
#     new_image.writeFits(output_filename)
#     
#     if DISPLAY: ds9.mtv(new_image, frame = 1)
    
    
    print 'Finished'
#     return new_image
    
    
    
    
if __name__ == "__main__":
    filename = '/mnt/hgfs/VMShared/useful/g08_gal.fits'
    output_filename = '/mnt/hgfs/VMShared/useful/g08_gal_unwarped.fits'
    
    a=1
    b=1
    c=1
    d=1
    
    UnwarpEdge(filename, a, b, c, d,output_filename)
    
