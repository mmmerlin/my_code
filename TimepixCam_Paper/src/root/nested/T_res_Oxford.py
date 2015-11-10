import pylab as pl
from my_functions import *

GLOBAL_OUT = []

xmin = 10
xmax = 245
ymin = 10
ymax = 245

out_path = '/mnt/hgfs/VMShared/output/TimepixCam_paper/Oxford/'


# #===============================================================================




timepix_path_1 = '/mnt/hgfs/VMShared/Data/oxford/Day 3/First ions/'
# timepix_path_1 = '/mnt/hgfs/VMShared/Data/oxford/Day 3/temp/'
timepix_offset  = 4300 #bigger moves left
tp_max_finetune = 0#-20
tp_max2_finetune = 0#-60




NORMALISE = True
# #===============================================================================


x, y = [],[]
x2, y2 = [],[]
x3, y3 = [],[]


def MakeToFSpectrum():
    global x,y,x2,y2
    
    timepix_timecodes_raw = GetTimecodes_AllFilesInDir(timepix_path_1, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
    timepix_timecodes_max = GetMaxClusterTimecodes_AllFilesInDir(timepix_path_1, xmin, xmax, ymin, ymax, checkerboard_phase = None, npix_min = 1)
    timepix_timecodes_max2 = GetMaxClusterTimecodes_AllFilesInDir(timepix_path_1, xmin, xmax, ymin, ymax, checkerboard_phase = None, npix_min = 4)

    for i,code in enumerate(timepix_timecodes_raw):
        timepix_timecodes_raw[i] = (11810. - code) - timepix_offset
        timepix_timecodes_raw[i] *= 20
        
    for i,code in enumerate(timepix_timecodes_max):
        timepix_timecodes_max[i] = (11810. - code) - timepix_offset
        timepix_timecodes_max[i] *= 20  
    
    for i,code in enumerate(timepix_timecodes_max2):
        timepix_timecodes_max2[i] = (11810. - code) - timepix_offset
        timepix_timecodes_max2[i] *= 20     
    
    timepix_nbins = 50
    
    fig = pl.figure(figsize=(14,10))
   
    n_tp, tp_bins, patches            = pl.hist(timepix_timecodes_raw,  bins = timepix_nbins, range = [0,timepix_nbins*20])
    n_tp_max, tp_bins_max, patches    = pl.hist(timepix_timecodes_max,  bins = timepix_nbins, range = [0,timepix_nbins*20])
    n_tp_max2, tp_bins_max2, patches  = pl.hist(timepix_timecodes_max2, bins = timepix_nbins, range = [0,timepix_nbins*20])


    pl.clf()
    tp_bins     = tp_bins[:-1] 
    tp_bins_max = tp_bins_max[:-1] 
    tp_bins_max2 = tp_bins_max2[:-1] 
    
    
    if NORMALISE:
        pl.plot(tp_bins,        n_tp/max(n_tp),                         'k-o', label="Raw timecodes", markersize=8)
        pl.plot(tp_bins_max-tp_max_finetune,n_tp_max/max(n_tp_max),     'b-.D',  label="Clustered, min", markersize=8)
        pl.plot(tp_bins_max2-tp_max2_finetune,n_tp_max2/max(n_tp_max2), 'r--s', label="Clustered, 4 pix", markersize=8)
    else:
        pl.plot(tp_bins,        n_tp,                   'k-o', label="Raw timecodes", markersize=8)
        pl.plot(tp_bins_max-tp_max_finetune,n_tp_max,   'b-.D',  label="Clustered, min", markersize=8)
        pl.plot(tp_bins_max2-tp_max2_finetune,n_tp_max2,'r--s', label="Clustered, 4 pix", markersize=8)

    
    x.extend(tp_bins_max-tp_max_finetune)
    y.extend(n_tp_max/max(n_tp_max))

    x2.extend(tp_bins_max2-tp_max2_finetune)
    y2.extend(n_tp_max2/max(n_tp_max2))
    
    x3.extend(tp_bins)
    y3.extend(n_tp/max(n_tp))
    
    
    pl.legend()
    pl.xlim([0,timepix_nbins*20])
    pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )
    pl.ylabel('Normalised Counts', horizontalalignment = 'right' )

    pl.tight_layout()
    fig.savefig(out_path + '1st_peak_4pix.pdf')
    pl.show()
    
    print "finished"
 

def ShowRawToF():
    raw_codes = GetTimecodes_AllFilesInDir(timepix_path_1, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
    offset = 0
    tmin = 0
    tmax = 11810

    fig = pl.figure(figsize=(14,10))
    n_codes, bins, patches = pl.hist([11810-i for i in raw_codes], bins = 11810, range = [0,11810])
#     pl.yscale('log', nonposy='clip')


    for i,code in enumerate(raw_codes):
        raw_codes[i] = (11810. - code) - offset
        raw_codes[i] *= 20

    fig = pl.figure(figsize=(14,10))
    n_codes, bins, patches = pl.hist(raw_codes, bins = 1000, range = [0,40000])
    
#     n_codes, bins, patches = pl.hist(raw_codes, bins = tmax-tmin, range = [tmin,tmax])

#     pl.clf()
#     n_codes = n_codes[:-1] 
#     pl.plot(bins, n_codes, 'k-.o', label="Timecodes")
    
    pl.tight_layout()
    
    pl.show()
        
    
if __name__ == '__main__':
    print "Oxford June 2015..."

#     print timepix_path_1
#     OpenTimepixInDS9(timepix_path_1 + '1_0003.txt', binary=True)
#     exit()

#     ShowRawToF()
#     exit()
    
    MakeToFSpectrum()
    print "Finished ToF Spectrum"
    
    
    from root_functions import ListVsList_fit
    
#     hist1 = ListVsList_fit(x, y,   out_path + 'tres_1.png', fitmin = 100+20, fitmax = 225+40)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
#     hist1 = ListVsList_fit(x2, y2, out_path + 'tres_4.png', fitmin = 100, fitmax = 200)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
#     hist1 = ListVsList_fit(x3, y3, out_path + 'raw.png',    fitmin = 100+20, fitmax = 225+60)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
    
    
    
    exit()
    















