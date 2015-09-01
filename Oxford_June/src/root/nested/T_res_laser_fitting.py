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

x, y = [],[]


def MakeToFSpectrum():
    global x,y
    timepix_centroided_1 =  GetMaxClusterTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, checkerboard_phase = None, npix_min = 9)
#     timepix_centroided_1 =  GetTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, checkerboard_phase = None)

    for i,code in enumerate(timepix_centroided_1):
        timepix_centroided_1[i] = (11810. - code) - centroid_offset_1
        timepix_centroided_1[i] *= 20
    
    timepix_nbins = 100
    
    fig = pl.figure(figsize=(14,10))
   
    n_centroided_1, pm_bins, patches      = pl.hist(timepix_centroided_1,  bins = timepix_nbins, range = [0,2000])

    pl.clf()
    pm_bins     = pm_bins[:-1]
    
    NORMALISE = True

    if NORMALISE == True:
        pl.plot(pm_bins,                n_centroided_1/max(n_centroided_1), 'b--o', label="4 pixel clusters")
        
    x.extend(pm_bins)
    y.extend(n_centroided_1)
    
    print "Peak height 4pix = %s"%max(n_centroided_1)
    
#     pl.legend()
#     pl.xlim([100,1100])
#     pl.ylim([0,1.1])
#     pl.xlabel('Time (ns)', horizontalalignment = 'right' )
# 
#     pl.tight_layout()
#     fig.savefig(out_path + 'temp.png')
#     pl.show()
    

    
if __name__ == '__main__':
    print "Oxford June 2015..."

#     ShowRawToF()
#     exit()
    
    MakeToFSpectrum()
    print "Finished ToF Spectrum"
    
    
    from root_functions import ListVsList_fit
    
    hist1 = ListVsList_fit(x, y, out_path + '9pix.png')#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
    
    print 'max value = %s'%max(y)
    
    
    exit()
    















