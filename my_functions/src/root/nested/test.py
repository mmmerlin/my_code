from AssembleImage import AssembleImage
import lsst.afw.display.ds9 as ds9

filename = '/mnt/hgfs/VMShared/data/temp/XEDShadowImageITL.fits'

image = AssembleImage(filename)

ds9.mtv(image)

print 'done'
exit()