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
    timecodes = GetTimecodes_AllFilesInDir(input_path, xmin, xmax, ymin, ymax, -151.1)
    print 'Total entries = %s' %len(timecodes)
     
    tmin = 0
    tmax = 40    
    bins = (tmax-tmin)*50 -1
     
    #make the histogram of the timecodes
    fig2 = pl.figure()
    pl.subplot(2,1,1)
     
    pl.hist(timecodes, bins = bins, range = [tmin,tmax])
#     pl.ylim([0,75])
    pl.xlim([tmin,tmax])
    pl.title('Timepix Spectrum')
 

#################################### 
    #################################### plot PMT data
#################################### 
    pl.subplot(2,1,2)

#     pmt_datafile = '/mnt/hgfs/VMShared/Data/oxford/Day 3/PMT/TEK0000.csv'
#     xs, ys = ReadTektronixWaveform(pmt_datafile)
#     pl.plot(xs*1e6 + 10, -1.*ys)

    pmt_datafile = '/mnt/hgfs/VMShared/Data/oxford/PMTdata/005.txt'
    xs, ys = ReadBNL_PMTWaveform(pmt_datafile)
    pl.plot(xs*1e6 -84.3, -1.*ys)
    
#     pl.ylim([0,20])
    pl.xlim([tmin,tmax])
    pl.title('PMT Spectrum')
    
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


#     input_path = '/mnt/hgfs/VMShared/Data/oxford/Big run 1/'
#     input_path = '/mnt/hgfs/VMShared/Data/oxford/PMT Comp/'
#     input_path = '/mnt/hgfs/VMShared/Data/oxford/Day 2/Run 1/'
    input_path = '/mnt/hgfs/VMShared/Data/oxford/Day 3/First ions/'

#     Make3DScatter()
    
    MakeToFSpectrum()
    exit()
#     TimepixDirToPImMMSDatafile('/mnt/hgfs/VMShared/Data/oxford/PMT comp/', '/mnt/hgfs/VMShared/Data/oxford/pimms.txt')

    from TrackViewer import TrackToFile_ROOT_2D_3D
    image = MakeCompositeImage_Timepix(input_path, maxfiles = 2000, t_min=20, t_max = 21)
    
    TrackToFile_ROOT_2D_3D(image.getArray(), '/mnt/hgfs/VMShared/temp/comp.png', log_z = False, force_aspect= True, fitline = None)

    import lsst.afw.display.ds9 as ds9
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'

    ds9.mtv(image)

    print '\n***End code***'







