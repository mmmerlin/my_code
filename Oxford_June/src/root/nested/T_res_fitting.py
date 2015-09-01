import pylab as pl
from my_functions import *

GLOBAL_OUT = []

xmin = 10
xmax = 245
ymin = 10
ymax = 245

out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'

#===============================================================================
timepix_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/timepix/run2/'
pimms_path =   '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/pimms_to_timepix/run2/'
timepix_offset     = 3651 #bigger moves left
timepix_max_offset = 3651 #bigger moves left
pimms_offset       = 1200 #smaller moves left
tp_finetune = 2.5
tp_max_finetune = -17.5
#===============================================================================

# #===============================================================================
# timepix_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/timepix/run2/'
# pimms_path =   '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day3/pimms_to_timepix/run2/'
# #= 4 pix min ===========================================================================
# # timepix_offset     = 3650 #bigger moves left
# # timepix_max_offset = 3651 #bigger moves left
# # pimms_offset       = 1188 #smaller moves left
# # tp_finetune = 5
# # tp_max_finetune = -55
# #===============================================================================
# timepix_offset     = 3650 #bigger moves left
# timepix_max_offset = 3650 #bigger moves left
# pimms_offset       = 1188 #smaller moves left
# tp_finetune = 5
# tp_max_finetune = -55


x, y = [],[]
x2, y2 = [],[]


def MakeToFSpectrum():
    global x,y,x2,y2
    
    timepix_timecodes_max = GetMaxClusterTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, checkerboard_phase = None, npix_min =9)
#     timepix_timecodes_max =  GetTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, checkerboard_phase = None)

#     for i,code in enumerate(pimms_timecodes_raw):
#         pimms_timecodes_raw[i] = (code - pimms_offset)*12.5

    for i,code in enumerate(timepix_timecodes_max):
        timepix_timecodes_max[i] = (11810. - code) - timepix_max_offset
        timepix_timecodes_max[i] *= 20     
    
    timepix_nbins = 100
    pimms_nbins = 160
    
    fig = pl.figure(figsize=(14,10))
   
#     n_pm, pm_bins, patches          = pl.hist(pimms_timecodes_raw,   bins = pimms_nbins,   range = [0,2000])
    n_tp_max, tp_bins_max, patches  = pl.hist(timepix_timecodes_max, bins = timepix_nbins, range = [0,2000])

    pl.clf()
#     pm_bins     = pm_bins[:-1]
    tp_bins_max = tp_bins_max[:-1] 
    
    pl.plot(tp_bins_max-tp_max_finetune,n_tp_max/max(n_tp_max), 'r-o',  label="Timepix Clustered")
#     pl.plot(pm_bins,                    n_pm/max(n_pm),         'b--o', label="PImMS")
    
    x.extend(tp_bins_max-tp_max_finetune)
    y.extend(n_tp_max/max(n_tp_max))
    
#     x2.extend(pm_bins)
#     y2.extend(n_pm/max(n_pm))
    
    pl.legend()
    pl.xlim([0,1100])
    pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )

    pl.tight_layout()
    fig.savefig(out_path + 'temp.png')
    pl.show(block = False)
    
    print "finished"
 
    
if __name__ == '__main__':
    print "Oxford June 2015..."


    MakeToFSpectrum()
    print "Finished ToF Spectrum"
    
    
    
    from root_functions import ListVsList_fit
    
    hist1 = ListVsList_fit(x, y, out_path + 'tp_fit.png', fitmin = 50, fitmax = 450)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
#     hist1 = ListVsList_fit(x2, y2, out_path + 'pimms.png', fitmin = 50, fitmax = 450)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
    
    print 'max value = %s'%max(y)
    
    
    exit()
    















