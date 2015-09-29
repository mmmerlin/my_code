import pylab as pl
from my_functions import *

GLOBAL_OUT = []

xmin = 10
xmax = 245
ymin = 10
ymax = 245

out_path = '/mnt/hgfs/VMShared/output/TimepixCam_paper/'


#===============================================================================
# timepix_path_1 = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/4-9-15/temp/'
timepix_path_1 = '/mnt/hgfs/VMShared/Data/new_sensors/bnl/4-9-15/100V_good_trigger/'
timepix_offset     = 9100 #bigger moves left
tp_finetune = 0
tp_max_finetune = -70
#===============================================================================
NORMALISE = False






x, y = [],[]
x2, y2 = [],[]


def MakeToFSpectrum():
    global x,y,x2,y2
    
    timepix_timecodes_raw = GetTimecodes_AllFilesInDir(timepix_path_1, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
#     pimms_timecodes_raw =   GetTimecodes_AllFilesInDir(pimms_path, 0, 999, 0, 999, 0, checkerboard_phase = None)
    timepix_timecodes_max = GetMaxClusterTimecodes_AllFilesInDir(timepix_path_1, xmin, xmax, ymin, ymax, checkerboard_phase = None, npix_min = 9)

    for i,code in enumerate(timepix_timecodes_raw):
        timepix_timecodes_raw[i] = (11810. - code) - timepix_offset
        timepix_timecodes_raw[i] *= 20
        
    for i,code in enumerate(timepix_timecodes_max):
        timepix_timecodes_max[i] = (11810. - code) - timepix_offset
        timepix_timecodes_max[i] *= 20     
    
    timepix_nbins = 250
    
    fig = pl.figure(figsize=(14,10))
   
    n_tp, tp_bins, patches          = pl.hist(timepix_timecodes_raw, bins = timepix_nbins, range = [0,timepix_nbins*20])
    n_tp_max, tp_bins_max, patches  = pl.hist(timepix_timecodes_max, bins = timepix_nbins, range = [0,timepix_nbins*20])


    pl.clf()
    tp_bins     = tp_bins[:-1] 
    tp_bins_max = tp_bins_max[:-1] 
    
    
    if NORMALISE:
        pl.plot(tp_bins-tp_finetune,        n_tp/max(n_tp),         'k-.o', label="Timepix Raw")
        pl.plot(tp_bins_max-tp_max_finetune,n_tp_max/max(n_tp_max), 'r-o',  label="Timepix Clustered")
    else:
        pl.plot(tp_bins-tp_finetune,        n_tp,         'k-.o', label="Timepix Raw")
        pl.plot(tp_bins_max-tp_max_finetune,n_tp_max, 'r-o',  label="Timepix Clustered")

    
    x.extend(tp_bins_max-tp_max_finetune)
    y.extend(n_tp_max/max(n_tp_max))
    
    x2.extend(tp_bins-tp_finetune)
    y2.extend(n_tp/max(n_tp))
    
    
    pl.legend()
    pl.xlim([0,timepix_nbins*20])
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
    
    hist1 = ListVsList_fit(x, y,   out_path + 'max_9.png', fitmin = 2900, fitmax = 3300)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
    hist1 = ListVsList_fit(x2, y2, out_path + 'raw.png',   fitmin = 2900, fitmax = 3300)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
    
    print 'max value = %s'%max(y)
    
    
    exit()
    















