import os
from os.path import expanduser
from mpl_toolkits.mplot3d import Axes3D

import pylab as pl
from numpy import dtype

from my_functions import *
from matplotlib.pyplot import pause

Make3DScatter = True
MakeToFSpectrum = True
AnalyseThresholdScan = False

input_path = '/mnt/hgfs/VMShared/Data/chem_14.12.14/after lunch/c1_s2_01_thr400/'


if __name__ == '__main__':
    print "Running mass spec analysis"


     
    #===========================================================================
    # 3D Scattergram
    #===========================================================================    
    if Make3DScatter:
        xs, ys, ts = GetXYTarray_AllFilesInDir(input_path, 1, 254, 1, 254, 0, 0, 250,10)
        print 'Number of X,Y,T points = %s'%len(xs)
        
        mask = []
        mask.append((2,3))
        mask.append((12,13))
        
        for i in range(len(xs)):
            print 'a'
            if mask.index((xs[i],ys[i])) == -1:
                xs[i],ys[i],ts[i] = -1,-1,-1
        
        fig = pl.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, ts)
        pl.show()


    #===========================================================================
    # Histograms vs. PMT Spectra 
    #===========================================================================
    if MakeToFSpectrum:
#         for file in os.listdir(input_path):
        timecodes = GetTimecodes_AllFilesInDir(input_path, 3, 252, 3, 252, 2)
        print 'Total entries = %s' %len(timecodes)
        
        #make the histogram of the timecodes
        fig2 = pl.figure()
        pl.subplot(2,1,1)
        pl.hist(timecodes, bins = 601, range = [75,150])
        pl.title('Oxygen - Timepix')
     
        #plot PMT data
#         pmt_datafile = ''
#         data = pl.loadtxt(pmt_datafile)
#         pl.subplot(2,1,2)
#         pl.plot(data[:,0], data[:,1])
#         pl.title('Oxygen - PMT')

        
        pl.show()


    #===========================================================================
    # Compositing the phosphor image
    #===========================================================================    
    if False:
        phosphor_map_path = '/mnt/hgfs/MShared/Data/Chem_09-06-14/Phosphor map data/'
        
        image = MakeCompositeImage_Medipix(phosphor_map_path, 2, 252, 2, 252, maxfiles=99999)
        
        import lsst.afw.display.ds9 as ds9
        try:
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)'
    
        ds9.mtv(image)
    
    #===========================================================================
    # Timecodes per frame as a function of threshold value
    #===========================================================================
    if AnalyseThresholdScan:
        import string
        from scipy.stats import norm
        import matplotlib as mlab
        threshold_path = 'mnt/hgfs/VMShared/Data/oxford/threshold_scan/'
        
        dirs = os.listdir(threshold_path)
        
        pl.figure()
        
        plotnum = 1
        for dirname in dirs:
            threshvalue = string.split(dirname, '_')[-1]
#                if threshvalue!='320': continue
    
            histdata = []
    
            files = os.listdir(threshold_path + dirname)
            for filename in files:
                histdata.append(len(GetTimecodes_SingleFile(threshold_path + dirname + '/' + filename, 8, 247, 8, 247)))
            
#                (mu, sigma) = norm.fit(histdata)
#                n, bins, patches = pl.hist(histdata, bins = 50, range = [0,250], facecolor='green', alpha=0.75)
#                y = norm.pdf(bins, mu, sigma)
#                l = pl.plot(bins, y, 'r--', linewidth=2)


            pl.subplot(2,5,plotnum)
            pl.title('Theshold = ' + str(threshvalue))
            pl.hist(histdata, bins = 25, range = [0,250])
            plotnum +=1

    
        
        pl.tight_layout()
        pl.show()


        
     

    print '\n***End code***'







