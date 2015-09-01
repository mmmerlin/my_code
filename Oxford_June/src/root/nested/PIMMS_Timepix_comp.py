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


def PlotREMPI_new():
    max_loops = 16
    loop_length = 999
    box_size = 1
    
    files = os.listdir(in_path)

    wavelength = range(999)
    intensity = np.zeros(999)
    total_codes = 0
    run_intensity = np.zeros(max_loops)

#     image_array = []
#     for i in range(999):
#         image = MakeCompositeImage_Timepix(in_path + files[0], xmin, xmax, ymin, ymax, t_min = tmin, t_max=tmax, return_raw_array=False)
#         image_array.append(image)
#         image_array[i] -= image
        

    for i,filename in enumerate(files):
        if str(filename).find('.DS')!=-1:continue
        run_num = float(str.split(filename,'_')[0])
        shot_num = float(str.split(str.split(filename,'_')[1],'.')[0])-1
        if shot_num >= 999: continue
        
        codes = GetRawTimecodes_SingleFile(in_path+filename, xmin, xmax, ymin, ymax, tmin, tmax, 0)
        ncodes = len(codes[0:])
        intensity[shot_num] += ncodes
        total_codes += ncodes
        run_intensity[run_num] += ncodes
        
        if i>=(max_loops*loop_length): break
        
    print 'Total codes = %s\n'%total_codes
    for i in range(max_loops):
        GLOBAL_OUT.append('run %s = %s'%(i,run_intensity[i]))
        print 'run %s =\t%s'%(i,run_intensity[i])
        
    wavelength = wavelength[0:999-box_size+1]
    intensity = BoxcarAverage1DArray(intensity,box_size)
    assert len(wavelength)==len(intensity)
    
    if exp_type == 'timepix':
        ax1.plot(wavelength,intensity)
        ax1.set_xlabel('Wavelength (a.u./nm)')
        ax3.errorbar(range(max_loops), run_intensity, run_intensity**0.5, fmt='o')
        ax3.set_ylim([0, max(run_intensity)*1.1])
        ax3.set_xlabel('Relative REMPI intensity (pixs/frame)')
        
        print 'Finished REMPI / Timepix'
    elif exp_type =='pimms_to_timepix':
        ax2.plot(wavelength,intensity)
        ax2.set_xlabel('Wavelength (a.u./nm)')
        ax4.errorbar(range(max_loops), run_intensity, run_intensity**0.5, fmt='o')
        ax4.set_ylim([0, max(run_intensity)*1.1])
        ax4.set_xlabel('Relative REMPI intensity (pixs/frame)')
       
        print 'Finished REMPI / PImMS'
        
    
    tot_int = 0.
    n_points = 0.
    for i in range(len(run_intensity)):
        if run_intensity[i] <> 0:
            tot_int += run_intensity[i]
            n_points += 1.
    av_int = tot_int / n_points
    
    
    print 'average intensity = %.2f'%(av_int)
    GLOBAL_OUT.append('average intensity = %.2f'%(av_int))
    
    
def MakeToFSpectrum():
    print in_path
    exit()
    timecodes = GetTimecodes_AllFilesInDir(in_path, xmin, xmax, ymin, ymax, 0) #OCS
    print 'Total entries = %s' %len(timecodes)
     
    #make the histogram of the timecodes
    fig2 = pl.figure()
    pl.hist(timecodes, bins = 11811, range = [tmin,tmax])
    pl.xlim([tmin,tmax])
    pl.xlabel('ToF (timecodes)', horizontalalignment = 'right' )
    pl.title('ToF Spectrum')

    fig2.savefig(out_path + day + run + exp_type + 'ToF.png')
    pl.show()


def PlotREMPI():
    max_loops = 16
    loop_length = 999
    box_size = 10
    
    files = os.listdir(in_path)

    wavelength = range(999)
    intensity = np.zeros(999)
    total_codes = 0
    run_intensity = np.zeros(max_loops)

    for i,filename in enumerate(files):
        run_num = float(str.split(filename,'_')[0])
        shot_num = float(str.split(str.split(filename,'_')[1],'.')[0])-1
        if shot_num >= 999: continue

        codes = GetRawTimecodes_SingleFile(in_path+filename, xmin, xmax, ymin, ymax, tmin, tmax, 0)
        ncodes = len(codes[0:])
        intensity[shot_num] += ncodes
        total_codes += ncodes
        run_intensity[run_num] += ncodes
        
        if i>=(max_loops*loop_length): break
        
    print 'Total codes = %s\n'%total_codes
    for i in range(max_loops):
        print 'run %s = %s'%(i,run_intensity[i])
        
    wavelength = wavelength[0:999-box_size+1]
    intensity = BoxcarAverage1DArray(intensity,box_size)
    assert len(wavelength)==len(intensity)
    
    plotname = out_path + day + run + exp_type + 'REMPI.png'
    ListVsList(wavelength, intensity, plotname, plot_opt='AC')
    exit()
    
    fig2 = pl.figure()
    pl.plot(wavelength,intensity)
    pl.xlabel('Wavelength (a.u./nm)', horizontalalignment = 'right' )
    fig2.savefig(out_path+plotname+'.png')
#     pl.show()
    
    fig3, ax = pl.subplots(nrows=1, ncols=1, sharex=True)
    ax.errorbar(range(max_loops), run_intensity, run_intensity**0.5, fmt='o')
    
    tot_int = 0.
    n_points = 0.
    for i in range(len(run_intensity)):
        if run_intensity[i] <> 0:
            tot_int += run_intensity[i]
            n_points += 1.
    av_int = tot_int / n_points
    
    print 'average intensity = %.2f'%(av_int)
    pl.show()
    


def AnalyseTimepix(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, tp_tmin, tp_tmax):
    global x,y
    
    print in_path
    offset = 3650
    npix_min = 9
    
    timepix_timecodes_max = GetMaxClusterTimecodes_AllFilesInDir(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, checkerboard_phase = None, npix_min=npix_min)
#     timepix_timecodes_max = GetTimecodes_AllFilesInDir(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, checkerboard_phase = None)

    for i,code in enumerate(timepix_timecodes_max):
        timepix_timecodes_max[i] = (11810. - code)-offset
        timepix_timecodes_max[i] *= 20     
    
    timepix_bins = 100
    
    fig = pl.figure(figsize=(14,10))
   
    n_tp_max, tp_bins_max, patches  = pl.hist(timepix_timecodes_max, bins = timepix_bins, range = [0,2000])

    pl.clf()
    tp_bins_max = tp_bins_max[:-1] 
    
    pl.plot(tp_bins_max,n_tp_max, 'r-o',  label="Timepix Clustered")
    
    x.extend(tp_bins_max)
    y.extend(n_tp_max)
    
    nclusters = len(timepix_timecodes_max)
    peak_height = max(n_tp_max)
    print "peak_height = %s"%peak_height
    print "n_clusters = %s"%nclusters
    
    pl.legend()
#     pl.xlim([0,1100])
#     pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )

    pl.tight_layout()
    fig.savefig(out_path + 'temp.png')
    pl.show(block = True)
  
      

def AnalysePImMS(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, tp_tmin, tp_tmax):
    global x,y
    
    print in_path
    offset = 1200
    
    mask_pixels = GeneratePixelMaskListFromFileset(in_path, noise_threshold = 0.05, xmin = 0, xmax = 255, ymin = 0, ymax = 255, file_limit = 1e6)
    print mask_pixels
    print '---'
    print len(mask_pixels[0])
    mask_array = MakeMaskArray(mask_pixels)
    ViewMaskInDs9(mask_array)
#     exit()
#     mask_array = None
    
    pimms_timecodes_raw = GetTimecodes_AllFilesInDir(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, checkerboard_phase = None, noise_mask=mask_array)

    for i,code in enumerate(pimms_timecodes_raw):
        pimms_timecodes_raw[i] = (code - offset)*12.5     
    
    pimms_nbins = 160
    
    fig = pl.figure(figsize=(14,10))
   
    n_tp_max, tp_bins_max, patches  = pl.hist(pimms_timecodes_raw, bins = pimms_nbins, range = [0,2000])

    pl.clf()
    tp_bins_max = tp_bins_max[:-1] 
    
    pl.plot(tp_bins_max,n_tp_max, 'r-o',  label="Timepix Clustered")
    
    x.extend(tp_bins_max)
    y.extend(n_tp_max)
    
    nclusters = len(pimms_timecodes_raw)
    peak_height = max(n_tp_max)
    print "peak_height = %s"%peak_height
    print "n_clusters = %s"%nclusters
    
    pl.legend()
#     pl.xlim([0,1100])
#     pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )

    pl.tight_layout()
    fig.savefig(out_path + 'temp.png')
    pl.show(block = True)
    
if __name__ == '__main__':

    #===============================================================================
    timepix_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/timepix/run2/'
    pimms_path =   '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/pimms_to_timepix/run2/'
    timepix_offset     = 3651 #bigger moves left
    timepix_max_offset = 3651 #bigger moves left
    pimms_offset       = 1200 #smaller moves left
    tp_finetune = 2.5
    tp_max_finetune = -17.5
    #===============================================================================

    out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'

    day = 'day3'
    run = 'run3'
    
    in_path = '/mnt/hgfs/VMShared/Data/oxford/june_2015/'
    exp_type = 'timepix'
#     exp_type = 'pimms_to_timepix'
    in_path += day + '/'
    in_path += exp_type + '/'
    in_path += run + '/'
    
    tp_xmin = 10
    tp_xmax = 245
    tp_ymin = 10
    tp_ymax = 245
    tp_tmin = 8060
    tp_tmax = 8160
    
#     MakeToFSpectrum()
#     exit()
    
    AnalyseTimepix(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, tp_tmin, tp_tmax)
#     AnalysePImMS(in_path, tp_xmin, tp_xmax, tp_ymin, tp_ymax, tp_tmin, tp_tmax)
    
    from root_functions import ListVsList_fit
    
    hist1 = ListVsList_fit(x, y, out_path + 'temp.png', fitmin = 150, fitmax = 700)#, xmin, xmax, xtitle, ytitle, setlogy, ymin, ymax, marker_color, set_grid, marker_style, marker_size, plot_opt)
    
    print 'max value = %s'%max(y)
    
    
    print 'done'
    exit()

    pimms_xmin = 0
    pimms_xmax = 80
    pimms_ymin = 0
    pimms_ymax = 80
    pimms_tmin = 0
    pimms_tmax = 5000
     
     
     
     
     
     
    PlotREMPI()
    exit()


#     MakeToFSpectrum()
#     print "Finished ToF Spectrum"
#     exit()
#     
    
    print '\n***End code***'







