# reads Fe55 data, assembles mosaic, finds footprints, fits 2D gaussian for each stamp
# plots histos
def DrawFootprint(footprint):
    import lsst.afw.display.utils as displayUtils
    x,y = footprint.getCentroid()
    ds9.dot("x",x,y)# cross on the peak
    displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more


#from ROOT import TCanvas, TF1, TH1F, TH2F
from ROOT import *
import ROOT
from root_functions import CANVAS_WIDTH
#import Initialise_ROOT

import cPickle as pickle

# import Erin's package
import ngmix
from ngmix.fitting import MCMCSimple, print_pars

# import the DMstack stuff 
import lsst.afw.math        as math
import lsst.afw.table       as afwTablesudo 
import lsst.afw.image       as afwImg
import lsst.afw.detection   as afwDetect
import lsst.afw.display.ds9 as ds9

import lsst.afw.geom.ellipses as Ellipses
import lsst.afw.display.utils as displayUtils
from lsst.pex.config import Config, Field, ConfigField, makePolicy
import lsst.pipe.base as pipeBase

import  numpy as np
import  pylab as pl
from matplotlib import cm
from numpy import log10, random

from os import listdir
from os.path import expanduser, join

from image_assembly import AssembleImage
from fit_constraints import ExamplePrior
from imprint import imprint

def srandu(num=None):
#  Generate random numbers in the symmetric distribution [-1,1]
    return 2*(np.random.random(num)-0.5)

if __name__ == '__main__':
    print "Running Andrei's Fe55 cluster finder code"

# running modes
    Pickled = False
    Print   = False
    ViewDS9 = False and not Pickled
            
# break the loop after Nmax hits if Nmax > 0
    Nmax = -1

# define some arrays
    xcoords, ycoords, npixels, clusterI = [], [], [], []
    majors, minors, thetas = [], [], []
    XX, YY, G1, G2, T, Flux, Theta, Size = [], [], [], [], [], [], [], []
    eXX, eYY, eG1, eG2, eT, eFlux, Chi2 = [], [], [], [], [], [], []
    xco, yco, xve, yve = [], [], [], []
    Stamp_c, Stamp_t, Stamp_b, Stamp_l, Stamp_r = [], [], [], [], []

    pickles = []
    histos  = []

# zero counters
    Ntotal  =   0
    Nfitted =   0
    Nfilled =   0
    Nselected = 0
    Nsinglehit =0
    Nsections = 0
    Nerrors =   0
    Nellip =    0
    Ngeom =     0
    NThisLoop = 0
    
    #    initialise DS9, deal with a bug in its launching
    if ViewDS9: 
        try:
            ds9.initDS9(False)
        except ds9.Ds9Error:
            print 'DS9 launch bug error thrown away (probably)' 

# set up some paths for filenames
    home_dir = expanduser("~")
    metadata_file = home_dir + '/useful/herring_bone.fits'

#    input_path_Fe55data = '/mnt/hgfs/VMShared/small_fe55_set/'
    input_path_Fe55data = '/mnt/hgfs/VMShared/Data/fe55/ITL_114_04/'
    filenames = listdir(input_path_Fe55data)

    pickle_prefix = 'grow_2_npx_1'
    pickle_output_path = '/mnt/hgfs/VMShared/Data/my_pickles/'
    
# read results from a file or loop over raw data to produce and save results
    
    if Pickled:
        print pickle_filename 
        pickles = pickle.load(open(pickle_filename, 'rb'))
        Theta = pickles[0]
        G1 =    pickles[1]
        G2 =    pickles[2]
        XX =    pickles[3]
        YY =    pickles[4]
        T  =    pickles[5]
        Flux =  pickles[6]
        eXX =   pickles[7]
        eYY =   pickles[8]
        eG1 =   pickles[9]
        eG2 =   pickles[10]
        eT  =   pickles[11]
        eFlux = pickles[12]
        Chi2 =  pickles[13]
        xvectors =  pickles[14]
        yvectors =  pickles[15]
        xcoords =   pickles[16]
        ycoords =   pickles[17]
        Sigma   =   pickles[18]
        eSigma  =   pickles[19]
        Ellip   =   pickles[20]
        Stamp_c =   pickles[21]
        Stamp_t =   pickles[22]
        Stamp_b =   pickles[23]
        Stamp_l =   pickles[24]
        Stamp_r =   pickles[25]

    else:
        for Fe55file in filenames:
            input_file = input_path_Fe55data + Fe55file    
            print input_file 
        
# Merlin's magic to mosaic correctly
            image = AssembleImage(input_file, metadata_file, subtract_background = True)
            maskedImage = afwImg.MaskedImageF(image)
                
            # show the file
            if ViewDS9: ds9.mtv(image)   
        
            # get the stats and print them out
            statFlags = math.NPOINT | math.MEAN | math.STDEV | math.MAX | math.MIN | math.ERRORS| math.STDEVCLIP
            control = math.StatisticsControl()
            SAT = afwImg.MaskU_getPlaneBitMask("SAT")
            control.setAndMask(SAT)
        
            imageStats = math.makeStatistics(maskedImage, statFlags, control)
            numBins = imageStats.getResult(math.NPOINT)[0]
            mean = imageStats.getResult(math.MEAN)[0]
            stdev = imageStats.getResult(math.STDEV)[0]
            stdevclip = imageStats.getResult(math.STDEVCLIP)[0]
            _max = imageStats.getResult(math.MAX)[0]
            print "The image has dimensions %i x %i pixels" % (maskedImage.getWidth(), maskedImage.getHeight())
            print "Mean = %s" % mean
            print "Stdev = %s" % stdev
            print "Stdevclip = %s" % stdevclip
            print "Max = %s" % _max
            print "nPx = %s\n" % numBins
        
# find Fe55 clusters - set up some clustering parameters
            thresholdValue = mean + (stdevclip * 10.0)  
            print "Theshold value = %s"%thresholdValue     
            npixMin = 1
            grow = 2
            isotropic = True
        
# do the footprint finding
            threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
            footPrintSet = afwDetect.FootprintSet(maskedImage, threshold, "DETECTED", npixMin)
            footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
        
            footPrints = footPrintSet.getFootprints()
            footPrintSet.setMask(maskedImage.getMask(), "DETECTED")
            print footPrints.size(), "footPrint(s) found\n"
        
            if ViewDS9:
                for footprint in footPrints:
                    DrawFootprint(footprint)
                    
        
# loop over found footprints
            footprint = afwDetect.Footprint()    
            for footprint in footPrints:               
                Ntotal = Ntotal + 1
                NThisLoop += 1
# calculate shapes using vanilla DM
                quadshape = footprint.getShape()
                axesshape = Ellipses.Axes(quadshape)
                A = axesshape.getA()
                B = axesshape.getB()
                theta = axesshape.getTheta()
                centroid_x, centroid_y = footprint.getCentroid()
                npix = footprint.getNpix()
    #            print "\n npix = %s" % npix

# draw reconstructed ellipses over hits
#                if ViewDS9:
#                    Ixx = quadshape.getIxx()
#                    Iyy = quadshape.getIyy()
#                    Ixy = quadshape.getIxy()
#                    argstring = "@:" + str(Ixx) + ',' + str(Ixy) + ',' + str(Iyy)
#                    ds9.dot(argstring, centroid_x, centroid_y)
#                    ds9.zoom(6)
          
# another piece of magic from Jim B to evaluate the flux
                array = np.zeros(footprint.getArea(), dtype=image.getArray().dtype)
                afwDetect.flattenArray(footprint, image.getArray(), array, image.getXY0())
                intens = array.sum()
                
# get stamps for Erin's sub-sampling
                box = footprint.getBBox()
                xmin = box.getMinX()
                xmax = box.getMaxX()
                ymin = box.getMinY()
                ymax = box.getMaxY()
#                im = image.getArray()
#                stamp = im[ymin:ymax+1, xmin:xmax+1]
                im = image.getArray().transpose()
                stamp = im[xmin:xmax+1, ymin:ymax+1]

# start using Erin's package               
                model="gauss"
        
# create a weight map (just 1/noise^2 for all pixels for now)
                noise = 0*stamp + stdevclip
                weight_map = 1/noise**2
               
# create an Observation object.  Only image and weight for now
                obs = ngmix.observation.Observation(stamp, weight=weight_map)
                
# parameters for the maximum likelihood fitter
                lm_pars={'maxfev':500,
                         'ftol':1.0e-6,
                         'xtol':1.0e-6,
                         'epsfcn': 1.0e-6}
        
# constrain T and Flux to be in certain ranges
        #        log10T_range=[log10(2*0.1**2), log10(2*10.0**2)]
        #        log10Flux_range=[log10(2000), log10(4000)]
        #        prior=ExamplePrior(log10T_range,log10Flux_range)

# do not constrain        
#                prior=None
#                fitter=ngmix.fitting.LMSimple(obs, model, nsub=nsub, lm_pars=lm_pars, prior=prior)
                        
# make a guess for [cen1,cen2,g1,g2,T,flux] where T is 2*sigma**2
                cen1 = centroid_x - xmin
                cen2 = centroid_y - ymin
                g1=0.
                g2=0.
                T_guess = 0.32 # = 2*(0.4)**2
                flux_guess=intens
#                guess=np.array( [cen1,cen2,g1,g2,log10(T_guess),log10(flux_guess)] )
#                guess=np.array( [cen1,cen2,g1,g2,T_guess,flux_guess] )

                nwalkers =  80
                burnin =    400
                nstep =     400
                npars =     6
# use 4x4 sub-pixels for fit
                nsub =      4

                guess=np.zeros( (nwalkers, npars) )
                guess[:,0] = centroid_x - xmin + 0.1*srandu(nwalkers)
                guess[:,1] = centroid_y - ymin + 0.1*srandu(nwalkers)
                guess[:,2] = g1 + 0.1*srandu(nwalkers)
                guess[:,3] = g2 + 0.1*srandu(nwalkers)
                guess[:,4] = T_guess*(1.0 + 0.1*srandu(nwalkers))
                guess[:,5] = flux_guess*(1.0 + 0.1*srandu(nwalkers))
        
# run the fitter
                mc  = MCMCSimple(obs, model, nwalkers=nwalkers, nsub=nsub)
                pos = mc.run_mcmc(guess, burnin)
                pos = mc.run_mcmc(pos,   nstep)

                mc.calc_result()

                result = mc.get_result()
                
                if Print:
                    print_pars(result['pars'],     front='pars:')
                    print_pars(result['pars_err'], front='err: ')
                    print 'chi2per:',result['chi2per']
                    print 'arate:', result['arate']
#                fitter.run_lm(guess)
#                result=fitter.get_result()

                if Print: print "event", Ntotal
               
                if result['flags'] != 0:
                    print " *****  something went wrong ******"
                else:
                    Nfitted = Nfitted + 1
        
                    chi2 = result['chi2per']
                    xx  = result['pars'][0]
                    yy  = result['pars'][1]
                    gg1 = result['pars'][2]
                    gg2 = result['pars'][3]
                    tt  = result['pars'][4]
                    ff  = result['pars'][5]
    
                    exx  = result['pars_err'][0]
                    eyy  = result['pars_err'][1]
                    egg1 = result['pars_err'][2]
                    egg2 = result['pars_err'][3]
                    ett  = result['pars_err'][4]
                    eff  = result['pars_err'][5]
    
                    ixx = int(xx + 0.5)
                    iyy = int(yy + 0.5)

                    if Print:
                        imprint(stamp, fmt='%7.1f')
                        print "xmin, xmax, ymin, ymax"
                        print xmin, xmax, ymin, ymax
                        print "cen1, cen2", cen1, cen2
                        print "xx, yy, ixx, iyy, XX, YY"
                        print xx, yy, ixx, iyy, xx+0.5-ixx, yy+0.5-iyy
                        print "stamp size" 
                        print stamp.shape[0], stamp.shape[1]
                    
                    if ixx < stamp.shape[0]-1 and ixx > 0 and iyy < stamp.shape[1]-1 and iyy > 0:
                        stamp_c = stamp[ixx][iyy]
                        stamp_t = stamp[ixx][iyy+1]
                        stamp_b = stamp[ixx][iyy-1]
                        stamp_l = stamp[ixx-1][iyy]
                        stamp_r = stamp[ixx+1][iyy]
                    else:
                        stamp_c = 1
                        stamp_t = 0
                        stamp_b = 0
                        stamp_l = 0
                        stamp_r = 0
                                            
                    if Print:
                        print "center, top, bottom, left, right"
                        print stamp_c, stamp_t, stamp_b, stamp_l, stamp_r                                      
                    
                    XX.append(xx + 0.5 - ixx)
                    YY.append(yy + 0.5 - iyy)
                    G1.append(gg1) 
                    G2.append(gg2)
                    T.append(tt)
                    Flux.append(ff)
                    eXX.append(exx)
                    eYY.append(eyy)
                    eG1.append(egg1) 
                    eG2.append(egg2)
                    eT.append(ett)
                    eFlux.append(eff)
    
                    Chi2.append(chi2) 
    
                    majors.append(A)
                    minors.append(B)
                    thetas.append(theta)
                    xcoords.append(centroid_x)
                    ycoords.append(centroid_y)
                    npixels.append(npix)
                    clusterI.append(intens)
                    
                    Stamp_c.append(stamp_c)
                    Stamp_t.append(stamp_t)
                    Stamp_b.append(stamp_b)
                    Stamp_l.append(stamp_l)
                    Stamp_r.append(stamp_r)
                    
                
                if NThisLoop % 100 == 0: print "Analysed %s clusters of %s (%s%%) in %s"%(NThisLoop, footPrints.size(), round((100 * float(NThisLoop)/float(footPrints.size())),2), Fe55file)
                if Nmax > 0 and Ntotal == Nmax: break
            
            if not Pickled: 
                GG1 = np.array(G1)
                GG2 = np.array(G2)
                Ellip = np.sqrt(GG1*GG1 + GG2*GG2)
                TT = np.array(T)
                Sigma = np.sqrt(TT/2.)
                eSigma = eT / Sigma
        
                Theta = 0.5*np.arctan2(G2,G1)*180/np.pi
                TT = np.array(Theta)
                xvectors = Ellip * np.cos(TT) 
                yvectors = Ellip * np.sin(TT)
        
        # store data in a file
                pickles.append(Theta)
                pickles.append(G1)
                pickles.append(G2)
                pickles.append(XX)
                pickles.append(YY)
                pickles.append(T)
                pickles.append(Flux)
                pickles.append(eXX)
                pickles.append(eYY)
                pickles.append(eG1)
                pickles.append(eG2)
                pickles.append(eT)
                pickles.append(eFlux)
                pickles.append(Chi2)
                pickles.append(xvectors)
                pickles.append(yvectors)
                pickles.append(xcoords)
                pickles.append(ycoords)
                pickles.append(Sigma)
                pickles.append(eSigma)
                pickles.append(Ellip)
                pickles.append(Stamp_c)
                pickles.append(Stamp_t)
                pickles.append(Stamp_b)
                pickles.append(Stamp_l)
                pickles.append(Stamp_r)
            
        #                    majors.append(A)
        #                    minors.append(B)
        #                    thetas.append(theta)
        #                    npixels.append(npix)
        #                    clusterI.append(intens)
                
                pickle_filename = join(pickle_output_path, pickle_prefix + "_" + Fe55file)
                pickle.dump(pickles, open(pickle_filename, 'wb'), protocol = pickle.HIGHEST_PROTOCOL)
                NThisLoop = 0
            if Nmax > 0 and Ntotal == Nmax: break #next file
                
# calculate some additional things

# define histogram ranges

    XMIN, XMAX      = -20, 4120
#    YMIN, YMAX      = 1950, 4025
    YMIN, YMAX      = -20, 4025
#    XMIN, XMAX      = 2000, 2600
#    YMIN, YMAX      = -20, 2020
    XMID            = 2000
    YMID            = 2000
    XXMIN, XXMAX    = 0., 1.
    YYMIN, YYMAX    = 0., 1.
    XXMINC, XXMAXC  = 0.3, 0.7
    YYMINC, YYMAXC  = 0.3, 0.7
    GMIN, GMAX      = -0.25, 0.25
    eGMIN, eGMAX      = 0., 0.5
    EMIN, EMAX      = 0., 0.25
    SMIN, SMAX      = 0., 0.7
    eSMIN, eSMAX      = 0., 0.7
    FMIN, FMAX      = 400, 600
    CHIMIN, CHIMAX  = 0., 20
    THMIN, THMAX    = -90, 90
    FRMIN, FRMAX    = 0., 1.
    
    nb = 50
    nb1 = 50
    nb2 = 25
    
# define root 1D histos
    xH =        TH1F('x', ' ', nb, XMIN, XMAX)
#    xH = histos[1]
    yH =        TH1F('y', ' ', nb, YMIN, YMAX)
    xminH =     TH1F('min x', ' ', nb, XMIN, XMIN+nb)
    yminH =     TH1F('min y', ' ', nb, YMIN, YMIN+nb)
    xmaxH =     TH1F('max x', ' ', nb, XMAX-nb, XMAX)
    ymaxH =     TH1F('max y', ' ', nb, YMAX-nb, XMAX)
    xpixH =     TH1F('pixel x', ' ', nb1, XXMIN, XXMAX)
    ypixH =     TH1F('pixel y', ' ', nb1, YYMIN, YYMAX)
    exH =       TH1F('error x', ' ', nb1, XXMIN, XXMAX)
    eyH =       TH1F('error y', ' ', nb1, YYMIN, YYMAX)
    chi2H =     TH1F('chi2', ' ', nb, CHIMIN, CHIMAX)
    g1H =       TH1F('g1', ' ', nb1, GMIN, GMAX)
    g2H =       TH1F('g2', ' ', nb1, GMIN, GMAX)
    sigmaH =    TH1F('sigma', ' ', nb1, SMIN, SMAX)
    fluxH =     TH1F('flux', ' ', nb1, FMIN, FMAX)
    eg1H =      TH1F('error g1', ' ', nb1, 0., eGMAX)
    eg2H =      TH1F('error g2', ' ', nb1, 0., eGMAX)
    esigmaH =   TH1F('error sigma', ' ', nb1, 0., eSMAX)
    efluxH =    TH1F('error flux', ' ', nb1, 0., (FMAX-FMIN)/10.)
#    efluxH =    TH1F('error flux', ' ', nb1, 0., FMAX)
    thetaH =    TH1F('theta', ' ', nb1, THMIN, THMAX)
    ellipH =    TH1F('ellipticity', ' ', nb1, EMIN, EMAX)

# define root 2D histos

# xy map
    xyfullH =       TH2F('xyfull', ' ',nb1, XMIN, XMAX, nb1, YMIN, YMAX)
    xyfullellH =    TH2F('xyfullell', ' ',nb1, XMIN, XMAX, nb1, YMIN, YMAX)
    xyfullsigH =    TH2F('xyfullsig', ' ',nb1, XMIN, XMAX, nb1, YMIN, YMAX)
    xyfullg1P =     TProfile2D('xyfullg1p', ' ',nb1, XMIN, XMAX, nb1, YMIN, YMAX, GMIN, GMAX)
    xyfullg2P =     TProfile2D('xyfullg2p', ' ',nb1, XMIN, XMAX, nb1, YMIN, YMAX, GMIN, GMAX)
    xyfullsigP =    TProfile2D('xyfullsigp', ' ',nb1, XMIN, XMAX, nb1, YMIN, YMAX, SMIN, SMAX)
    xyfulltheP =    TProfile2D('xyfullthep', ' ',nb1, XMIN, XMAX, nb1, YMIN, YMAX, THMIN, THMAX)

# chi2 correlations
    g1chi2H =       TH2F('g1chi2', ' ',nb2, GMIN, GMAX, nb2, CHIMIN, CHIMAX)
    g2chi2H =       TH2F('g2chi2', ' ',nb2, GMIN, GMAX, nb2, CHIMIN, CHIMAX)
    sigmachi2H =    TH2F('sigmachi2', ' ',nb2, SMIN, SMAX, nb2, CHIMIN, CHIMAX)
    fluxchi2H =     TH2F('fluxchi2', ' ',nb2, FMIN, FMAX, nb2, CHIMIN, CHIMAX)
    thetachi2H =    TH2F('thetachi2', ' ',nb2, THMIN, THMAX, nb2, CHIMIN, CHIMAX)
    ellipchi2H =    TH2F('ellipchi2', ' ',nb2, EMIN, EMAX, nb2, CHIMIN, CHIMAX)

# edge correlations
    xminsigmaH =    TH2F('xminsigma', ' ',nb2, XMIN, XMIN+nb2, nb2, SMIN, SMAX)
    xmaxsigmaH =    TH2F('xmaxsigma', ' ',nb2, XMAX-nb2, XMAX, nb2, SMIN, SMAX)
    yminsigmaH =    TH2F('yminsigma', ' ',nb2, YMIN, YMIN+nb2, nb2, SMIN, SMAX)
    ymaxsigmaH =    TH2F('ymaxsigma', ' ',nb2, YMAX-nb2, YMAX, nb2, SMIN, SMAX)
    xminfluxH =     TH2F('xminflux', ' ',nb2, XMIN, XMIN+nb2, nb2, FMIN, FMAX)
    xmaxfluxH =     TH2F('xmaxflux', ' ',nb2, XMAX-nb2, XMAX, nb2, FMIN, FMAX)
    yminfluxH =     TH2F('yminflux', ' ',nb2, YMIN, YMIN+nb2, nb2, FMIN, FMAX)
    ymaxfluxH =     TH2F('ymaxflux', ' ',nb2, YMAX-nb2, YMAX, nb2, FMIN, FMAX)
    xminthetaH =    TH2F('xmintheta', ' ',nb2, XMIN, XMIN+nb2, nb2, THMIN, THMAX)
    xmaxthetaH =    TH2F('xmaxtheta', ' ',nb2, XMAX-nb2, XMAX, nb2, THMIN, THMAX)
    yminthetaH =    TH2F('ymintheta', ' ',nb2, YMIN, YMIN+nb2, nb2, THMIN, THMAX)
    ymaxthetaH =    TH2F('ymaxtheta', ' ',nb2, YMAX-nb2, YMAX, nb2, THMIN, THMAX)
    xminellipH =    TH2F('xminellip', ' ',nb2, XMIN, XMIN+nb2, nb2, EMIN, EMAX)
    xmaxellipH =    TH2F('xmaxellip', ' ',nb2, XMAX-nb2, XMAX, nb2, EMIN, EMAX)
    yminellipH =    TH2F('yminellip', ' ',nb2, YMIN, YMIN+nb2, nb2, EMIN, EMAX)
    ymaxellipH =    TH2F('ymaxellip', ' ',nb2, YMAX-nb2, YMAX, nb2, EMIN, EMAX)
    xming1H =       TH2F('xming1', ' ',nb2, XMIN, XMIN+nb, nb2, GMIN, GMAX)
    xmaxg1H =       TH2F('xmaxg1', ' ',nb2, XMAX-nb, XMAX, nb2, GMIN, GMAX)
    yming1H =       TH2F('yming1', ' ',nb2, YMIN, YMIN+nb, nb2, GMIN, GMAX)
    ymaxg1H =       TH2F('ymaxg1', ' ',nb2, YMAX-nb, YMAX, nb2, GMIN, GMAX)
    xming2H =       TH2F('xming2', ' ',nb2, XMIN, XMIN+nb, nb2, GMIN, GMAX)
    xmaxg2H =       TH2F('xmaxg2', ' ',nb2, XMAX-nb, XMAX, nb2, GMIN, GMAX)
    yming2H =       TH2F('yming2', ' ',nb2, YMIN, YMIN+nb, nb2, GMIN, GMAX)
    ymaxg2H =       TH2F('ymaxg2', ' ',nb2, YMAX-nb, YMAX, nb2, GMIN, GMAX)

    xminsigmaP =    TProfile('xminsigmap', ' ',nb2, XMIN, XMIN+nb2, SMIN, SMAX)
    xmaxsigmaP =    TProfile('xmaxsigmap', ' ',nb2, XMAX-nb2, XMAX, SMIN, SMAX)
    yminsigmaP =    TProfile('yminsigmap', ' ',nb2, YMIN, YMIN+nb2, SMIN, SMAX)
    ymaxsigmaP =    TProfile('ymaxsigmap', ' ',nb2, YMAX-nb2, YMAX, SMIN, SMAX)
    xminfluxP =     TProfile('xminfluxp', ' ',nb2, XMIN, XMIN+nb2, FMIN, FMAX)
    xmaxfluxP =     TProfile('xmaxfluxp', ' ',nb2, XMAX-nb2, XMAX, FMIN, FMAX)
    yminfluxP =     TProfile('yminfluxp', ' ',nb2, YMIN, YMIN+nb2, FMIN, FMAX)
    ymaxfluxP =     TProfile('ymaxfluxp', ' ',nb2, YMAX-nb2, YMAX, FMIN, FMAX)
    xminthetaP =    TProfile('xminthetap', ' ',nb2, XMIN, XMIN+nb2, THMIN, THMAX)
    xmaxthetaP =    TProfile('xmaxthetap', ' ',nb2, XMAX-nb2, XMAX, THMIN, THMAX)
    yminthetaP =    TProfile('yminthetap', ' ',nb2, YMIN, YMIN+nb2, THMIN, THMAX)
    ymaxthetaP =    TProfile('ymaxthetap', ' ',nb2, YMAX-nb2, YMAX, THMIN, THMAX)
    xminellipP =    TProfile('xminellipp', ' ',nb2, XMIN, XMIN+nb2, EMIN, EMAX)
    xmaxellipP =    TProfile('xmaxellipp', ' ',nb2, XMAX-nb2, XMAX, EMIN, EMAX)
    yminellipP =    TProfile('yminellipp', ' ',nb2, YMIN, YMIN+nb2, EMIN, EMAX)
    ymaxellipP =    TProfile('ymaxellipp', ' ',nb2, YMAX-nb2, YMAX, EMIN, EMAX)
    xming1P =       TProfile('xming1p', ' ',nb2, XMIN, XMIN+nb2, GMIN, GMAX)
    xmaxg1P =       TProfile('xmaxg1p', ' ',nb2, XMAX-nb2, XMAX, GMIN, GMAX)
    yming1P =       TProfile('yming1p', ' ',nb2, YMIN, YMIN+nb2, GMIN, GMAX)
    ymaxg1P =       TProfile('ymaxg1p', ' ',nb2, YMAX-nb2, YMAX, GMIN, GMAX)
    xming2P =       TProfile('xming2p', ' ',nb2, XMIN, XMIN+nb2, GMIN, GMAX)
    xmaxg2P =       TProfile('xmaxg2p', ' ',nb2, XMAX-nb2, XMAX, GMIN, GMAX)
    yming2P =       TProfile('yming2p', ' ',nb2, YMIN, YMIN+nb2, GMIN, GMAX)
    ymaxg2P =       TProfile('ymaxg2p', ' ',nb2, YMAX-nb2, YMAX, GMIN, GMAX)

# midline correlations
    xmidg1P =       TProfile('xmidg1p', ' ',nb2, XMID-nb2/2, XMID+nb2/2, GMIN, GMAX)
    ymidg1P =       TProfile('ymidg1p', ' ',nb2, YMID-nb2/2, YMID+nb2/2, GMIN, GMAX)
    xmidg2P =       TProfile('xmidg2p', ' ',nb2, XMID-nb2/2, XMID+nb2/2, GMIN, GMAX)
    ymidg2P =       TProfile('ymidg2p', ' ',nb2, YMID-nb2/2, YMID+nb2/2, GMIN, GMAX)

# inside pixel correlations
    xyH =           TH2F('xy', ' ',nb2, XXMIN, XXMAX, nb2, YYMIN, YYMAX)
    xycH =          TH2F('xyc', ' ',nb2, XXMIN, XXMAX, nb2, YYMIN, YYMAX)
    xycP =          TProfile2D('xyp', ' ',nb2, XXMIN, XXMAX, nb2, YYMIN, YYMAX, FRMIN, FRMAX)
    xytP2 =         TProfile2D('xyt', ' ',nb2, XXMIN, XXMAX, nb2, YYMIN, YYMAX, FRMIN, FRMAX)
    xytP =          TProfile('ytp', ' ',nb2, YYMIN, YYMAX, XXMIN, XXMAX)
    xyt =           TH1F('yt', ' ',nb, YYMIN, YYMAX)
    xybP2 =         TProfile2D('xyb', ' ',nb2, XXMIN, XXMAX, nb2, YYMIN, YYMAX, FRMIN, FRMAX)
    xybP =          TProfile('ybp', ' ',nb2, YYMIN, YYMAX, XXMIN, XXMAX)
    xyb =           TH1F('yb', ' ',nb, YYMIN, YYMAX)
    xylP2 =         TProfile2D('xyl', ' ',nb2, XXMIN, XXMAX, nb2, YYMIN, YYMAX, FRMIN, FRMAX)
    xylP =          TProfile('ylp', ' ',nb2, XXMIN, XXMAX, YYMIN, YYMAX)
    xyl =           TH1F('xl', ' ',nb, XXMIN, XXMAX)
    xyrP2 =         TProfile2D('xyr', ' ',nb2, XXMIN, XXMAX, nb2, YYMIN, YYMAX, FRMIN, FRMAX)
    xyrP =          TProfile('yrp', ' ',nb2, XXMIN, XXMAX, YYMIN, YYMAX)
    xyr =           TH1F('xr', ' ',nb, XXMIN, XXMAX)
    xsigmaH =       TH2F('xsigma', ' ',nb2, XXMIN, XXMAX, nb2, SMIN, SMAX)
    ysigmaH =       TH2F('ysigma', ' ',nb2, YYMIN, YYMAX, nb2, SMIN, SMAX)
    xfluxH =        TH2F('xflux', ' ',nb2, XXMIN, XXMAX, nb2, FMIN, FMAX)
    yfluxH =        TH2F('yflux', ' ',nb2, YYMIN, YYMAX, nb2, FMIN, FMAX)
    xthetaH =       TH2F('xtheta', ' ',nb2, XXMIN, XXMAX, nb2, THMIN, THMAX)
    ythetaH =       TH2F('ytheta', ' ',nb2, YYMIN, YYMAX, nb2, THMIN, THMAX)
    xellipH =       TH2F('xellip', ' ',nb2, XXMIN, XXMAX, nb2, EMIN, EMAX)
    yellipH =       TH2F('yellip', ' ',nb2, YYMIN, YYMAX, nb2, EMIN, EMAX)

# theta correlations
    thetasigmaH =   TH2F('thetasigma', ' ',nb2, THMIN, THMAX, nb2, SMIN, SMAX)
    thetafluxH =    TH2F('thetaflux', ' ',nb2, THMIN, THMAX, nb2, FMIN, FMAX)
    thetaellipH =   TH2F('thetaellip', ' ',nb2, THMIN, THMAX, nb2, EMIN, EMAX)
    thetag1H =      TH2F('thetag1', ' ',nb2, THMIN, THMAX, nb2, GMIN, GMAX)
    thetag2H =      TH2F('thetag2', ' ',nb2, THMIN, THMAX, nb2, GMIN, GMAX)

# sigma correlations
    sigmafluxH =    TH2F('sigmaflux', ' ',nb2, SMIN, SMAX, nb2, FMIN, FMAX)
    sigmaellipH =   TH2F('sigmaellip', ' ',nb2, SMIN, SMAX, nb2, EMIN, EMAX)
    sigmag1H =      TH2F('sigmag1', ' ',nb2, SMIN, SMAX, nb2, GMIN, GMAX)
    sigmag2H =      TH2F('sigmag2', ' ',nb2, SMIN, SMAX, nb2, GMIN, GMAX)

# flux correlations
    fluxellipH =    TH2F('fluxellip', ' ',nb2, FMIN, FMAX, nb2, EMIN, EMAX)
    fluxg1H =       TH2F('fluxg1', ' ',nb2, FMIN, FMAX, nb2, GMIN, GMAX)
    fluxg2H =       TH2F('fluxg2', ' ',nb2, FMIN, FMAX, nb2, GMIN, GMAX)

# all other correlations
    ellipg1H =      TH2F('ellipg1', ' ',nb2, EMIN, EMAX, nb2, GMIN, GMAX)
    ellipg2H =      TH2F('ellipg2', ' ',nb2, EMIN, EMAX, nb2, GMIN, GMAX)
    g1g2H =         TH2F('g1g2', ' ',nb2, GMIN, GMAX, nb2, GMIN, GMAX)

# fill all histograms
#    from __builtin__ import len

    print 'entering the fill loop'
    print len(xcoords), len(eFlux)
    for j in range(0, len(xcoords)):
#    for j in range(0, 1970000):
        Nfilled = Nfilled + 1

# select hits with one x-ray
        if Flux[j] > FMAX or Flux[j] < FMIN: continue        
        Nsinglehit = Nsinglehit + 1 

# select the area
#        if xcoords[j] > XMAX or xcoords < XMIN: continue
#        if ycoords[j] > YMAX or xcoords < YMIN: continue
        Nsections = Nsections + 1
             
# require reasonable fit errors    
        if eG1[j] > eGMAX or eG2[j] > eGMAX or eSigma[j] > eSMAX: continue
#        if eXX[j] > 0.1 or eYY[j] > 0.1: continue
        Nerrors = Nerrors + 1

# require ellipticity
#        if Ellip[j] > 0.1: continue       
        Nellip = Nellip + 1
        
# require corners
#        if XX[j] > XXMINC and XX[j] < XXMAXC: continue
#        if YY[j] > YYMINC and YY[j] < YYMAXC: continue
        Ngeom = Ngeom + 1

        Nselected = Nselected + 1

        xH.Fill(xcoords[j])
        yH.Fill(ycoords[j])
        xminH.Fill(xcoords[j])
        yminH.Fill(ycoords[j])
        xmaxH.Fill(xcoords[j])
        ymaxH.Fill(ycoords[j])
        xpixH.Fill(XX[j])
        ypixH.Fill(YY[j])
        eyH.Fill(eYY[j])
        exH.Fill(eXX[j])
        chi2H.Fill(Chi2[j])
        g1H.Fill(G1[j])
        g2H.Fill(G2[j])
        sigmaH.Fill(Sigma[j])
        fluxH.Fill(Flux[j])
        eg1H.Fill(eG1[j])
        eg2H.Fill(eG2[j])
        esigmaH.Fill(eSigma[j])
        efluxH.Fill(eFlux[j])
        thetaH.Fill(Theta[j])
        ellipH.Fill(Ellip[j])

        xyfullH.Fill(xcoords[j], ycoords[j], 1.)
        xyfullellH.Fill(xcoords[j], ycoords[j], Ellip[j])
        xyfullsigH.Fill(xcoords[j], ycoords[j], Sigma[j])
        xyfullg1P.Fill(xcoords[j], ycoords[j], G1[j], 1.)
        xyfullg2P.Fill(xcoords[j], ycoords[j], G2[j], 1.)
        xyfullsigP.Fill(xcoords[j], ycoords[j], Sigma[j], 1.)
        xyfulltheP.Fill(xcoords[j], ycoords[j], Theta[j], 1.)
        g1chi2H.Fill(G1[j], Chi2[j], 1.)
        g2chi2H.Fill(G2[j], Chi2[j], 1.)
        sigmachi2H.Fill(Sigma[j], Chi2[j], 1.)
        fluxchi2H.Fill(Flux[j], Chi2[j], 1.)
        thetachi2H.Fill(Theta[j], Chi2[j], 1.)
        ellipchi2H.Fill(Ellip[j], Chi2[j], 1.)

        xminsigmaH.Fill(xcoords[j], Sigma[j], 1.)
        xmaxsigmaH.Fill(xcoords[j], Sigma[j], 1.)
        yminsigmaH.Fill(ycoords[j], Sigma[j], 1.)
        ymaxsigmaH.Fill(ycoords[j], Sigma[j], 1.)
        xminfluxH.Fill(xcoords[j], Flux[j], 1.)
        xmaxfluxH.Fill(xcoords[j], Flux[j], 1.)
        yminfluxH.Fill(ycoords[j], Flux[j], 1.)
        ymaxfluxH.Fill(ycoords[j], Flux[j], 1.)
        xminthetaH.Fill(xcoords[j], Theta[j], 1.)
        xmaxthetaH.Fill(xcoords[j], Theta[j], 1.)
        yminthetaH.Fill(ycoords[j], Theta[j], 1.)
        ymaxthetaH.Fill(ycoords[j], Theta[j], 1.)
        xminellipH.Fill(xcoords[j], Ellip[j], 1.)
        xmaxellipH.Fill(xcoords[j], Ellip[j], 1.)
        yminellipH.Fill(ycoords[j], Ellip[j], 1.)
        ymaxellipH.Fill(ycoords[j], Ellip[j], 1.)
        xming1H.Fill(xcoords[j], G1[j], 1.)
        xmaxg1H.Fill(xcoords[j], G1[j], 1.)
        yming1H.Fill(ycoords[j], G1[j], 1.)
        ymaxg1H.Fill(ycoords[j], G1[j], 1.)
        xming2H.Fill(xcoords[j], G2[j], 1.)
        xmaxg2H.Fill(xcoords[j], G2[j], 1.)
        yming2H.Fill(ycoords[j], G2[j], 1.)
        ymaxg2H.Fill(ycoords[j], G2[j], 1.)

        xminsigmaP.Fill(xcoords[j], Sigma[j], 1.)
        xmaxsigmaP.Fill(xcoords[j], Sigma[j], 1.)
        yminsigmaP.Fill(ycoords[j], Sigma[j], 1.)
        ymaxsigmaP.Fill(ycoords[j], Sigma[j], 1.)
        xminfluxP.Fill(xcoords[j], Flux[j], 1.)
        xmaxfluxP.Fill(xcoords[j], Flux[j], 1.)
        yminfluxP.Fill(ycoords[j], Flux[j], 1.)
        ymaxfluxP.Fill(ycoords[j], Flux[j], 1.)
        xminthetaP.Fill(xcoords[j], Theta[j], 1.)
        xmaxthetaP.Fill(xcoords[j], Theta[j], 1.)
        yminthetaP.Fill(ycoords[j], Theta[j], 1.)
        ymaxthetaP.Fill(ycoords[j], Theta[j], 1.)
        xminellipP.Fill(xcoords[j], Ellip[j], 1.)
        xmaxellipP.Fill(xcoords[j], Ellip[j], 1.)
        yminellipP.Fill(ycoords[j], Ellip[j], 1.)
        ymaxellipP.Fill(ycoords[j], Ellip[j], 1.)
        xming1P.Fill(xcoords[j], G1[j], 1.)
        xmaxg1P.Fill(xcoords[j], G1[j], 1.)
        yming1P.Fill(ycoords[j], G1[j], 1.)
        ymaxg1P.Fill(ycoords[j], G1[j], 1.)
        xming2P.Fill(xcoords[j], G2[j], 1.)
        xmaxg2P.Fill(xcoords[j], G2[j], 1.)
        yming2P.Fill(ycoords[j], G2[j], 1.)
        ymaxg2P.Fill(ycoords[j], G2[j], 1.)

        xmidg1P.Fill(xcoords[j], G1[j], 1.)
        ymidg1P.Fill(ycoords[j], G1[j], 1.)
        xmidg2P.Fill(xcoords[j], G2[j], 1.)
        ymidg2P.Fill(ycoords[j], G2[j], 1.)

        xyH.Fill(XX[j], YY[j], 1.)
        xycH.Fill(XX[j], YY[j], Stamp_c[j]/Flux[j])
        xycP.Fill(XX[j], YY[j], Stamp_c[j]/Flux[j], 1.)
        xytP2.Fill(XX[j], YY[j], Stamp_t[j]/Flux[j], 1.)
        xybP2.Fill(XX[j], YY[j], Stamp_b[j]/Flux[j], 1.)
        xylP2.Fill(XX[j], YY[j], Stamp_l[j]/Flux[j], 1.)
        xyrP2.Fill(XX[j], YY[j], Stamp_r[j]/Flux[j], 1.)

        xyt.Fill(YY[j], Stamp_t[j]/Flux[j])
        xyb.Fill(YY[j], Stamp_b[j]/Flux[j])
        xyl.Fill(XX[j], Stamp_l[j]/Flux[j])
        xyr.Fill(XX[j], Stamp_r[j]/Flux[j])
        xytP.Fill(YY[j], Stamp_t[j]/Flux[j], 1.)
        xybP.Fill(YY[j], Stamp_b[j]/Flux[j], 1.)
        xylP.Fill(XX[j], Stamp_l[j]/Flux[j], 1.)
        xyrP.Fill(XX[j], Stamp_r[j]/Flux[j], 1.)

        xsigmaH.Fill(XX[j], Sigma[j], 1.)
        ysigmaH.Fill(YY[j], Sigma[j], 1.)
        xfluxH.Fill(XX[j], Flux[j], 1.)
        yfluxH.Fill(YY[j], Flux[j], 1.)
        xthetaH.Fill(XX[j], Theta[j], 1.)
        ythetaH.Fill(YY[j], Theta[j], 1.)
        xellipH.Fill(XX[j], Ellip[j], 1.)
        yellipH.Fill(YY[j], Ellip[j], 1.)

        thetasigmaH.Fill(Theta[j], Sigma[j], 1.)
        thetafluxH.Fill(Theta[j], Flux[j], 1.)
        thetaellipH.Fill(Theta[j], Ellip[j], 1.)
        thetag1H.Fill(Theta[j], G1[j], 1.)
        thetag2H.Fill(Theta[j], G2[j], 1.)

        sigmafluxH.Fill(Sigma[j], Flux[j], 1.)
        sigmaellipH.Fill(Sigma[j], Ellip[j], 1.)
        sigmag1H.Fill(Sigma[j], G1[j], 1.)
        sigmag2H.Fill(Sigma[j], G2[j], 1.)

        fluxellipH.Fill(Flux[j], Ellip[j], 1.)
        fluxg1H.Fill(Flux[j], G1[j], 1.)
        fluxg2H.Fill(Flux[j], G2[j], 1.)

        ellipg1H.Fill(Ellip[j], G1[j], 1.)
        ellipg2H.Fill(Ellip[j], G2[j], 1.)
        g1g2H.Fill(G1[j], G2[j], 1.)

        xco.append(xcoords[j])
        yco.append(ycoords[j])
        xve.append(xvectors[j])
        yve.append(yvectors[j])       

        if Nmax > 0 and Nfilled == Nmax: break

# deal with titles    
#    xH.GetXaxis().SetTitle('x')
#    yH.GetXaxis().SetTitle('y')
#    xminH.GetXaxis().SetTitle('x')
#    yminH.GetXaxis().SetTitle('y')
#    xmaxH.GetXaxis().SetTitle('x')
#    ymaxH.GetXaxis().SetTitle('y')
#    xpixH.GetXaxis().SetTitle('pixel x')
#    ypixH.GetXaxis().SetTitle('y')
#    exH.GetXaxis().SetTitle('error x')
#    eyH.GetXaxis().SetTitle('error y')
# need to finish titles

# draw and save histograms
    can1, can2, can3, can4 = 500, 200, 700, 500

    canvas = TCanvas('canvas', 'canvas', can1, can2, can3, can4)
#    canvas.Divide(1, 2, 0, 0)
#    canvas.cd(1)
#    xH.Draw()
#    canvas.cd(2)
#    yH.Draw("same")

    xH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/x.pdf')
    yH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/y.pdf')
    xminH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/xmin.pdf')
    yminH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/ymin.pdf')
    xmaxH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/xmax.pdf')
    ymaxH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/ymax.pdf')
    xpixH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/xpix.pdf')
    ypixH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/ypix.pdf')
    exH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/ex.pdf')
    eyH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/ey.pdf')
    chi2H.Draw()
    canvas.SaveAs('/home/mmmerlin/output/chi2.pdf')
    g1H.Draw()
    canvas.SaveAs('/home/mmmerlin/output/g1.pdf')
    g2H.Draw()
    canvas.SaveAs('/home/mmmerlin/output/g2.pdf')
    sigmaH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/sigma.pdf')
    fluxH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/flux.pdf')
    eg1H.Draw()
    canvas.SaveAs('/home/mmmerlin/output/eg1.pdf')
    eg2H.Draw()
    canvas.SaveAs('/home/mmmerlin/output/eg2.pdf')
    esigmaH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/esigma.pdf')
    efluxH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/eflux.pdf')
    thetaH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/theta.pdf')
    ellipH.Draw()
    canvas.SaveAs('/home/mmmerlin/output/ellip.pdf')

# 2D histograms
    gStyle.SetOptStat(0)
    style = 'colz'
    
    can1, can2 = 400, 300
    canvas = TCanvas( 'canvas', 'canvas', can1, can2) #create canvas

    xyfullH.Draw(style)
    canvas.SaveAs('/home/mmmerlin/output/xyfull.pdf')
    xyfullellH.Draw(style)
    canvas.SaveAs('/home/mmmerlin/output/xyfullell.pdf')
    xyfullsigH.Draw(style)
    canvas.SaveAs('/home/mmmerlin/output/xyfullsig.pdf')
    xyfullg1P.Draw(style)
    canvas.SaveAs('/home/mmmerlin/output/xyfullg1p.pdf')
    xyfullg2P.Draw(style)
    canvas.SaveAs('/home/mmmerlin/output/xyfullg2p.pdf')
    xyfullsigP.Draw(style)
    canvas.SaveAs('/home/mmmerlin/output/xyfullsigp.pdf')
    xyfulltheP.Draw(style)
    canvas.SaveAs('/home/mmmerlin/output/xyfullthep.pdf')

    g1chi2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/g1chi2.pdf')
    g2chi2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/g2chi2.pdf')
    sigmachi2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/sigmachi2.pdf')
    fluxchi2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/fluxchi2.pdf')
    thetachi2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/thetachi2.pdf')
    ellipchi2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ellipchi2.pdf')

    xminsigmaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xminsigma.pdf')
    xmaxsigmaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xmaxsigma.pdf')
    yminsigmaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/yminsigma.pdf')
    ymaxsigmaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ymaxsigma.pdf')
    xminfluxH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xminflux.pdf')
    xmaxfluxH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xmaxflux.pdf')
    yminfluxH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/yminflux.pdf')
    ymaxfluxH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ymaxflux.pdf')
    xminthetaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xmintheta.pdf')
    xmaxthetaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xmaxtheta.pdf')
    yminthetaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ymintheta.pdf')
    ymaxthetaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ymaxtheta.pdf')
    xminellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xminellip.pdf')
    xmaxellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xmaxellip.pdf')
    yminellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/yminellip.pdf')
    ymaxellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ymaxellip.pdf')
    xming1H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xming1.pdf')
    xmaxg1H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xmaxg1.pdf')
    yming1H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/yming1.pdf')
    ymaxg1H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ymaxg1.pdf')
    xming2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xming2.pdf')
    xmaxg2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xmaxg2.pdf')
    yming2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/yming2.pdf')
    ymaxg2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ymaxg2.pdf')

#    xminsigmaP.SetMarkerStyle(20)
    xminsigmaP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xminsigmap.pdf')
    xmaxsigmaP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xmaxsigmap.pdf')
    yminsigmaP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/yminsigmap.pdf')
    ymaxsigmaP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/ymaxsigmap.pdf')
    xminfluxP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xminfluxp.pdf')
    xmaxfluxP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xmaxfluxp.pdf')
    yminfluxP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/yminfluxp.pdf')
    ymaxfluxP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/ymaxfluxp.pdf')
    xminthetaP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xminthetap.pdf')
    xmaxthetaP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xmaxthetap.pdf')
    yminthetaP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/yminthetap.pdf')
    ymaxthetaP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/ymaxthetap.pdf')
    xminellipP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xminellipp.pdf')
    xmaxellipP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xmaxellipp.pdf')
    yminellipP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/yminellipp.pdf')
    ymaxellipP.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/ymaxellipp.pdf')
    xming1P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xming1p.pdf')
    xmaxg1P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xmaxg1p.pdf')
    yming1P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/yming1p.pdf')
    ymaxg1P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/ymaxg1p.pdf')
    xming2P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xming2p.pdf')
    xmaxg2P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xmaxg2p.pdf')
    yming2P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/yming2p.pdf')
    ymaxg2P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/ymaxg2p.pdf')

    xmidg1P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xmidg1p.pdf')
    ymidg1P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/ymidg1p.pdf')
    xmidg2P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/xmidg2p.pdf')
    ymidg2P.Draw("EP")
    canvas.SaveAs('/home/mmmerlin/output/ymidg2p.pdf')

    xyH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xy.pdf')
    xycH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xyc.pdf')
    xycH.Draw("lego2")
    canvas.SaveAs('/home/mmmerlin/output/xyclego.pdf')
    xycP.Draw("e1")
    canvas.SaveAs('/home/mmmerlin/output/xycp.pdf')
    xytP2.Draw("e1")
    canvas.SaveAs('/home/mmmerlin/output/xyt.pdf')
    xybP2.Draw("e1")
    canvas.SaveAs('/home/mmmerlin/output/xyb.pdf')
    xylP2.Draw("e1")
    canvas.SaveAs('/home/mmmerlin/output/xyl.pdf')
    xyrP2.Draw("e1")
    canvas.SaveAs('/home/mmmerlin/output/xyr.pdf')
    xycP.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xycp.pdf')
    xytP2.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xytc.pdf')
    xybP2.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xybc.pdf')
    xylP2.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xylc.pdf')
    xyrP2.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xyrc.pdf')
    xyt.Draw()
    canvas.SaveAs('/home/mmmerlin/output/t.pdf')
    xyb.Draw()
    canvas.SaveAs('/home/mmmerlin/output/b.pdf')
    xyl.Draw()
    canvas.SaveAs('/home/mmmerlin/output/l.pdf')
    xyr.Draw()
    canvas.SaveAs('/home/mmmerlin/output/r.pdf')
    xytP.Draw()
    canvas.SaveAs('/home/mmmerlin/output/xytp.pdf')
    xybP.Draw()
    canvas.SaveAs('/home/mmmerlin/output/xybp.pdf')
    xylP.Draw()
    canvas.SaveAs('/home/mmmerlin/output/xylp.pdf')
    xyrP.Draw()
    canvas.SaveAs('/home/mmmerlin/output/xyrp.pdf')
    xsigmaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xsigma.pdf')
    ysigmaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ysigma.pdf')
    xfluxH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xflux.pdf')
    yfluxH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/yflux.pdf')
    xthetaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xtheta.pdf')
    ythetaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ytheta.pdf')
    xellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/xellip.pdf')
    yellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/yellip.pdf')

    thetasigmaH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/thetasigma.pdf')
    thetafluxH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/thetaflux.pdf')
    thetaellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/thetaellip.pdf')
    thetag1H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/thetag1.pdf')
    thetag2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/thetag2.pdf')

    sigmafluxH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/sigmaflux.pdf')
    sigmaellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/sigmaellip.pdf')
    sigmag1H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/sigmag1.pdf')
    sigmag2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/sigmag2.pdf')

    fluxellipH.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/fluxellip.pdf')
    fluxg1H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/fluxg1.pdf')
    fluxg2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/fluxg2.pdf')

    ellipg1H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ellipg1.pdf')
    ellipg2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/ellipg2.pdf')
    g1g2H.Draw("colz")
    canvas.SaveAs('/home/mmmerlin/output/g1g2.pdf')

# plot ellipticity map
    pl.figure()
    dm_abt = pl.quiver(xco, yco, xve, yve, angles='uv', units='xy', pivot='middle', width=0.5, headwidth=0 , scale=1./200. )
    pl.axis([XMIN, XMAX, YMIN, YMAX])
    pl.title('ellipticity map')
#    pl.show(block = False)
    pl.show()
    
    print 'Total, Fitted, Filled, SingleHit, Sections, Errors, Ellipticity, Corners, Selected'
    print Ntotal, Nfitted, Nfilled, Nsinglehit, Nsections, Nerrors, Nellip, Ngeom, Nselected
    print '\n***End code***'
    exit()
