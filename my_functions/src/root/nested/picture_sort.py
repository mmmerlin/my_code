import os
import exifread
import numpy as np


in_path = '/mnt/hgfs/VMShared/India_suction/'
outfile = open('/mnt/hgfs/VMShared/temp/pic_infos.txt','w')


files = os.listdir(in_path)
print "Found %s files"%len(files)


# in_path = '/mnt/hgfs/VMShared/temp/'
# files = ['IMG_2.JPG']



for filenum,file in enumerate(files):
    if filenum%10 ==0: print "Processed %s files"%filenum
    thisfile = in_path + file
    f = open(thisfile, 'rb')
    tags = {}
    tags = exifread.process_file(f)
    f.close()
    print file
    
#     for item in tags.items():
#         print item
    
    DateTime = str(tags.get('Image DateTime'))
#     digitised = tags['EXIF DateTimeDigitized']
#     print DateTime
    
    ymd,hms = DateTime.split(' ')
    y,mo,d = ymd.split(':')
    h,mi,s = hms.split(':')
    
    y = int(y)
    mo = int(mo)
    d = int(d)
    h = int(h)
    mi = int(mi)
    s = int(s)
    
#     print ymd
#     print hms
#     print y
#     print mo
#     print d
#     print h
#     print mi
#     print s
    t = (s) + (mi*60) + (h*60*60) + (d*60*60*24) + (d*60*60*24) + (mo*60*60*24*31) + (y*60*60*24*31*365)
    
    outfile.write(thisfile + '\t' + str(t) + '\n')
    outfile.flush()

