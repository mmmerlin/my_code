import pylab as pl
from my_functions import *

GLOBAL_OUT = []


out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'
in_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/timepix/run1/'

# in_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/pimms_to_timepix/run2/'

# in_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day4/timepix/run6/'


xmin = 10
xmax = 245
ymin = 10
ymax = 245
tmin = 8060
tmax = 8160

# tmin = 0
# tmax = 4096



def MakeToFSpectrum():
    timecodes_raw =     GetTimecodes_AllFilesInDir(in_path, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
    timecodes_phase0 =  GetTimecodes_AllFilesInDir(in_path, xmin, xmax, ymin, ymax, 0, checkerboard_phase = 0)
    timecodes_phase1 =  GetTimecodes_AllFilesInDir(in_path, xmin, xmax, ymin, ymax, 0, checkerboard_phase = 1)
    print 'Total entries = %s' %len(timecodes_raw)
    
    nbins = tmax - tmin
    
#     make the histogram of the timecodes
    fig = pl.figure()
   
    n_raw, bins, patches =       pl.hist(timecodes_raw,    bins = nbins, range = [tmin,tmax])
    n_phase_0, dummy1, patches = pl.hist(timecodes_phase0, bins = nbins, range = [tmin,tmax])
    n_phase_1, dummy2, patches = pl.hist(timecodes_phase1, bins = nbins, range = [tmin,tmax])

    bins = bins[:-1]
 
    pl.clf()
 
    pl.plot(bins, n_raw, 'k--o')
    pl.plot(bins, n_phase_0, 'b--o')
    pl.plot(bins, n_phase_1, 'r-o')
    pl.show()
    exit()
 
    pl.xlim([tmin,tmax])
    pl.xlabel('ToF (timecodes)', horizontalalignment = 'right' )
    pl.title('ToF Spectrum')
    
    for bin, value in zip(bins, n_raw):
        print str(bin) + '\t' + str(value)
    exit()


    fig.savefig(out_path + 'ToF_raw.png')
    pl.show()


    
if __name__ == '__main__':
    print "Oxford June 2015..."
    print in_path


    
    MakeToFSpectrum()
    print "Finished ToF Spectrum"
    exit()
    
    print '\n***End code***'







