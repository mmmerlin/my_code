#from scipy import *
#from scipy import optimize
#
#
#from pylab import *
#from mpl_toolkits.mplot3d import Axes3D
#
#import lsst.afw.table       as afwTable
#import lsst.afw.image       as afwImg
#import lsst.afw.detection   as afwDetect
#import lsst.afw.display.ds9 as ds9
#
#
#from os.path import expanduser
#from misc import TimepixToExposure
#
##import rootpy.ROOT as ROOT
#
#import re
#import lsst.afw.image as afwImage
#import lsst.afw.geom as afwGeom
#import lsst.afw.math as afwMath
#import lsst.afw.table as afwTable
#import lsst.afw.display.ds9 as ds9
#from numpy import *
#import pylab as plt
#import scipy
#
#import ROOT
#from ROOT import *
#from ROOT import TH1D, TF1
#

import lsst.afw.geom.ellipses as Ellipses
import lsst.afw.detection   as afwDetect
import numpy as np
from lsst import afw
from __builtin__ import str

import pylab
from pylab import *
from numpy import ma
import numpy

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm

import matplotlib.mlab as mlab

def randrange(n, vmin, vmax):
    return(vmax-vmin)*random.rand(n) + vmin


import numpy, matplotlib.mlab

def makeVectorRedundant(xs, red):
    t = numpy.zeros(red * xs.shape[0])
    for i in xrange(red):
        t[i::red] = xs
    return t


def prepLegoData(xlims, ylims, zvals):
    """Prepare 3D histogram data to be used with matplotlib's Axes3D/Axes3DI.

    usage example:

    >>> nx, ny = 3, 5
    >>> X, Y, Z = prepLegoData(numpy.arange(nx), numpy.arange(ny),
    ... numpy.random.rand(nx, ny))
    >>> fig = pylab.figure()
    >>> ax = matplotlib.axes3d.Axes3DI(fig)
    >>> ax.plot_surface(X, Y, Z, rstride=2, cstride=2)
    >>> pylab.show()

    @param xlims: N+1 array with the bin limits in x direction
    @param ylims: M+1 array with the bin limits in y direction
    @param zvals: a 2D array with shape (N, M) with the bin entries,
        example::
        --> y-index (axis 1)
        |       z_0_0  z_0_1  ...
        |       z_1_0  z_1_1  ...
        V        ...
        x-index (axis 0)
    @returns: X, Y, Z 2D-arrays for Axes3D plotting methods
    """
    assert xlims.shape[0] - 1 == zvals.shape[0]
    assert ylims.shape[0] - 1 == zvals.shape[1]

    # use a higher redundancy for surface_plot
    # must be a multiple of 2!
    red = 4


    X, Y = pylab.meshgrid(makeVectorRedundant(xlims, red),
                                    makeVectorRedundant(ylims, red))
    #X, Y = matplotlib.mlab.meshgrid(makeVectorRedundant(xlims, 2),
                         #makeVectorRedundant(ylims, 2))
    Z = numpy.zeros(X.shape)

    # enumerate the columns of th zvals
    for yi, zvec in enumerate(zvals):
        #print makeVectorRedundant(zvec, red)
        #print Z[2*xi + 1, 1:-1]
        #Z[2*xi + 1, 1:-1] = Z[2*xi + 2, 1:-1] = makeVectorRedundant(zvec, 2)
        t = makeVectorRedundant(zvec, red)
        #print 't', t.shape
        for off in xrange(1, red+1):
            #print red*xi, Z[red*xi + off, red/2:-red/2].shape
            # Z[red*xi + off, red/2:-red/2] = t
            Z[red/2:-red/2, red*yi + off] = t
    return X, Y, Z


def test_lego():
    import pylab
#    from matplotlib import axes3d
    from mpl_toolkits.mplot3d import axes3d
#
#    X, Y, Z = prepLegoData(numpy.arange(3), numpy.arange(3),
#            numpy.array([[1, 3], [2, 4]]))
#    fig = pylab.figure()
#    ax1 = axes3d.Axes3D(fig)
#    ax1.plot_wireframe(X, Y, Z)

#
#    X, Y, Z = prepLegoData(numpy.arange(4), numpy.arange(5),
#            numpy.array([[1.0, 1.5, 1.3],
#                        [1.7, 2.1, 0.8],
#                        [2.1, 2.0, 0.7],
#                        [2.5, 1.9, 0.5]])
#            )
#
#    ax2 = axes3d.Axes3D(pylab.figure())
#    ax2.plot_wireframe(X, Y, Z, colors=((0,0,0),))
#    ax2.plot_surface(X, Y, Z, rstride=2, cstride=2,
#            edgecolors='w')
#    ax2.set_xlabel('X')
#    ax2.set_ylabel('Y')
#    ax2.set_zlabel('#')
#    
#    show()
    
    from matplotlib import cm
    

    nx, ny = 23, 8
    z = numpy.random.rand(nx, ny)
    X, Y, Z = prepLegoData(numpy.arange(nx + 1), numpy.arange(ny + 1),
            z)
    ax3 = axes3d.Axes3D(pylab.figure())
    ax3.plot_surface(X, Y, Z, rstride=2, cstride=2,
            edgecolors='w', cmap=cm.jet)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_zlabel('#')


    pylab.show()
if __name__ == '__main__':
    import os
    import numpy as np
    import lsst.afw.display.ds9 as ds9

    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'
    
    from my_functions import OpenTimepixInDS9
#     OpenTimepixInDS9('/mnt/hgfs/VMShared/Data/new_sensors/oxford/march_2015/E404_50nm_newsample/420@133_1.txt')
#     OpenTimepixInDS9('/mnt/hgfs/VMShared/Data/new_sensors/suny_01042015/50nm_big_runs/422_big_only_electrons/1@1_1.txt')
#     OpenTimepixInDS9('/mnt/hgfs/VMShared/Data/new_sensors/suny_01042015/50nm_big_runs/422_big_only_ions/1@1_1.txt')
    OpenTimepixInDS9('/mnt/hgfs/VMShared/Data/new_sensors/bnl/24_03_2015/A2(300nm)/Run4/1_0001.txt')
 
    ds9.ds9Cmd('-scale limits 6400 6600')
    ds9.ds9Cmd('-scale limits 6400 6600')
    
    exit()
    
    
    expids,durations = np.loadtxt('/mnt/hgfs/VMShared/temp/input.txt', delimiter = '\t', skiprows = 1, usecols = (0,1), unpack = True)
    
    for i in range(len(expids)):
        print i, str(expids[i]), str(durations[i])
    
        
    dl = []
    files = os.listdir('/mnt/hgfs/VMShared/Data/des_darks/')
    for filename in files:
        dl.append(filename[8:14])
    print "downloaded " + str(len(dl))

    index = []
#     for i in range(len(expids)):
#         indx = expids.index(dl[i])
#         if indx != -1: index.append(indx)


#     index = np.where(str(dl)  str(expids))
#     print index


    locations = np.in1d(expids, dl)
    index = np.where(locations == True)
    
    for value in expids[index]:
        print str(int(value)) + '\t'
        
    
    
    inttime = durations[index].sum()
    print inttime
    exit()
       

    print "running"
    from my_functions import Timepix_ToT_to_lego
    from time import sleep

    filename = '/'
#    path = '/home/mmmerlin/Desktop/VMShared/Data/QE/Disc method/627nm/ToT before/10us_5V/'
#    path = '/home/mmmerlin/Desktop/VMShared/Data/QE/Disc method/627nm/ToT before/50us_5V/'
    path = '/home/mmmerlin/Desktop/VMShared/Data/QE/Disc method/627nm/Focusing sweep/'
    files = os.listdir(path)
    
    spot_center_x = 150
    spot_center_y = 98
    boxsize_over_2 = 26
    mask_values_over = 100
    zmax = 75
    display_RMS = True
    
    from root_functions import CANVAS_HEIGHT, CANVAS_WIDTH
    from ROOT import TH2F, TCanvas

    c1 = TCanvas( '1', '1', CANVAS_WIDTH,CANVAS_HEIGHT)
    av_hist = TH2F('', '',256,0,255,256, 0, 255)
    
#    c2 = TCanvas( '2', '2', CANVAS_WIDTH,CANVAS_HEIGHT)
    
    for i, file in enumerate(files):
        filenum = str(i).zfill(2)
        hist = Timepix_ToT_to_lego(path + file, spot_center_x, spot_center_y, boxsize_over_2, savefile='/home/mmmerlin/output/focusing_no_rotation.gif+5', mask_above = mask_values_over, print_RMS= False, fix_zmax = zmax)
#        hist = Timepix_ToT_to_lego(path + file, spot_center_x, spot_center_y, boxsize_over_2, savefile='/home/mmmerlin/output/focusing.gif+5', mask_above = mask_values_over, print_RMS= False, fix_zmax = zmax, nfiles_for_camera_tricks = 500, filenum_for_camera_trick =i)
#        hist = Timepix_ToT_to_lego(path + file, spot_center_x, spot_center_y, boxsize_over_2, mask_above = mask_values_over, print_RMS= False, fix_zmax = zmax, nfiles_for_camera_tricks = 200, filenum_for_camera_trick =i)
#        hist.Draw("lego2 0")
#        av_hist += hist
#        c2.SaveAs('/home/mmmerlin/output/b.gif+10')
        print i
        if i == 500: break
    print"done"
    exit()

    av_hist.GetXaxis().SetTitle('x')
    av_hist.GetYaxis().SetTitle('y')
    av_hist.GetZaxis().SetTitle('ToT (us)')
    av_hist.GetXaxis().SetRangeUser(spot_center_x - boxsize_over_2, spot_center_x + boxsize_over_2)
    av_hist.GetYaxis().SetRangeUser(spot_center_y - boxsize_over_2, spot_center_y + boxsize_over_2)
    av_hist.GetXaxis().SetTitleOffset(1.2)
    av_hist.GetYaxis().SetTitleOffset(1.4)
    av_hist.GetZaxis().SetTitleOffset(1.2)

    av_hist.Draw("lego2 0 z") #box, lego, colz, lego2 0
    av_hist.SetStats(False)
    
    c1.SetTheta(41.57391)
    c1.SetPhi(-132.4635)
        
    c1.SaveAs('/home/mmmerlin/output/avg_10us.png')



    print "finished"
    exit()







    test_lego()

    print "done"
    
    exit()
    
    import pylab
#    from pylab import *
    from numpy import ma
    import numpy
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import axes3d
    from matplotlib import cm
    
    data=numpy.loadtxt("/home/mmmerlin/useful/mystars_420_20140430.cat")
    
    o = data[:, 0]
    a = data[:, 1]
    area = data[:, 2]
    x = data[:, 3]
    y = data[:, 4]
    x2 = data[:, 5]
    y2 = data[:, 6]
    xy = data[:, 7]
    aa = data[:, 8]
    bb = data[:, 9]
    angle = data[:, 10]
    e1 = (x2-y2)/(x2+y2)
    e2 = (2*xy)/(x2+y2)
    #print e1
    
    theta = numpy.arctan2(e2,e1)/2.
    r = numpy.sqrt(e1**2 + e2**2)
    u = r*numpy.cos(theta)
    v = r*numpy.sin(theta)
    
    #convert LSST pixels to arcsec
    x1 = x/5.
    y1 = y/5.
    
    fig = plt.figure()
    
    from __builtin__ import repr
    print repr(x)
    
    ax = fig.gca(projection='3d')
    ax.plot_trisurf(x, y, 3.1415*aa*bb, cmap=cm.jet, linewidth=0.2)
    #ax.plot_surface(x, y, area, rstride=10, cstride=10)
    #ax.plot_wireframe(x, y, area, rstride=10, cstride=10)
    #cset = ax.contourf(x, y, area, zdir='z', offset=-100, cmap=cm.coolwarm)
    #cset = ax.contourf(x, y, area, zdir='x', offset=-40, cmap=cm.coolwarm)
    #cset = ax.contourf(x, y, area, zdir='y', offset=40, cmap=cm.coolwarm)
    
    ax.set_xlabel('x')
    #ax.set_xlim(-40, 40)
    ax.set_ylabel('y')
    #ax.set_ylim(-40, 40)
    ax.set_zlabel('PSF area')
    #ax.set_zlim(-100, 100)
    
    
    plt.show()
    
    
    show()

    
    
    
    exit()

    a = TH1D("","",100,-10,10)
    print "1"
    er = TF1("er","TMath::Erfc(x)",0,10)
    print "2"
    a.FillRandom("er",10000)
    print "3"

    ga = Ga( TF1( "s", gax, -10., 10., 3 ) )
    

    b = TF1("b",ga,-10,10,3)
    print "4"
    b.SetParameters(0.,1.,1000.)
    print "5"
    a.Fit(b,"","",-2,2)

    print "done."
    exit()











#    from image_assembly import AssembleImage
#       
##    filename = '/home/mmmerlin/Desktop/VMShared/Data/all_darks/113-03_dark_dark_999.00_000_20140709014210.fits'
#    filename = '/home/mmmerlin/useful/fringes.fits'
#    metadata_filename = '/home/mmmerlin/useful/herring_bone.fits'
#    
#    
#    image = AssembleImage(filename, metadata_filename, subtract_background=True)
#    ds9.mtv(image)
#    
#    
#    print "success"
#    exit()
    
    
    
    filename = '/home/mmmerlin/Desktop/VMShared/Data/all_darks/113-03_dark_dark_999.00_000_20140709014210.fits'
    
    exposure = afwImage.ExposureF(filename)
    metaData = exposure.getMetadata()
    
#    header = afwImage.readMetadata(filename, 1) # PHU's DETSIZE differs from that of the extensions...?
#    header.get("LTM1_1")

#    header = 

    metaData.getOrderedNames()

#    print header.get("LTM1_1")
    
    
    
    
    
    print 'Done.'
    exit()
    
    
    
    
    
    
    
    
    
    
#    filename = '/home/mmmerlin/useful/fringes.fits'
    filename = '/home/mmmerlin/useful/herring_bone.fits'
#    filename = '/home/mmmerlin/useful/dark.fits'
        #    filename = '/home/mmmerlin/Desktop/VMShared/Data/long_darks_20140708/113-03_dark_dark_999.00_000_20140709014210.fits'
        #
        ##
        #    import astropy.io.fits as pyfits
        #
        #    
        #    for i in range(1,17):
        #        print i
        #        metadata = pyfits.getheader(filename, i)
        #        print metadata['DETSEC']





    header = afwImage.readMetadata(filename, 1) # PHU's DETSIZE differs from that of the extensions...?
#    image = _assemble(read(filename))
    ds9.mtv(image, frame=1)






#    if True:
##        from astropy.io import fits
#        import astropy
#        print 'Pyfits...'
#        
#        home_dir = expanduser("~")
#
#        input_path = home_dir + '/dl/darks/from ccdtest.e2v.CCD250.112-04.dark.20140419-190507/'
#
#        input_file = '000-00_dark_dark_500.00_004_20140420040711.fits'
#        fitsfile = fits.open(input_path + input_file)
#        fitsfile.info()
#        
#        fitsfile.func_doc.amap(fn)
#    
#    exit()
#    


    if False:
        from astropy.modeling import models, fitting
        
        # Generate fake data
        random.seed(0)
        x = linspace(-5., 5., 200)
        y = 3 * exp(-0.5 * (x - 1.3)**2 / 0.8**2) #+ 1.5 * np.exp(-0.5 * (x + 3.4)**2 / 0.8**2)
        y += random.normal(0., 0.2, x.shape)
        
        # Fit the data using a box model
        t_init = models.Trapezoid1D(amplitude=1., x_0=0., width=1., slope=0.5)
        f1 = fitting.NonLinearLSQFitter()
        t = f1(t_init, x, y)
        
        # Fit the data using a Gaussian
        g_init = models.Gaussian1D(amplitude=1., mean=1, stddev=1.)
#        g_init2 = models.Gaussian1D(amplitude=1., mean=-1, stddev=1.)
#        g_init = g_init.add_model(g_init2, mode = 's')

        f2 = fitting.NonLinearLSQFitter()
        g = f2(g_init, x, y)
        
        # Plot the data with the best-fit model
        plt.figure(figsize=(8,5))
        plt.plot(x, y, 'ko')
        plt.plot(x, t(x), 'b-', lw=2, label='Trapezoid')
        plt.plot(x, g(x), 'r-', lw=2, label='Gaussian')
        plt.xlabel('Position')
        plt.ylabel('Flux')
        plt.legend(loc=2)

        plt.show()

    

    if False: 
        # Generate data points with noise
#        from numpy import *
        from scipy import optimize
        num_points = 150
        Tx = linspace(5., 8., num_points)
        Ty = Tx
        
        tX = 11.86*cos(2*pi/0.81*Tx-1.32) + 0.64*Tx+4*((0.5-scipy.rand(num_points))*exp(2*scipy.rand(num_points)**2))
        tY = -32.14*cos(2*pi/0.8*Ty-1.94) + 0.15*Ty+7*((0.5-scipy.rand(num_points))*exp(2*scipy.rand(num_points)**2))
        
        # Fit the first set
        fitfunc = lambda p, x: p[0]*cos(2*pi/p[1]*x+p[2]) + p[3]*x # Target function
        errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
        p0 = [-15., 0.8, 0., -1.] # Initial guess for the parameters
        p1, success = optimize.leastsq(errfunc, p0[:], args=(Tx, tX))
        
        time = linspace(Tx.min(), Tx.max(), 1000)
        plt(Tx, tX, "ro", time, fitfunc(p1, time), "r-") # Plot of the data and the fit
        
        
        # Fit the second set
        p0 = [-15., 0.8, 0., -1.]
        p2,success = optimize.leastsq(errfunc, p0[:], args=(Ty, tY))
        
        time = linspace(Ty.min(), Ty.max(), 1000)
        plt(Ty, tY, "b^", time, fitfunc(p2, time), "b-")
    
        # Legend the plot
        plt.title("Oscillations in the compressed trap")
        plt.xlabel("time [ms]")
        plt.ylabel("displacement [um]")
        plt.legend(('x position', 'x fit', 'y position', 'y fit'))
        
        ax = plt.axes()
        
        plt.text(0.8, 0.07,
             'x freq :  %.3f kHz \n y freq :  %.3f kHz' % (1/p1[1],1/p2[1]),
             fontsize=16,
             horizontalalignment='center',
             verticalalignment='center',
             transform=ax.transAxes)
        
        plt.show()
    
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        n = 100
        for c, m, zl, zh in [('r', 'o', -50, -25), ('b', '^', -30, -5)]:
            xs = randrange(n, 23, 32)
            ys = randrange(n, 0, 100)
            zs = randrange(n, zl, zh)
            ax.scatter(xs, ys, zs, c=c, marker=m)
        
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        
        plt.show()

    
    
    


    from os.path import expanduser
    from my_functions import TimepixToExposure
    home_dir = expanduser("~")

#    input_file = home_dir + '/Desktop/DMStack VM Shared/20130104221032-986.fits'
#    exposure = afwImg.ExposureF(input_file)
#    maskedImage = exposure.getMaskedImage()
#    image = maskedImage.getImage()
    
    
    input_file = home_dir + '/Desktop/VMShared/timepix/Delay 0 Microseconds_0001.txt'
    image = TimepixToExposure(input_file)
    


    # initialise DS9, deal with a bug in its launching
    try:
        ds9.initDS9(False)
    except ds9.Ds9Error:
        print 'DS9 launch bug error thrown away (probably)'

    ds9.mtv(image)









    print '\n***End code***'







