import pylab as pl
from my_functions import *

GLOBAL_OUT = []

xmin = 10
xmax = 245
ymin = 10
ymax = 245

out_path = '/mnt/hgfs/VMShared/output/TimepixCam_paper/'


# #===============================================================================

timepix_path_1 = '/mnt/hgfs/VMShared/Data/Chem_09-06-14/Butanone_2us_delay/'

 

def ShowRawToF():
    raw_codes = GetTimecodes_AllFilesInDir(timepix_path_1, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
    offset = 6940 #6850
    tmin = 0
    tmax = 11810

#     fig = pl.figure(figsize=(14,10))
#     n_codes, bins, patches = pl.hist([11810-i for i in raw_codes], bins = 11810, range = [0,11810])
#     pl.yscale('log', nonposy='clip')


    for i,code in enumerate(raw_codes):
        raw_codes[i] = (11810. - code) - offset
        raw_codes[i] *= 20./1000.


    nbins = 1300

    fig = pl.figure(figsize=(14,10))
    n_codes, bins, patches = pl.hist(raw_codes, bins = nbins, range = [0,nbins*20/1000])
#     pl.yscale('log', nonposy='clip')
    
    pl.xlim([0,nbins*20/1000])
    pl.xlabel('Time (um)', horizontalalignment = 'right' )
    pl.ylabel('Counts', horizontalalignment = 'right' )
    

    pl.tight_layout()
    fig.savefig(out_path + 'ToF.pdf')

    pl.show()
        
    
if __name__ == '__main__':
    print "Oxford June 2015..."

    ShowRawToF()
    exit()
    









