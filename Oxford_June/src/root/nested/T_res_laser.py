import pylab as pl
from my_functions import *

GLOBAL_OUT = []

xmin = 10
xmax = 245
ymin = 10
ymax = 245

out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'


#= laser exp ==============================================================================
timepix_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day4/timepix/run2/'
pimms_path =   '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day4/timepix/run2/'
raw_offset     = 5282 #bigger moves left
centroid_offset_1 = 5280
centroid_offset_2 = 5280
timepix_max_offset = 5280 #bigger moves left
finetune_1 = 0
finetune_2 = -20



def MakeToFSpectrum():
    timepix_timecodes_raw = GetTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
    timepix_centroided_1 =  GetMaxClusterTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, checkerboard_phase = None, npix_min = 4)
    timepix_centroided_2 =  GetMaxClusterTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, checkerboard_phase = None, npix_min = 9)

    for i,code in enumerate(timepix_timecodes_raw):
        timepix_timecodes_raw[i] = (11810. - code) - raw_offset
        timepix_timecodes_raw[i] *= 20
        
    for i,code in enumerate(timepix_centroided_1):
        timepix_centroided_1[i] = (11810. - code) - centroid_offset_1
        timepix_centroided_1[i] *= 20
#         pimms_timecodes_raw[i] = (code - pimms_offset)*12.5

    for i,code in enumerate(timepix_centroided_2):
        timepix_centroided_2[i] = (11810. - code) - centroid_offset_2
        timepix_centroided_2[i] *= 20     
    
    timepix_nbins = 100
    
    fig = pl.figure(figsize=(14,10))
   
    n_raw, tp_bins, patches               = pl.hist(timepix_timecodes_raw, bins = timepix_nbins, range = [0,2000])
    n_centroided_1, pm_bins, patches      = pl.hist(timepix_centroided_1,  bins = timepix_nbins, range = [0,2000])
    n_centroided_2, tp_bins_max, patches  = pl.hist(timepix_centroided_2,  bins = timepix_nbins, range = [0,2000])

    pl.clf()
    tp_bins     = tp_bins[:-1] 
    pm_bins     = pm_bins[:-1]
    tp_bins_max = tp_bins_max[:-1] 
    
    NORMALISE = True

    if NORMALISE == True:
        pl.plot(tp_bins-finetune_1,     n_raw/max(n_raw),                   'k-.o', label="Timepix Raw")
        pl.plot(pm_bins,                n_centroided_1/max(n_centroided_1), 'b--o', label="4 pixel clusters")
        pl.plot(tp_bins_max-finetune_2, n_centroided_2/max(n_centroided_2), 'r-o',  label="9 pixel clusters")
    else:
        pl.plot(tp_bins-finetune_1,     n_raw,          'k-.o', label="Timepix Raw")
        pl.plot(pm_bins,                n_centroided_1, 'b--o', label="4 pixel clusters")
        pl.plot(tp_bins_max-finetune_2, n_centroided_2, 'r-o',  label="9 pixel clusters")
        
    print "Peak height raw = %s"%max(n_raw)
    print "Peak height 4pix = %s"%max(n_centroided_1)
    print "Peak height 9pix = %s"%max(n_centroided_2)
    
    pl.legend()
    pl.xlim([100,1100])
    pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )

    pl.tight_layout()
    fig.savefig(out_path + 'temp.png')
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
    















