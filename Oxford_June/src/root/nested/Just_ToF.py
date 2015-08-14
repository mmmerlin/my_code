import os
import pylab as pl
from my_functions import *
from root_functions import *
from lsst.afw.display import ds9
from lsst.afw.display.ds9 import ds9Cmd


GLOBAL_OUT = []

out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'


in_path = '/mnt/hgfs/VMShared/Data/oxford/Day 4/Run 20/'


xmin, xmax, ymin, ymax,tmin,tmax=0,0,0,0,0,0


def MakeToFSpectrum_new():
    timecodes = GetTimecodes_AllFilesInDir(in_path, xmin, xmax, ymin, ymax, 0) #OCS
    print 'Total entries = %s' %len(timecodes)
     
    if exp_type == 'timepix':
        ax5.hist(timecodes, bins = 11811, range = [0,11810])
        ax5.set_title('ToF Spectrum - Full range')
        ax7.hist(timecodes, bins = (tmax-tmin) +1 , range = [tmin,tmax])
        print 'Finished ToF / Timepix'
#         pl.xlabel('ToF (timecodes)', horizontalalignment = 'right' )
#         pl.title('ToF Spectrum - ROI')
    elif exp_type =='pimms_to_timepix':
        ax6.hist(timecodes, bins = 11811, range = [0,11810])
        ax6.set_title('ToF Spectrum - Full range')
        ax8.hist(timecodes, bins = (tmax-tmin) +1 , range = [tmin,tmax])
        print 'Finished ToF / PImMS'



TOF_fig, ((ax5, ax6), (ax7, ax8)) = pl.subplots(2, 2, sharey=False)

day = 'day3'
run = 'run8'

# 
# exp_type = 'timepix'
# xmin = 10
# xmax = 245
# ymin = 10
# ymax = 245
# # tmin = 8060
# # tmax = 8160
# tmin = 6460
# tmax = 6520
# in_path = '/mnt/hgfs/VMShared/Data/oxford/june_2015/'
# in_path += day + '/'
# in_path += exp_type + '/'
# in_path += run + '/'
# 
# GLOBAL_OUT.append('Timepix parameters')
# GLOBAL_OUT.append('%s\t%s\t%s\t%s\t%s\t%s\n'%(xmin,xmax,ymin,ymax,tmin,tmax))
#                   
# PlotREMPI_new()
# MakeToFSpectrum_new()
# 
# 
# 
# exp_type = 'pimms_to_timepix'
# xmin = 0
# xmax = 245
# ymin = 0
# ymax = 245
# tmin = 1160
# tmax = 1320
# in_path = '/mnt/hgfs/VMShared/Data/oxford/june_2015/'
# in_path += day + '/'
# in_path += exp_type + '/'
# in_path += run + '/'
# 
# GLOBAL_OUT.append('Timepix parameters')
# GLOBAL_OUT.append('%s\t%s\t%s\t%s\t%s\t%s\n'%(xmin,xmax,ymin,ymax,tmin,tmax))
# 
# 
# # PlotREMPI_new()
# # MakeToFSpectrum_new()
# 
# REMPI_fig.set_size_inches(15,15)
# REMPI_fig.savefig(out_path + day + run + 'REMPI.png')
# TOF_fig.set_size_inches(15,15)
# TOF_fig.savefig(  out_path + day + run + 'ToF.png')
# 
# 
# outfile = open(out_path + day + run + 'data.txt', 'w')
# for line in GLOBAL_OUT: outfile.write(line + '\n')
# outfile.close()
# 
# print 'Finished combined analysis'
# exit()





xmin = 10
xmax = 245
ymin = 10
ymax = 245
tmin = 8060
tmax = 8160

ds9Cmd




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



if __name__ == '__main__':
    print "Oxford June 2015..."
    print in_path


#     MakeToFSpectrum()
#     print "Finished ToF Spectrum"
#     exit()
#     
    
    print '\n***End code***'







