import os
from os.path import expanduser
from mpl_toolkits.mplot3d import Axes3D
import pylab as pl
from numpy import dtype
from my_functions import *
from matplotlib.pyplot import pause
from root_functions import *
from TrackViewer import TrackToFile_ROOT_2D_3D




# exp_type = 'pimms'
exp_type = 'timepix'

day = 'day3'
run = 'run8'



if exp_type == 'timepix':
    xmin = 10
    xmax = 245
    ymin = 10
    ymax = 245
#     tmin = 8060
#     tmax = 8160
    tmin = 9100
    tmax = 9200
    
elif exp_type == 'pimms':
    xmin = 0
    xmax = 245
    ymin = 0
    ymax = 245
    tmin = 1201
    tmax = 1275
else:
    print 'INVALID EXP_TYPE'
    exit()


in_path = '/mnt/hgfs/VMShared/Data/oxford/june_2015/'
in_path += day + '/'
in_path += exp_type + '/'
in_path += run + '/'


out_path = '/mnt/hgfs/VMShared/output/oxford_june_2015/'


conversion_in  = '/mnt/hgfs/VMShared/Data/oxford/june_2015/Day3/pimms/run8/'
conversion_out = '/mnt/hgfs/VMShared/Data/oxford/june_2015/Day3/pimms_to_timepix/run8/'


def PlotREMPI():
    max_loops = 16
    loop_length = 999
    box_size = 1
    
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
#     ListVsList(wavelength, intensity, out_path+plotname+'.png', plot_opt='AC')
    
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
    
    
    

def MakeToFSpectrum():
    timecodes = GetTimecodes_AllFilesInDir(in_path, xmin, xmax, ymin, ymax, 0) #OCS
    print 'Total entries = %s' %len(timecodes)
     
    #make the histogram of the timecodes
#     fig2 = pl.figure()
#     pl.hist(timecodes, bins = bins, range = [tmin,tmax])
#     pl.xlim([tmin,tmax])
#     pl.xlabel('ToF (timecodes)', horizontalalignment = 'right' )
#     pl.title('ToF Spectrum')

    f, (ax1, ax2) = pl.subplots(1, 2, sharey=False)
    ax1.hist(timecodes, bins = 11811, range = [0,11810])
    ax1.set_title('ToF Spectrum - Full range')
    ax2.hist(timecodes, bins = (tmax-tmin) +1 , range = [tmin,tmax])
    pl.xlim([tmin,tmax])
    pl.xlabel('ToF (timecodes)', horizontalalignment = 'right' )
    pl.title('ToF Spectrum - ROI')

    f.savefig(out_path + day + run + exp_type + 'ToF.png')
    pl.show()

def ShowCompositeImageMedipix(path):
    
    image = MakeCompositeImage_Medipix(path, xmin, xmax, ymin, ymax, maxfiles=99999)
    
    import lsst.afw.display.ds9 as ds9
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'

    ds9.mtv(image)
    
def ShowImage(image):
    
    import lsst.afw.display.ds9 as ds9
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'

    ds9.mtv(image)
    
if __name__ == '__main__':
    print "Oxford June 2015..."
    print in_path


    for i, filename in enumerate(os.listdir(conversion_in)):
        TranslatePImMSToTimepix(conversion_in + filename, i, conversion_out)
    print 'finished translating %s'%conversion_in
    exit()


    image = MakeCompositeImage_Timepix(in_path, maxfiles = 5000, t_min=tmin, t_max = tmax)
    ShowImage(image)
#     TrackToFile_ROOT_2D_3D(image.getArray(), out_path + 'comp.png', plot_opt='colz', log_z = False, force_aspect= True, fitline = None, zmax = 500)
    exit()
     
     
#     ShowCompositeImageMedipix(in_path)
#     exit()
    
#     in_path = in_path + '../pimms_to_timepix/'
    
#     PlotREMPI()
#     exit()


#     MakeToFSpectrum()
#     print "Finished ToF Spectrum"
#     exit()
#     
    
    print '\n***End code***'







