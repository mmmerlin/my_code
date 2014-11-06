from scipy import *
from pylab import *
from scipy import optimize



if __name__ == '__main__':
    print "Landau test"

    input_path = '/home/mmmerlin/dl/landau/'
    input_file = 'landau_no_noise.dat'

#    # Read in Landau histogram data
    datafile = open(input_path + input_file)
    hist_data = [float(line.rstrip()) for line in datafile]
    datafile.close()
    
#    my_fig = figure()
    my_hist = hist(hist_data, bins = 100)
    
    
#    num_points = 150
#    Tx = linspace(5., 8., num_points)
#    Ty = Tx
#    
#    tX = 11.86*cos(2*pi/0.81*Tx-1.32) + 0.64*Tx+4*((0.5-rand(num_points))*exp(2*rand(num_points)**2))
#    tY = -32.14*cos(2*pi/0.8*Ty-1.94) + 0.15*Ty+7*((0.5-rand(num_points))*exp(2*rand(num_points)**2))
#     
#    fitfunc = lambda p, x: p[0]*cos(2*pi/p[1]*x+p[2]) + p[3]*x # Target function
#    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
#    p0 = [-15., 0.8, 0., -1.] # Initial guess for the parameters
#    p1, success = optimize.leastsq(errfunc, p0[:], args=(Tx, tX))
#    
#    time = linspace(Tx.min(), Tx.max(), 100)
#    plot(Tx, tX, "ro", time, fitfunc(p1, time), "r-") # Plot of the data and the fit
        
        
        
    # Fit the first set
    fitfunc = lambda p, x: p[0]*(x-p[1])**2 + p[2] # Target function
    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
    p0 = [-2., 300 ,11000.] # Initial guess for the parameters
#    p1, success = optimize.leastsq(errfunc, p0[:], my_hist)
    
    
    x = linspace(0, 2000, 1000)
    plot(x, fitfunc(p0, x)) # Plot of the data and the fit
    
    ylim([0,12000])
    xlim([0,1500])
    
    
    show()
    exit()
    
    # Fit the second set
    p0 = [-15., 0.8, 0., -1.]
    p2,success = optimize.leastsq(errfunc, p0[:], args=(Ty, tY))
    
    time = linspace(Ty.min(), Ty.max(), 1000)
    plot(Ty, tY, "b^", time, fitfunc(p2, time), "b-")

    # Legend the plot
    title("Oscillations in the compressed trap")
    xlabel("time [ms]")
    ylabel("displacement [um]")
    legend(('x position', 'x fit', 'y position', 'y fit'))
    
    ax = axes()
    
    text(0.8, 0.07,
         'x freq :  %.3f kHz \n y freq :  %.3f kHz' % (1/p1[1],1/p2[1]),
         fontsize=16,
         horizontalalignment='center',
         verticalalignment='center',
         transform=ax.transAxes)
    
    show()


    print '\n***End code***'







