import pylab as pl
from my_functions import MakeCompositeImage_Timepix, MakeCompositeImage_PImMS
from matplotlib.colors import LogNorm 
import numpy as np
from copy import copy
import matplotlib.cm as cm 
# import pylab.colormaps as cm

PIMMS = True

# data_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/timepix/run2/'
data_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day1/pimms_to_timepix/run2/'

out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'


### all except perimeter pixels
ymin = 1
ymax = 254
xmin = 1
xmax = 254
    
if __name__ == '__main__':

#     cmaps = [m for m in pl.cm.datad if not m.endswith("_r")]
#     cmaps.sort()
#     print cmaps
#     exit()


    my_cmap = copy(cm.get_cmap('jet'))
    my_cmap.set_under('w', alpha=1) # make locations over vmax translucent red
    my_cmap.set_over('w', alpha=1)   # make location under vmin transparent white
    my_cmap.set_bad('g')             # make location with invalid data green


    if PIMMS:
        array = MakeCompositeImage_PImMS(data_path, xmin, xmax, ymin, ymax, 0, 999999, return_raw_array=True)
    else:
        array = MakeCompositeImage_Timepix(data_path, xmin, xmax, ymin, ymax, 0, 999999, return_raw_array=True)
        
#     size = 125
#     xmin = 25
#     ymin = 50

    fig = pl.figure(figsize=(14,10))
    ax = pl.axes()
    
    temp = array.flatten()
    temp.sort()
#     for element in temp[-200:-1]:
#         print element
    if PIMMS:
#         zmax = temp[-70]#good for linear
        zmax = temp[-50]
    else:
        zmax = temp[-20]
    print 'zmax = %s'%zmax
    
    
    zmax = 100
    
    cmap = my_cmap
    #gist_heat, gnuplot, hot
    
#     array[1,2] = np.nan
#     array[array == 0.0] = np.nan
    
    imgplot = pl.imshow(array, interpolation = 'none', vmin = 1, vmax = 15000, cmap=my_cmap)
#     imgplot = pl.imshow(array, interpolation = 'none')
#     imgplot = pl.imshow(array, interpolation = 'none', norm=LogNorm(vmin=1,vmax=zmax), cmap=cmap)
    pl.colorbar()
    pl.tight_layout()
    
    
#     ax.set_xlim(xmin,xmin + size)
#     ax.set_ylim(ymin + size, ymin)
    
#     imgplot.set_clim(0,zmax)


    fig.savefig(out_path + 'temp.png')
#     fig.savefig(out_path + cmap + '.png')

    
    pl.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    exit()
    
