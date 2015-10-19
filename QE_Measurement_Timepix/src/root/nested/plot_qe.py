from __builtin__ import str
import pylab as pl
import numpy as np
from matplotlib import gridspec 


if __name__ == '__main__':

    print "running"
    
    filename = '/mnt/hgfs/VMShared/output/QE_Timepix/Sensors/calibrated_diode_1/calib_diode_1_clipped.txt'
#     filename = '/mnt/hgfs/VMShared/output/QE_Timepix/Sensors/calibrated_diode_1/calib_diode_1_raw.txt'
    wavelengths, qe, resp, respcal, residuals, rel_errors = np.loadtxt(filename, skiprows = 1, delimiter = '\t', unpack = True)
    



    f = pl.figure(figsize=(12,9))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
    
    
    ax0 = pl.subplot(gs[0])
    pl.tight_layout()
    
    pl.subplots_adjust(hspace=0.0001)
    
    ax0.plot(wavelengths,resp,'or',wavelengths,respcal,'ob')
    ax0.get_xaxis().set_visible(False)

#     ax0.get_xaxis().set_ticklabels([])
        
    pl.xlim(300,1150)
    
    ax1 = pl.subplot(gs[1], sharex=ax0)
    ax1.plot(wavelengths,rel_errors,'ok')
    pl.xlim(300,1150)
    
    ax1.axhline(0, linestyle='--', color='k')
    ax1.set_yticks([-20,0,20], minor=False)
#     ax1.yaxis.grid(True, which='major')
    
#     yticklabels = ax1.get_yticklabels()
#     new_ticks = [label for i, label in enumerate(yticklabels) if i%2==0]
    
    
    
#     ax1.set_yticklabels(my_list)
    
    
#     print type(yticklabels)
#     print type(new_ticks)
#     exit()
    
    pl.ylim(-40,40)


    
    pl.show()







#     f = pl.figure(figsize=(12,9))
#     
#     
#     ax1 = pl.subplot(211)
#     pl.tight_layout()
#     
#     pl.subplots_adjust(hspace=0.0001)
#     
#     ax1.plot(wavelengths,resp,'or',wavelengths,respcal,'ob')
# #     pl.yticks(np.arange(-0.9, 1.0, 0.4))
#     pl.xlim(300,1150)
#     
#     ax2 = pl.subplot(212, sharex=ax1)
#     ax2.plot(wavelengths,rel_errors,'ok')
# #     pl.yticks(np.arange(0.1, 1.0,  0.2))
#     pl.xlim(300,1150)
# #     pl.ylim(0,1)
#     
# #     xticklabels = ax1.get_xticklabels()+ax2.get_xticklabels()
# #     pl.setp(xticklabels, visible=False)
#     pl.show()




    pl.show()
    
    
    
    print '\n***End code***'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
