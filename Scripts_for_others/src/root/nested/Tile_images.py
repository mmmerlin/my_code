import lsst.afw.image   as afwImage
import lsst.afw.display.ds9 as ds9
import os

input_path = '/mnt/hgfs/VMShared/temp/12_noatmo_850/'
save_file =  '/mnt/hgfs/VMShared/temp/combined.fits.gz'
#NB the .gz at the end of the save filename - this turns a ~625MB file into a ~4MB file!

file_list = os.listdir(input_path)

dummy_image = afwImage.ImageF(input_path + file_list[0])
width, height = (dummy_image.getWidth(), dummy_image.getHeight())

x_gap = 200
y_gap = 500

new_width  = (width*3)  + (2*x_gap)
new_height = (height*3) + (2*y_gap)

gutter_value = -999 #value to set the pixels in the gaps to

big_image = afwImage.ImageF(new_width, new_height, gutter_value)

print 'Individual image size = %s x %s'%(width,height)
print 'Big image size = %s x %s'%(new_width,new_height)

for filename in file_list:
    #Get the coordinate from the filename
    substrings = str.split(filename,'_')
    xy = substrings[-2]
    x  = int(xy[-2])
    y  = int(xy[-1])

    #load the file, determine location at which to insert and insert
    image = afwImage.ImageF(input_path + filename)
    loc_x, loc_y = x*(width+x_gap), y*(height + y_gap)
    big_image[loc_x:loc_x+width, loc_y:loc_y+height] = image
    
big_image.writeFits(save_file)
# ds9.mtv(big_image)
print 'Finished'