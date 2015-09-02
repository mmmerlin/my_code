import os
import pylab as pl
from my_functions import *
from root_functions import ListVsList

GLOBAL_OUT = []

exp_type = ''
day = ''
run = ''

out_path = '/mnt/hgfs/VMShared/output/2015_june/temp/'
in_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/timepix/run1/'

x, y = [],[]

xmin, xmax, ymin, ymax,tmin,tmax=10,245,10,245,0,15000
    

def AnalyseTimepix(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, raw, npix):
    from root_functions import ListVsList_fit
   
    global x,y
    retval = ''
    print in_path
    offset = 3650
#     offset = 3540
    
    if raw:
        timepix_timecodes_max = GetTimecodes_AllFilesInDir(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, checkerboard_phase = None)
    else:
        timepix_timecodes_max = GetMaxClusterTimecodes_AllFilesInDir(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, checkerboard_phase = None, npix_min=npix)

    for i,code in enumerate(timepix_timecodes_max):
        timepix_timecodes_max[i] = (11810. - code)-offset
        timepix_timecodes_max[i] *= 20     
    
    timepix_bins = 100
    
    fig = pl.figure(figsize=(14,10))
   
    n_tp_max, tp_bins_max, patches  = pl.hist(timepix_timecodes_max, bins = timepix_bins, range = [0,2000])

    pl.clf()
    tp_bins_max = tp_bins_max[:-1] 
    
    pl.plot(tp_bins_max,n_tp_max, 'r-o',  label="Timepix Clustered")
    
    x = []
    y = []
    x.extend(tp_bins_max)
    y.extend(n_tp_max)
    
    sigma, hist1 = ListVsList_fit(x, y, out_path + 'temp.png', fitmin = 50, fitmax = 500)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
    
    nclusters = len(timepix_timecodes_max)
    peak_height = max(n_tp_max)
    print "peak_height = %s"%peak_height
    print "n_clusters = %s"%nclusters
    
    retval += str(nclusters) + '\t' + str(peak_height) + '\t' + str(sigma)
    
    pl.legend()
#     pl.xlim([0,1100])
#     pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )

    pl.tight_layout()
#     fig.savefig(out_path + 'temp.png')
    pl.show(block = False)
  
    return retval

def AnalysePImMS(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, raw):
    from root_functions import ListVsList_fit
    global x,y
    
    print in_path
    offset = 1200
    retval = ''
    
    if raw:
        mask_array = None
        n_masked_pix = 0
    else:
        mask_pixels = GeneratePixelMaskListFromFileset(in_path, noise_threshold = 0.05, xmin = 0, xmax = 255, ymin = 0, ymax = 255, file_limit = 1e6)
        print mask_pixels
        print '---'
        n_masked_pix = len(mask_pixels[0])
        mask_array = MakeMaskArray(mask_pixels)
#         ViewMaskInDs9(mask_array)
    
    pimms_timecodes_raw = GetTimecodes_AllFilesInDir(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, checkerboard_phase = None, noise_mask=mask_array)

    for i,code in enumerate(pimms_timecodes_raw):
        pimms_timecodes_raw[i] = (code - offset)*12.5     
    
    pimms_nbins = 160
    
    fig = pl.figure(figsize=(14,10))
   
    n_tp_max, tp_bins_max, patches  = pl.hist(pimms_timecodes_raw, bins = pimms_nbins, range = [0,2000])

    pl.clf()
    tp_bins_max = tp_bins_max[:-1] 
    
    pl.plot(tp_bins_max,n_tp_max, 'r-o',  label="Timepix Clustered")
    
    x = []
    y = []
    x.extend(tp_bins_max)
    y.extend(n_tp_max)
    
    sigma, hist1 = ListVsList_fit(x, y, out_path + 'temp.png', fitmin = 50, fitmax = 500)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
    
    
    nclusters = len(pimms_timecodes_raw)
    peak_height = max(n_tp_max)
    print "peak_height = %s"%peak_height
    print "n_clusters = %s"%nclusters
    
    retval += str(nclusters) + '\t' + str(peak_height) + '\t' + str(sigma) + '\t' + str(n_masked_pix)
    
    pl.legend()
#     pl.xlim([0,1100])
#     pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )

    pl.tight_layout()
#     fig.savefig(out_path + 'temp.png')
    pl.show(block = True)
    
    
    return retval
    
    
if __name__ == '__main__':


    out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'

    day = 'day4'
    run = 'run1'
    
    in_path = '/mnt/hgfs/VMShared/Data/oxford/june_2015/'
#     exp_type = 'timepix'
    exp_type = 'pimms_to_timepix'
    in_path += day + '/'
    in_path += exp_type + '/'
    in_path += run + '/'
    
    tp_xmin = 10
    tp_xmax = 245
    tp_ymin = 10
    tp_ymax = 245
    
#     raw = True
#     npix = 1
#     line = AnalyseTimepix(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, raw, npix)
#     GLOBAL_OUT.append(line)
#     raw = False
#     npix = 1
#     line = AnalyseTimepix(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, raw, npix)
#     GLOBAL_OUT.append(line)
#     npix = 4
#     line = AnalyseTimepix(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, raw, npix)
#     GLOBAL_OUT.append(line)
#     npix = 9
#     line = AnalyseTimepix(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, raw, npix)
#     GLOBAL_OUT.append(line)
#  
#     for line in GLOBAL_OUT:
#         print line
#  
#     exit()

    raw = True
    line = AnalysePImMS(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, raw)
    GLOBAL_OUT.append(line)
    raw = False
    line = AnalysePImMS(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, raw)
    GLOBAL_OUT.append(line)
    
    
    for line in GLOBAL_OUT:
        print line
    exit()
 
    print 'max value = %s'%max(y)
    
    
    print 'done'
    exit()

    pimms_xmin = 0
    pimms_xmax = 80
    pimms_ymin = 0
    pimms_ymax = 80
    pimms_tmin = 0
    pimms_tmax = 5000
     
     
     
     


#     MakeToFSpectrum()
#     print "Finished ToF Spectrum"
#     exit()
#     
    
    print '\n***End code***'







