import numpy as np
import os


filenames, numbers, dummy = np.loadtxt('/mnt/hgfs/VMShared/temp/ordered.txt', delimiter='\t', dtype = str, unpack = True)

# print filenames
# print numbers

for i in range(len(filenames)):
    print i
    
    oldname = filenames[i]
    newname = '/mnt/hgfs/VMShared/India_suction/' + numbers[i] + '.jpg'
    
#     print oldname
#     print newname
#     exit()
    
    os.rename(oldname, newname) 
    
print "Finished!"
