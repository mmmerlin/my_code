import pylab as pl
import numpy as np
from my_functions import *

out_path = ''

# xmin = 1
# xmax = 255
# ymin = 1
# ymax = 255

### run 10 bounds
# ymin = 44
# ymax = 129
# xmin = 76
# xmax = 150

### ultra-tight box for run 10
ymin = 72
ymax = 110
xmin = 97
xmax = 126

data_path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Xenon/Run11/'

# data_path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Vacuum_gauge/'

mcp_filename = '/mnt/hgfs/VMShared/Data/DESY/2015_june/MCPdata/2015-07-02-4_55am-Xenon-run10_Ch1.awd'

out_path = '/mnt/hgfs/VMShared/output/DESY/2015_june/'



def PlotMCPCurrent():
    timecodes = GetTimecodes_AllFilesInDir(data_path, xmin, xmax, ymin, ymax, 162.2, translate_to_us=True)
#     y,binEdges=np.histogram(timecodes,bins=11811)
#     bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
#     
    data = np.loadtxt(mcp_filename, skiprows = 6)
#     print 'Total entries = %s' %len(data)
    
    mcp_times = np.linspace(0, len(data)*5e-10, len(data), endpoint = True)


    mcp_t_offset_us = 2.25-.125+.08 #larger = more left

    for i, value in enumerate(mcp_times):
        mcp_times[i] = (value *1e6) - mcp_t_offset_us
        data[i] = (data[i]-0.02455)*1000


#     f, (ax1) = pl.subplots(1, 1, sharey=False)
#     ax1.plot(mcp_times, data, '-')
#     ax1.plot(bincenters,y,'-')
#     pl.xlim([-1,5])
    
    
#     tmin = -1
#     tmax = 7

    tmin = -1
    tmax = 15
    
#     fig = pl.figure(figsize=(14,10))
#     ax  = fig.add_subplot(111)
#     myHist = ax.hist(timecodes, 50*(tmax-tmin)+1, normed=False, log = True, range = [tmin,tmax])
#     ax.plot(mcp_times, data, '-')
#     pl.xlim([tmin,tmax])
#     pl.xlabel('Time (us)', horizontalalignment = 'right' )
#     pl.title('MCP current (a.u.)')
# #     f.savefig(out_path + run + 'MCP.png')
#     pl.show()
    
    
    fig, ax1 = pl.subplots(figsize=(14,10))
    ax1.hist(timecodes, 50*(tmax-tmin)+1, normed=False, log = True, range = [tmin,tmax], color = 'b')
    ax1.set_xlabel('Time ($\mu s$)')
    ax1.set_ylabel('Timepix (# pixels)', color='b')
    ax1.set_ylim([1,1e9])
#     ax1.set_ylim([1e2,1e8])
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

     
    ax2 = ax1.twinx()
    ax2.plot(mcp_times, data, 'r-')
    ax2.set_ylabel('MCP (mV)', color='r')
    ax2.set_ylim([0,70])
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
        
    pl.xlim([tmin,tmax])
    
    pl.tight_layout()
    fig.savefig(out_path + 'High_flux_tight_cut.png')
    
    pl.show()
    
    
if __name__ == '__main__':

#     OpenTimepixInDS9(data_path + '1_0010.txt')
#     exit()



    PlotMCPCurrent()
