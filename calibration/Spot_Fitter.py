from test.test_support import temp_cwd
def DrawFootprint(bbox,x,y,ellipse_string):
    ds9.dot("x",x,y) # draw cross at the centroid
    ds9.dot(ellipse_string,x,y) # draw cross at the centroid
    displayUtils.drawBBox(bbox, borderWidth=0.5) # borderWidth of 0.5 set bbox to fully encompass footprint and no more

import lsst.afw.display.ds9 as ds9
# from lsst.display.ds9 import ds9Cmd
# from lsst.display.ds9 import initDS9


import lsst.afw.image as afwImage
import lsst.afw.math as math
import lsst.afw.detection as afwDetect
import lsst.afw.display.utils as displayUtils
import lsst.afw.geom as afwGeom
import lsst.afw.geom.ellipses as ellipses
from time import sleep
import numpy as np
import os
import glob
import matplotlib
matplotlib.rcParams.update({'font.size':20})
import matplotlib.pyplot as plt

#---------

DISPLAY = True
#xy0 = [852,262]
#xy1 = [1167,561]


xy0 = [875,10]
xy1 = [1184,323]

# suffix = '.0001.short.M.fits.old'
# prefix = '/mnt/hgfs/VMShared/Data/lsst_calibration/1/t'
# files = [prefix + str(i) + suffix for i in range(1,6)]


path = '/mnt/hgfs/VMShared/Data/spots/1/'
outpath = os.path.join(path,'out')
if not os.path.isdir(outpath):
    os.mkdir(outpath)
plotpath = os.path.join(path,'plots')
if not os.path.isdir(plotpath):
    os.mkdir(plotpath)    
    
files = glob.glob(os.path.join(path,'test*.fits'))
#files = ['/mnt/hgfs/VMShared/Data/spots/test.fits']
#files = ['/mnt/hgfs/VMShared/Data/spots/

# print files

output = []
output.append('filename, x, y, a, b, theta, ixx, iyy, ixy, flux')

x_all = []
y_all = []
a_all = []
b_all = []
theta_all = []
ixx_all = []
iyy_all = []
ixy_all= []
flux_all = []

for i, filename in enumerate(files):
    if filename.find('.DS') != -1: continue #because OSX sucks
    print 'Processing %s'%filename
    
    image = afwImage.ImageF_readFits(filename)
    image = image
    
    #Define ROI
    image = image[xy0[0]:xy1[0], xy0[1]:xy1[1]]
    image.setXY0(afwGeom.Point2I(0,0))
        
#     xy0 = afwGeom.Point2I(1266,743)
#     size = 450
#     bbox = afwGeom.Box2I(xy0, afwGeom.Extent2I(size,size))
#     image = afwImage.ImageF(image,bbox,afwImage.LOCAL, True)
#     image.setXY0(afwGeom.Point2I(0,0))
    
    
    statFlags = math.MEAN | math.MEANCLIP | math.STDEV | math.STDEVCLIP
    control = math.StatisticsControl()
    
    imageStats  = math.makeStatistics(image, statFlags, control)
    mean        = imageStats.getResult(math.MEAN)[0]
    mean_clip   = imageStats.getResult(math.MEANCLIP)[0]
    stdev       = imageStats.getResult(math.STDEV)[0]
    stdevclip   = imageStats.getResult(math.STDEVCLIP)[0]
    
    print 'Mean = %s\nMean_clip = %s\nstddev = %s\nstddev_clip = %s\n'%(mean, mean_clip,stdev, stdevclip)
    
    image -= mean_clip
    
    thresholdValue = (50*stdevclip)
    npixMin = 2
    grow = 2
    isotropic = True
    
    maskedIm = afwImage.MaskedImageF(image)
    
    threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
    footPrintSet = afwDetect.FootprintSet(maskedIm, threshold, "DETECTED", npixMin)
    footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
  
    footPrints = footPrintSet.getFootprints()
    print "Found %s footprints"%len(footPrints)
 
 
    if DISPLAY:
#         initDS9()
        ds9.mtv(image)
 
 
    with ds9.Buffering():
        for footprint_num, footprint in enumerate(footPrints):
#             if footprint_num!=25: continue
            centroid_x, centroid_y = footprint.getCentroid()
            bbox = footprint.getBBox()
            

            
            quadshape = footprint.getShape()
            axeshape = ellipses.Axes(quadshape)
            
            a=axeshape.getA()
            b=axeshape.getB()
            theta=axeshape.getTheta()
            ixx=quadshape.getIxx()
            iyy=quadshape.getIyy()
            ixy=quadshape.getIxy()
            
            array = np.zeros(footprint.getArea(), dtype=image.getArray().dtype)
            afwDetect.flattenArray(footprint, image.getArray(), array, image.getXY0())
            flux = array.sum()
            norm_flux = flux / len(array)
            
            image_array = image.getArray()

            fp_xy0 = bbox.getBegin()
            fp_xy1 = bbox.getEnd()
            
            bl = fp_xy0[1]
            br = fp_xy1[1]
            tl = fp_xy0[0]
            tr = fp_xy1[0]

            small_sum = image_array[bl:br,tl:tr].sum()
            big_sum =   image_array[bl-1:br+1,tl-1:tr+1].sum()
            perimeter = float(2*(fp_xy1[0] - fp_xy0[0] + 2) + 2*(fp_xy1[1] - fp_xy0[1]+2) - 4)

            background_level = (big_sum-small_sum) / perimeter
            area = (br-bl) * (tr - tl)
            background_flux = background_level * area

            spot_flux = small_sum - background_flux
            
            out_line = "%s,%.5f,%.5f,%.5f,%5f,%.5f,%.5f,%.5f,%.5f,%.5f"%(filename,centroid_x,centroid_y,a,b,theta,ixx,iyy,ixy,spot_flux)
            output.append(out_line)
            
            ellipse_string = "@:"+str(4*ixx)+','+str(4*ixy)+','+str(4*iyy)
            
            if DISPLAY:
                DrawFootprint(bbox, centroid_x, centroid_y, ellipse_string)       
             
#     arg = 'saveimage jpeg ' + '/mnt/hgfs/VMShared/Data/lsst_calibration/' + str(i) + '_no_crop.jpeg' + ' 100'
#     ds9Cmd(arg)
    filenameFits = filename.split("/")[-1]
    filenameOutput = os.path.join(outpath,filenameFits.replace(".fits",".txt"))
    fid = open(filenameOutput,'w')
    for line in output:
        fid.write("%s\n"%line)
    fid.close()
     
    x,y,a,b,theta,ixx,iyy,ixy,spot_flux = np.loadtxt(filenameOutput,skiprows=1,usecols=[1,2,3,4,5,6,7,8,9],delimiter=',',unpack=True)
     
    x_all.append(np.median(x))
    y_all.append(np.median(y))
    a_all.append(np.median(a))
    b_all.append(np.median(b))
    ixx_all.append(np.median(ixx))
    iyy_all.append(np.median(iyy))
    ixy_all.append(np.median(ixy))
    flux_all.append(np.median(spot_flux)) 
     
    filenamePlot = os.path.join(plotpath,filenameFits.replace(".fits",".png"))
    plt.figure()
    plt.quiver(x,y,a,b,spot_flux)
    plt.colorbar()
    plt.xlim([0,350])
    plt.ylim([0,350])
    plt.savefig(filenamePlot)
    plt.close()

x_all = np.array(x_all)
y_all = np.array(y_all)
a_all = np.array(a_all)
b_all = np.array(b_all)
ixx_all = np.array(ixx_all)
iyy_all = np.array(iyy_all)
ixy_all = np.array(ixy_all)
flux_all = np.array(flux_all)

image_numbers = np.arange(len(files))
fwhms = np.sqrt(a_all**2 + b_all**2)     
    
xticks = []
for file in files:
    fileSplit = file.split("/")
    xticks.append(fileSplit[-1])    
    
flux_all = flux_all + np.random.randn(len(flux_all),)
fwhms = fwhms + np.random.randn(len(fwhms),)    
    
filenamePlot = os.path.join(plotpath,'scatter.pdf')
plt.figure(figsize=(24,18))
plt.scatter(image_numbers,flux_all,s=100,c=fwhms)
cbar = plt.colorbar()
cbar.ax.set_ylabel('FWHM')
plt.xlabel('Image number')
plt.ylabel('Flux')
plt.xticks(image_numbers,xticks,rotation=90)
plt.savefig(filenamePlot)
plt.close()    
    
    
    
    