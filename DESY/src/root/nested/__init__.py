import pylab as pl
import numpy as np
from my_functions import *

tmin,tmax, xmin, xmax, ymin, ymax = 0,0,0,0,0,0
out_path = ''

xmin = 10
xmax = 245
ymin = 10
ymax = 245
tmin = 7050
tmax = 7350

data_path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Xenon/Run11/'

mcp_filename = '/mnt/hgfs/VMShared/Data/DESY/2015_june/MCPdata/2015-07-02-4_55am-Xenon-run10_Ch1.awd'

# mcp_filename = '/mnt/hgfs/VMShared/Data/DESY/2015_june/MCPdata/2015-07-02-5_42am-Xenon-run11_Ch1.awd'


out_path = '/mnt/hgfs/VMShared/output/DESY/2015_june/'



def PlotMCPCurrent():
    timecodes = GetTimecodes_AllFilesInDir(data_path, 10, 245, 10, 245, 160, translate_to_us=True)
#     y,binEdges=np.histogram(timecodes,bins=11811)
#     bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
#     
    data = np.loadtxt(mcp_filename, skiprows = 6)
#     print 'Total entries = %s' %len(data)
    
    mcp_times = np.linspace(0, len(data)*5e-10, len(data), endpoint = True)


    mcp_t_offset_us = 4.45 #larger = more left

    for i, value in enumerate(mcp_times):
        mcp_times[i] = (value *1e6) - mcp_t_offset_us
        data[i] = 10.**(data[i]*100)
        data[i] = max(data[i],10)
        
#         data[i] = (data[i]-0.02455)*500000*25



#     f, (ax1) = pl.subplots(1, 1, sharey=False)
#     ax1.plot(mcp_times, data, '-')
#     ax1.plot(bincenters,y,'-')
#     pl.xlim([-1,5])
    
    tmin = -5
    tmax = 6
    
    fig = pl.figure(figsize=(14,10))
    ax  = fig.add_subplot(111)
    myHist = ax.hist(timecodes, 50*(tmax-tmin)+1, normed=False, log = True, range = [tmin,tmax])
    ax.plot(mcp_times, data, '-')

    pl.xlim([tmin,tmax])
#     pl.ylim([10,1e7])

    
    pl.xlabel('Time (us)', horizontalalignment = 'right' )
    pl.title('MCP current (a.u.)')

#     f.savefig(out_path + run + 'MCP.png')
    pl.show()
    
    
if __name__ == '__main__':

    
    PlotMCPCurrent()
