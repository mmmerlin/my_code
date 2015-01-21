import os
from os.path import expanduser
from mpl_toolkits.mplot3d import Axes3D

import pylab as pl
from numpy import dtype

from my_functions import *

from matplotlib.pyplot import pause

xmin = 0
xmax = 230
ymin = 0
ymax = 230

tmin = 28
tmax = 28.6 

nfiles_3d = 200

def Make3DScatter():
    xs, ys, ts = GetXYTarray_AllFilesInDir(input_path, xmin, xmax, ymin, ymax, -186.6, tmin, tmax, nfiles_3d)
    print 'Number of X,Y,T points = %s'%len(xs)
    
    fig = pl.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(xs, ys, ts)
    pl.xlim([0,200])
    pl.ylim([0,200])
    pl.show()
    
def MakeToFSpectrum():
#         for file in os.listdir(input_path):
    timecodes = GetTimecodes_AllFilesInDir(in_stem + path, xmin, xmax, ymin, ymax, -151.1)
    print 'Total entries = %s' %len(timecodes)
     
    tmin = 6000
    tmax = 7500  
    bins = (tmax-tmin) -1 #*50
     
    #make the histogram of the timecodes
    fig2 = pl.figure()
#     pl.subplot(2,1,1)
     
    pl.hist(timecodes, bins = bins, range = [tmin,tmax])
#     pl.ylim([0,500])
    pl.xlim([tmin,tmax])
    pl.xlabel('Timecodes', horizontalalignment = 'right' )
    pl.title('Timepix ToF Spectrum')

#################################### 
    #################################### plot PMT data
#################################### 
#     pl.subplot(2,1,2)
# 
#     pmt_datafile = '/mnt/hgfs/VMShared/Data/oxford/Day 3/PMT/TEK0004.csv'
#     xs, ys = ReadTektronixWaveform(pmt_datafile)
#     pl.plot(xs*1e6 + 10, -1.*ys)
# 
# #     pmt_datafile = '/mnt/hgfs/VMShared/Data/oxford/PMTdata/005.txt'
# #     xs, ys = ReadBNL_PMTWaveform(pmt_datafile)
# #     pl.plot(xs*1e6 -84.3, -1.*ys)
#     
# #     pl.ylim([0,20])
#     pl.xlim([tmin,tmax])
#     pl.title('PMT Spectrum')
    
    fig2.savefig(out_stem + path + 'Full_ToF.png')
    pl.xlim([7100,7170])
    fig2.savefig(out_stem + path + 'ToF_ROI.png')
    pl.xlim([6900,7170])
    fig2.savefig(out_stem + path + 'ToF_ROI_More.png')
    
    pl.show()
    
    
      
  

def ShowCompositeImageMedipix(path):
    
    image = MakeCompositeImage_Medipix(path, xmin, xmax, ymin, ymax, maxfiles=99999)
    
    import lsst.afw.display.ds9 as ds9
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'

    ds9.mtv(image)
    
if __name__ == '__main__':
    print "Running mass spec analysis"
    from root_functions import *
    from TrackViewer import TrackToFile_ROOT_2D_3D

    in_stem = '/mnt/hgfs/VMShared/Data/oxford/'
    path = 'Day 4/map 1/'
    out_stem = '/mnt/hgfs/VMShared/Oxford_output/'
    
#     Make3DScatter()
#     TimepixDirToPImMMSDatafile('/mnt/hgfs/VMShared/Data/oxford/PMT comp/', '/mnt/hgfs/VMShared/Data/oxford/pimms.txt')
    
#     MakeToFSpectrum()
#     print "Finished ToF Spectrum"
#     exit()
    
#     image = MakeCompositeImage_Timepix(in_stem + path, maxfiles = 2000, t_min=6960, t_max = 6980)
#     TrackToFile_ROOT_2D_3D(image.getArray(), out_stem + path + 'temp.png', plot_opt='surf1', log_z = False, force_aspect= True, fitline = None)
#     import lsst.afw.display.ds9 as ds9
#     try:
#         ds9.initDS9(False)
#     except ds9.Ds9Error:
#         print 'DS9 launch bug error thrown away (probably)'
#   
#     ds9.mtv(image)

    
    slicelist = []
####### CO+ range
    for i in range(7140,7160):
        slicelist.append([i])
        slicelist.append([i,i+1])
        slicelist.append([i,i+2])
    slicelist.append([7135,7139])#5 timecodes wide
    slicelist.append([7140,7144])#5 timecodes wide
    slicelist.append([7145,7149])#5 timecodes wide
    slicelist.append([7150,7154])#5 timecodes wide
    slicelist.append([7155,7159])#5 timecodes wide
    slicelist.append([7160,7164])#5 timecodes wide
    slicelist.append([7135,7166])# full ROI and a bit more

####### S+ range
#     for i in range(7110,7136):
#         slicelist.append([i])
#     slicelist.append([7110,7114])#5 timecodes wide
#     slicelist.append([7115,7119])#5 timecodes wide
#     slicelist.append([7120,7124])#5 timecodes wide
#     slicelist.append([7125,7129])#5 timecodes wide
#     slicelist.append([7130,7134])#5 timecodes wide
#     slicelist.append([7122,7133, '*'])#5 2nd peak integral S+
#     slicelist.append([7114,7123, '*'])# 1st peak integral S+
    
    
    
#     MakeTimeSlices(in_stem + path, slicelist, out_stem + path)


    image = MakeCompositeImage_Timepix(in_stem + path, maxfiles = 9999, t_min=0, t_max = 11810)
#     TrackToFile_ROOT_2D_3D(image.getArray(), out_stem + path + '1.png', plot_opt='surf1', log_z = False, force_aspect= True, fitline = None)

    import lsst.afw.display.ds9 as ds9
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'
  
    ds9.mtv(image)

    print '\n***End code***'







