from my_functions import *
import numpy as np
import pylab as pl
from scipy.interpolate import interp1d

path = '/mnt/hgfs/VMShared/output/TimepixCam_paper/sensitivity/ratios.txt'
out_path = '/mnt/hgfs/VMShared/output/TimepixCam_paper/'


    
if __name__ == '__main__':


    x, p47, e404 = np.loadtxt(path, delimiter='\t', skiprows=1, unpack = True)

    xmin = 0
    xmax = 1000
    
    fig = pl.figure(figsize=(14,10))
    ax = fig.add_subplot(1,1,1)


    ax.plot(x, p47,  'ro', label="P47")
    
    interp_p47_1 = interp1d(x, p47, kind='cubic')
    t_new = np.linspace(min(x), 500, len(x)*20)
    ax.plot(t_new,interp_p47_1(t_new),'r-')
    
#     interp_p47_2 = interp1d(x, p47, kind='linear')
#     t_new = np.linspace(500, 1000, len(x)*20)
#     pl.plot(t_new,interp_p47_2(t_new),'r-')


    ax.plot(x, e404, 'bD', label="E404")
    interp_e404 = interp1d(x, e404, kind='quadratic')
    t_new = np.linspace(min(x), max(x), len(x)*20)
    ax.plot(t_new,interp_e404(t_new),'b--')

    ax.legend()
    pl.xlim([-50,1100])
#     pl.ylim([0,1.1])
    pl.xlabel('Passivation Depth (nm)', horizontalalignment = 'right', fontsize=25)
    pl.ylabel('Normalised Sensitivity', horizontalalignment = 'right', fontsize=25)

    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)

    pl.tight_layout()
    fig.savefig(out_path + 'sensitivity_1_new.pdf')
    pl.show()    
    
    
    exit()
    




    


    pl.show()











