import os
from os.path import expanduser
from mpl_toolkits.mplot3d import Axes3D

import pylab as pl
from numpy import dtype

from my_functions import *
from matplotlib.pyplot import pause


if __name__ == '__main__':
    print "Running mass spec analysis"

    home_dir = expanduser("~")
    input_path = '/mnt/hgfs/VMShared/Data/chem_14.12.14/'

     
    #===========================================================================
    # 3D Scattergram
    #===========================================================================    
    if False:
        xs, ys, ts = GetXYTarray_AllFilesInDir(input_path, 25, 252, 3, 252, 3, 3, 30)
        print 'Number of X,Y,T points = %s'%len(xs)
        
        fig = pl.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, ts)
        pl.show()


    #===========================================================================
    # Histograms vs. PMT Spectra 
    #===========================================================================
    if False:
        timecodes = GetTimecodes_AllFilesInDir(input_path, 3, 252, 3, 252, 2)
        print 'Total entries = %s' %len(timecodes)
        
        #make the histogram of the timecodes
        fig2 = pl.figure()
        pl.subplot(2,1,1)
        pl.hist(timecodes, bins = 601, range = [0,40])
        pl.title('Oxygen - Timepix')
     
        #plot PMT data
        data = pl.loadtxt(home_dir + '/Desktop/DMStack VM Shared/Data/Chem_09-06-14/oxygen_pmt.txt')
        pl.subplot(2,1,2)
        pl.plot(data[:,0], data[:,1])
        pl.title('Oxygen - PMT')
    #    pl.show()


    #===========================================================================
    # Compositing the phosphor image
    #===========================================================================    
    if False:
        phosphor_map_path = home_dir + '/Desktop/DMStack VM Shared/Data/Chem_09-06-14/Phosphor map data/'
        
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
    if True:
            import string
            from scipy.stats import norm
            import matplotlib as mlab
            threshold_path = home_dir + '/Desktop/DMStack VM Shared/Data/Chem_09-06-14/threshold/'
            
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







