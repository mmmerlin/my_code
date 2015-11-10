from my_functions import *

#     OpenTimepixInDS9('/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/timepix/run8/1_0214.txt', True)
import lsst.afw.display.ds9 as ds9

#     image = MakeCompositeImage_Timepix('/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/timepix/run8/', 0, 255, 0, 255, 0, 999999, -99999, 9999999, return_raw_array=False)



# path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/timepix/run745/'
# path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/pimms_to_timepix/run8/'
path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/pimms_to_timepix/run5/'
mask_pixels = GeneratePixelMaskListFromFileset(path, noise_threshold = 0.1, xmin = 0, xmax = 255, ymin = 0, ymax = 255, file_limit = 1e6)
n_masked_pix = len(mask_pixels[0])
print 'masking %s pixels'%n_masked_pix


data_array = MakeCompositeImage_Timepix(path, 0, 255, 0, 255, 0, 1e6, -99999, 9999999, return_raw_array=True)
MaskBadPixels(data_array, mask_pixels)
ViewIntensityArrayInDs9(data_array)
exit()



try:
    ds9.initDS9(False)
except ds9.Ds9Error:
    print 'DS9 launch bug error thrown away (probably)'

ds9.mtv(image)
exit()