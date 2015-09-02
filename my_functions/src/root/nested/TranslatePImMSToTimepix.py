from my_functions import TranslatePImMSToTimepix
import os

conversion_in  = '/mnt/hgfs/VMShared/Data/oxford/june_2015/Day3/pimms/run1/'
conversion_out = '/mnt/hgfs/VMShared/Data/oxford/june_2015/Day3/pimms_to_timepix/run1/'


for i, filename in enumerate(os.listdir(conversion_in)):
    print filename
    TranslatePImMSToTimepix(conversion_in + filename, i, conversion_out)
print 'finished translating %s'%conversion_in
exit()