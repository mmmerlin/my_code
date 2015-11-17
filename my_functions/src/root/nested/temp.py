import lsst.afw.display.ds9 as ds9
import lsst.afw.image as afwImage


filename = '/mnt/hgfs/VMShared/Data/hyeyun_small/long/113-10-hiloflux2_shutter_675_411_shutter1_20150903223736.fits'

image = afwImage.ImageF(filename,2) #2-17 are where the actual data is.

ds9.mtv(image)

print'done'

