import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from scipy import *

#import  pylab as pl
from os.path import expanduser


if __name__ == '__main__':
    print "Running ellipticity comparison\n"
 
#===============================================================================
# Load and display   
   
    #0 = display nothing, 1 = just display the fits file, 2 = draw boxes around footprints, mark centroids
    DISPLAY_LEVEL = 2 

    home_dir = expanduser("~")
    output_path = home_dir + '/output/'
    input_path = home_dir + '/dl/'

    input_file = 'sparse_tree_rings.fits'
 
#===============================================================================
# Plot options
#===============================================================================
    ANGLES='uv'
    UNITS = 'xy'
    PIVOT = 'middle'
    WIDTH = 0.5
    HEADWIDTH = 0
    XMIN = 1536
    XMAX = 2436
    YMIN = 1600
    YMAX = 2450
#===============================================================================


#===============================================================================
# Sextractor - 2nd moments
#===============================================================================
    data = np.loadtxt(input_path + "sparse_tree_rings.cat")
    x = data[:, 2] #x pos
    y = data[:, 3] #y pos
    x2 = data[:, 4] #x pos variance
    y2 = data[:, 5] #y pos variance
    xy = data[:, 6] # x-y covariance
    aa = data[:, 7] #major axis RMS
    bb = data[:, 8] #minor axis RMS
    angle = data[:, 9] #theta in degrees

    e1 = (x2 - y2) / (x2 + y2)
    e2 = (2 * xy) / (x2 + y2)

    theta = np.arctan2(e2, e1) / 2.
    r = np.sqrt(e1 ** 2 + e2 ** 2)
    u = r * np.cos(theta)
    v = r * np.sin(theta)

    plt.figure()
    sex_moments = plt.quiver(x, y, u, v, angles=ANGLES, units=UNITS, pivot=PIVOT, width=WIDTH, headwidth=HEADWIDTH , scale=1./500. )
    plt.axis([XMIN, XMAX, YMIN, YMAX])
    plt.title('Sextractor - second moments')
#===============================================================================


#===============================================================================
# Sextractor - a,b,theta
#===============================================================================
    sex_ellipticity = (aa - bb)/(aa)
    ob_size = aa * bb *3.1415
    

    xvectors = sex_ellipticity * np.cos(angle * np.pi /180.) 
    yvectors = sex_ellipticity * np.sin(angle * np.pi /180.)
    
    plt.figure()
    sex_abt = plt.quiver(x, y, xvectors, yvectors, angles=ANGLES, units=UNITS, pivot=PIVOT, width=WIDTH, headwidth=HEADWIDTH , scale=1./500. )
    plt.axis([XMIN, XMAX, YMIN, YMAX])
    plt.title('Sextractor - a, b, theta')
#===============================================================================



#===============================================================================
# 3D Scatter plot
#===============================================================================
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, ob_size)
    plt.show()


    def flux_qubit_potential(phi_m, phi_p):
        alpha = 0.2
        phi_ext = 2 * pi * 0.5
        return 2 + alpha - 2 * cos(phi_p)*cos(phi_m) - alpha * cos(phi_ext - 2*phi_p)


    phi_m = linspace(0, 2*pi, 100)
    phi_p = linspace(0, 2*pi, 100)
    X,Y = meshgrid(phi_p, phi_m)
    Z = flux_qubit_potential(X, Y)
    

    ax = fig.add_subplot(1, 2, 1, projection='3d')
    
    p = ax.plot_surface(X, Y, Z, rstride=4, cstride=4, linewidth=0)

#===============================================================================


##===============================================================================
## Distributions of angles
##===============================================================================
#    
#    pl.figure()
#    pl.hist(angle, bins = 180)
#    pl.title('Sextractor angle histogram')
##===============================================================================






    plt.show()
    print '\n*** End code ***'














