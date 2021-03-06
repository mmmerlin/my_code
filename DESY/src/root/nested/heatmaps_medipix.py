import pylab as pl
from my_functions import MakeCompositeImage_Timepix
from matplotlib.colors import LogNorm

# data_path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Xenon/Run11/'
data_path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Vacuum_gauge/'

out_path = '/mnt/hgfs/VMShared/output/DESY/2015_june/'

### all except perimeter pixels
ymin = 1
ymax = 254
xmin = 1
xmax = 254
    
if __name__ == '__main__':

    array = MakeCompositeImage_Timepix(data_path, xmin, xmax, ymin, ymax, 0, 99999, return_raw_array=True)
    
#     size = 80
#     xmin = 47
#     ymin = 70

    size = 125
    xmin = 25
    ymin = 50

    fig = pl.figure(figsize=(14,10))
    ax = pl.axes()
    
    temp = array.flatten()
    temp.sort()
    zmax = temp[-20]
    print 'zmax = %s'%zmax
#     zmax = 500

#     imgplot = pl.imshow(array, interpolation = 'none')
    imgplot = pl.imshow(array, interpolation = 'none', norm=LogNorm(vmin=1,vmax=zmax))
#     imgplot = pl.imshow(array, interpolation = 'none', norm=LogNorm(vmin=1,vmax=2997))
    pl.colorbar()
    pl.tight_layout()
    
    
#     ax.set_xlim(xmin,xmin + size)
#     ax.set_ylim(ymin,ymin + size)
    
#     imgplot.set_clim(0,zmax)



    fig.savefig(out_path + '/medipix/vacuum_gauge_log.png')

    
    pl.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    exit()
    
