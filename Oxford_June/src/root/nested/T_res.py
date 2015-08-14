import pylab as pl
from my_functions import *

GLOBAL_OUT = []

xmin = 10
xmax = 245
ymin = 10
ymax = 245

out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'

#===============================================================================
# timepix_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/timepix/run2/'
# pimms_path =   '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/pimms_to_timepix/run2/'
# timepix_offset     = 3651 #bigger moves left
# timepix_max_offset = 3651 #bigger moves left
# pimms_offset       = 1200 #smaller moves left
# tp_finetune = 2.5
# tp_max_finetune = -17.5
#===============================================================================

# #===============================================================================
timepix_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/timepix/run2/'
pimms_path =   '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/pimms_to_timepix/run2/'
# #= 4 pix min ===========================================================================
# # timepix_offset     = 3650 #bigger moves left
# # timepix_max_offset = 3651 #bigger moves left
# # pimms_offset       = 1188 #smaller moves left
# # tp_finetune = 5
# # tp_max_finetune = -55
# #===============================================================================
timepix_offset     = 3650 #bigger moves left
timepix_max_offset = 3650 #bigger moves left
pimms_offset       = 1188 #smaller moves left
tp_finetune = 5
tp_max_finetune = -55



def MakeToFSpectrum():
    timepix_timecodes_raw = GetTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
    pimms_timecodes_raw =   GetTimecodes_AllFilesInDir(pimms_path, 0, 999, 0, 999, 0, checkerboard_phase = None)
    timepix_timecodes_max = GetMaxClusterTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, checkerboard_phase = None, npix_min = 9)

    for i,code in enumerate(timepix_timecodes_raw):
        timepix_timecodes_raw[i] = (11810. - code) - timepix_offset
        timepix_timecodes_raw[i] *= 20
        
    for i,code in enumerate(pimms_timecodes_raw):
        pimms_timecodes_raw[i] = (code - pimms_offset)*12.5

    for i,code in enumerate(timepix_timecodes_max):
        timepix_timecodes_max[i] = (11810. - code) - timepix_max_offset
        timepix_timecodes_max[i] *= 20     
    
    timepix_nbins = 100
    pimms_nbins = 160
    
    fig = pl.figure(figsize=(14,10))
   
    n_tp, tp_bins, patches          = pl.hist(timepix_timecodes_raw, bins = timepix_nbins, range = [0,2000])
    n_pm, pm_bins, patches          = pl.hist(pimms_timecodes_raw,   bins = pimms_nbins,   range = [0,2000])
    n_tp_max, tp_bins_max, patches  = pl.hist(timepix_timecodes_max, bins = timepix_nbins, range = [0,2000])

    pl.clf()
    tp_bins     = tp_bins[:-1] 
    pm_bins     = pm_bins[:-1]
    tp_bins_max = tp_bins_max[:-1] 
    
    pl.plot(tp_bins-tp_finetune,        n_tp/max(n_tp),         'k-.o', label="Timepix Raw")
    pl.plot(tp_bins_max-tp_max_finetune,n_tp_max/max(n_tp_max), 'r-o',  label="Timepix Clustered")
    pl.plot(pm_bins,                    n_pm/max(n_pm),         'b--o', label="PImMS")
    
    pl.legend()
    pl.xlim([100,1100])
    pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )

    pl.tight_layout()
    fig.savefig(out_path + 'T_res_day1.png')
    pl.show()
    
    print "finished"
 

def ShowRawToF():
    raw_codes = GetTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
    offset = 5280#3700
    tmin = 0
    tmax = 11810

    for i,code in enumerate(raw_codes):
        raw_codes[i] = (11810. - code) - offset
        raw_codes[i] *= 20
        
    fig = pl.figure(figsize=(14,10))
    n_codes, bins, patches = pl.hist(raw_codes, bins = 100, range = [0,2000])
#     n_codes, bins, patches = pl.hist(raw_codes, bins = tmax-tmin, range = [tmin,tmax])

#     pl.clf()
#     n_codes = n_codes[:-1] 
#     pl.plot(bins, n_codes, 'k-.o', label="Timecodes")
    
    pl.tight_layout()
    pl.show()
        
    
if __name__ == '__main__':
    print "Oxford June 2015..."

#     ShowRawToF()
#     exit()
    
    MakeToFSpectrum()
    print "Finished ToF Spectrum"
    exit()
    















