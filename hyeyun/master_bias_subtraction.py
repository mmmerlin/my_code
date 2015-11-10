from AssembleImage import AssembleImage
import lsst.afw.display.ds9 as ds9
import lsst.afw.image as afwImage 
from os import listdir


bias_dir = '/mnt/hgfs/VMShared/data/hyeyun_big/bias/'
short_exp_dir = '/mnt/hgfs/VMShared/data/hyeyun_big/short/'

# long_exp_filename = '/mnt/hgfs/VMShared/data/hyeyun_small/long/113-10-hiloflux2_shutter_675_412_shutter1_20150903223804.fits'
long_exp_filename = '/mnt/hgfs/VMShared/data/hyeyun_small/long/113-10-hiloflux2_shutter_675_413_shutter1_20150903223838.fits'
long_exp_length = 60.376


bias_files = listdir(bias_dir)
print 'Found %s bias files'%len(bias_files)
short_files = listdir(short_exp_dir)
print 'Found %s short exposure files'%len(short_files)

short_exp_length_each = 0.03
short_exp_length_total = short_exp_length_each*len(short_files)


# temp_image = AssembleImage(short_exp_dir+short_files[0], trim = True)
# # temp_image = AssembleImage(bias_dir+bias_files[0], trim = False)
# print temp_image.getArray().shape
# ds9.mtv(temp_image)
# exit()


long_exp = AssembleImage(long_exp_filename, trim = True)
long_exp_array = long_exp.getArray()

example_short_image = AssembleImage(short_exp_dir+short_files[0], trim = True)
x_size = example_short_image.getWidth()
y_size = example_short_image.getHeight()
assert x_size == long_exp.getWidth()
assert y_size == long_exp.getHeight()
del example_short_image



print 'Master bias image = %s x %s'%(x_size,y_size)
master_bias = afwImage.ImageF(x_size, y_size, 0.0)

mb_array = master_bias.getArray()
for bias_file in bias_files:
    mb_array += AssembleImage(bias_dir + bias_file, trim = True).getArray()
mb_array /= float(len(bias_files))
long_exp_array -= mb_array

short_exp_coadd = afwImage.ImageF(x_size, y_size, 0.0)
short_exp_coadd_array = short_exp_coadd.getArray()
for short_file in short_files:
    short_exp_coadd_array += (AssembleImage(short_exp_dir + short_file, trim = True).getArray() - mb_array)


output_image = afwImage.ImageF(x_size, y_size, 0.0)
output_image_array = output_image.getArray()
output_image_array += long_exp.getArray()
output_image_array /= (short_exp_coadd_array * (long_exp_length/short_exp_length_total)) 


print 'Averaged %s files for master bias'%len(bias_files)
print 'Averaged %s short exposures, subtracting master bias from each'%len(short_files)
print 'Long exposure is \t%s s long'%long_exp_length
print 'Short exposures are \t %s s long each'%short_exp_length_each
print 'Short exposures are \t %s s long total'%short_exp_length_total
print 'Short exp coadd is therefore %s x %s = %s s long'%(len(short_files), short_exp_length_each, len(short_files) * short_exp_length_each)
print 'Short coadd was therefore scaled up by %s x'%(long_exp_length/short_exp_length_total)
print 'Resulting ratio is displayed'

ds9.mtv(output_image)

print 'done'
exit()






