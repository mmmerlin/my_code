from my_functions import *
import numpy as np
import pylab as pl
from scipy.interpolate import interp1d

path = '/mnt/hgfs/VMShared/output/TimepixCam_paper/sensitivity/QE.txt'
out_path = '/mnt/hgfs/VMShared/output/TimepixCam_paper/'


    
if __name__ == '__main__':


    x, nm_500, nm_50, LSST = np.loadtxt(path, delimiter='\t', skiprows=1, unpack = True)

    xmin = 260
    xmax = 1100
    
    fig = pl.figure(figsize=(14,10))


    pl.plot(x, nm_50,  'b-o', label="50nm passivation")

    pl.plot(x, nm_500,  'r-o', label="500nm passivation")
    
    
    pl.plot(x, LSST, 'kD', label="LSST CCDs")
    interp_LSST = interp1d(x, LSST, kind='cubic')
    t_new = np.linspace(min(x), max(x), len(x)*20)
    pl.plot(t_new,interp_LSST(t_new),'k-')








    pl.legend()
    pl.xlim([250,1125])
#     pl.ylim([0,1.1])
    pl.xlabel('Wavelength (nm)', horizontalalignment = 'right' )
    pl.ylabel('Quantum Efficiency', horizontalalignment = 'right' )

    pl.tight_layout()
    fig.savefig(out_path + 'sensitivity_2.pdf')
    pl.show()    
    
    
    exit()
    




    


    pl.show()











