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
    ax = fig.add_subplot(1,1,1)

    ax.plot(x, nm_50,  'b-D', label="50nm passivation")

    ax.plot(x, nm_500,  'r-s', label="500nm passivation")
    
    
    ax.plot(x, LSST, 'ko', label="LSST CCDs")
    interp_LSST = interp1d(x, LSST, kind='cubic')
    t_new = np.linspace(min(x), max(x), len(x)*20)
    pl.plot(t_new,interp_LSST(t_new),'k-')



    font = {'family' : 'serif',
            'color'  : 'darkred',
            'weight' : 'normal',
            'size'   : 106,
            }




    ax.legend()
    pl.xlim([300,1135])
#     pl.ylim([0,1.1])

    pl.xlabel('Wavelength (nm)', horizontalalignment = 'right' , fontsize=25)
    pl.ylabel('Quantum Efficiency', horizontalalignment = 'right' , fontsize=25)

    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)

    pl.tight_layout()
    fig.savefig(out_path + 'sensitivity_2_new.pdf')
    pl.show()    
    
    
    exit()
    




    


    pl.show()











