import pylab as pl
import numpy as np
from my_functions import *

tmin,tmax, xmin, xmax, ymin, ymax = 0,0,0,0,0,0
out_path = ''


    
def PlotMCPCurrent():
    data = np.loadtxt( '/mnt/hgfs/VMShared/Data/DESY/2015_june/MCPdata/2015-07-02-4_55am-Xenon-run10_Ch1.awd', skiprows = 6)
    data2 = np.loadtxt('/mnt/hgfs/VMShared/Data/DESY/2015_june/MCPdata/2015-07-02-5_42am-Xenon-run11_Ch1.awd', skiprows = 6)
    print 'Total entries = %s' %len(data)
    
    mcp_times = np.linspace(0, len(data)*5e-10, len(data), endpoint = True)

    mcp_t_offset_us=0

    for i, value in enumerate(mcp_times):
        mcp_times[i] = (value*1e6) - mcp_t_offset_us
        data[i]  = ((data[i] -0.02455)*1000000)+15000
        data2[i] = ((data2[i]-0.02455)*1000000)-10000

    first_point = 0
    last_point = first_point + 12000

#     times = mcp_times[first_point:last_point]
#     data = data[first_point:last_point]
#     data2 = data2[first_point:last_point]
     
    f, (ax1) = pl.subplots(1, 1, sharey=False)
    ax1.plot(mcp_times, data, '-')
    ax1.plot(mcp_times, data2, '-')

    pl.xlim([0,10])

    
#     pl.xlim([tmin,tmax])
    pl.xlabel('Time (us)', horizontalalignment = 'right' )
    pl.title('MCP current (a.u.)')

    f.savefig(out_path + run + 'MCP.png')
    pl.show(block =False)
    
    
def MakeToFSpectrum_single():
    timecodes = GetTimecodes_AllFilesInDir(in_path, 10, 245, 10, 245, 160, translate_to_us=True) #OCS
    print 'Total entries = %s' %len(timecodes)
    
    f, (ax1) = pl.subplots(1, 1, sharey=False)
    print 'Declared figure'
    ax1.hist(timecodes, bins = 301, range = [0,6], log=True)
    print 'Made histogram'
    pl.xlim([0,6])
    pl.xlabel('ToF (timecodes)', horizontalalignment = 'right' )
    pl.title('ToF Spectrum - ROI')

    f.savefig(out_path + run + 'ToF_ROI.png')
    pl.show()
    
if __name__ == '__main__':

    path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Xenon/'
    run = 'Run11'
    in_path = path + run + '/'
    
    out_path = '/mnt/hgfs/VMShared/output/DESY/2015_june/'
    
    PlotMCPCurrent()
    MakeToFSpectrum_single()
    