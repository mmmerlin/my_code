import pylab as pl
from my_functions import MakeCompositeImage_Timepix
from matplotlib.colors import LogNorm 
from matplotlib.patches import Rectangle


# data_path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Xenon/Run10/'
data_path = '/mnt/hgfs/VMShared/Data/DESY/2015_june/Vacuum_gauge/'

out_path = '/mnt/hgfs/VMShared/output/DESY/2015_june/'

### run 11 bounds
# ymin = 50
# ymax = 123
# xmin = 81
# xmax = 142

### run 10 bounds
# ymin = 44
# ymax = 129
# xmin = 76
# xmax = 150

### ultra-tight box for run 10
# ymin = 72
# ymax = 110
# xmin = 97
# xmax = 126

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
    
#     imgplot = pl.imshow(array, interpolation = 'none')
    imgplot = pl.imshow(array, interpolation = 'none', norm=LogNorm(vmin=1,vmax=1300))
#     imgplot = pl.imshow(array, interpolation = 'none', norm=LogNorm(vmin=1,vmax=2997))
    pl.colorbar()
    pl.tight_layout()
    
    
    
#     ### run 10 bounds
#     ymin = 44
#     ymax = 129
#     xmin = 76
#     xmax = 150
#  
#     currentAxis = pl.gca()
#     currentAxis.add_patch(Rectangle((ymin, xmin), ymax-ymin, xmax-xmin, edgecolor="red", fill = False, linewidth = 3, linestyle = 'solid'))
#  
#  
# ### ultra-tight box for run 10
#     ymin = 72
#     ymax = 110
#     xmin = 97
#     xmax = 126
#  
#     currentAxis = pl.gca()
#     currentAxis.add_patch(Rectangle((ymin, xmin), ymax-ymin, xmax-xmin, edgecolor="black", fill = False, linewidth = 3, linestyle = 'dashed'))


    
#     ax.set_xlim(xmin,xmin + size)
#     ax.set_ylim(ymin + size, ymin)
    
#     imgplot.set_clim(2500,3000)

    fig.savefig(out_path + 'vacuum_gauge.png')
#     fig.savefig(out_path + 'temp.png')

    
    pl.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    exit()
    
