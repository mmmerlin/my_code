import cPickle as pickle

# import Erin's package
import ngmix
# import the DMstack stuff 
import lsst.afw.math        as math
import lsst.afw.table       as afwTable
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
from os.path import expanduser, isfile, isdir

from image_assembly import AssembleImage
from fit_constraints import ExamplePrior
from imprint import imprint


import time

if __name__ == '__main__':
    print "Running Andrei's Fe55 cluster finder code"
    print time.ctime()

# running modes
    Print   = False
            
# break the loop after Nmax hits if Nmax > 0
    Nmax = -1
    FileLimit = 999999

# define some arrays
    xcoords, ycoords, xvectors, yvectors, npixels, clusterI = [], [], [], [], [], []
    majors, minors, thetas = [], [], []
    XX, YY, G1, G2, T, Flux, Theta, Size = [], [], [], [], [], [], [], []
    eXX, eYY, eG1, eG2, eT, eFlux, Chi2 = [], [], [], [], [], [], []
    xco, yco, xve, yve = [], [], [], []
    Sigma, eSigma, Ellip = [], [], []
    Stamp_c, Stamp_t, Stamp_b, Stamp_l, Stamp_r = [], [], [], [], []

    pickles = []

# zero counters
    Ntotal  =   0
    Nfitted =   0

# set up some paths for filenames
    home_dir = expanduser("~")
    metadata_file = home_dir + '/useful/herring_bone.fits'

    input_path_Fe55data = '/mnt/hgfs/VMShared/Data/fe55/device112-04_march13_750_files/'
    filenames = listdir(input_path_Fe55data)

    pickle_dir = '/mnt/hgfs/VMShared/Data/fe55/device112-04_march13_750_files/pickles/'
    
# loop over raw data to produce and save results
    for Fe55file in filenames:
        if (FileLimit <= len(filenames)) and (Fe55file == filenames[FileLimit]): break
        if Fe55file.find('.DS_') != -1: continue
        if isdir(Fe55file) == True: continue # skip bias dir
        input_file = input_path_Fe55data + Fe55file    
        print input_file 
        
# Merlin's magic to mosaic correctly
        gains = [3.79509352,3.851916292,3.834108654,3.876996568,3.835078189,3.856641255,3.832781099,3.856389413,3.758698179,3.808504386,3.742609872,3.810088368,3.775578121,3.809432767,3.780270026,3.79986126]

        image = AssembleImage(input_file, metadata_file, subtract_background = True, gain_correction_list= gains)
        maskedImage = afwImg.MaskedImageF(image)
        
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
        thresholdValue = mean + stdevclip * 10.0        
#            thresholdValue = stdevclip * 10.0        
        npixMin = 2
        grow = 2
        isotropic = True
        
# do the footprint finding
        threshold = afwDetect.Threshold(thresholdValue, afwDetect.Threshold.VALUE)
        footPrintSet = afwDetect.FootprintSet(maskedImage, threshold, "DETECTED", npixMin)
        footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
    
        footPrints = footPrintSet.getFootprints()
        footPrintSet.setMask(maskedImage.getMask(), "DETECTED")
        print footPrints.size(), "footPrint(s) found\n"
    
# loop over found footprints
        footprint = afwDetect.Footprint()    
        for footprint in footPrints:               
            Ntotal = Ntotal + 1
# calculate shapes using vanilla DM
            quadshape = footprint.getShape()
            axesshape = Ellipses.Axes(quadshape)
            A = axesshape.getA()
            B = axesshape.getB()
            theta = axesshape.getTheta()
            centroid_x, centroid_y = footprint.getCentroid()
            npix = footprint.getNpix()
#            print "\n npix = %s" % npix

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
            
# fit with 16x16 sub-pixel sampling
            nsub=16
    
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
            prior=None

            fitter=ngmix.fitting.LMSimple(obs, model, nsub=nsub, lm_pars=lm_pars, prior=prior)
                    
# make a guess for [cen1,cen2,g1,g2,T,flux] where T is 2*sigma**2
            cen1 = centroid_x - xmin + 0.1 * (np.random.random()-0.5)
            cen2 = centroid_y - ymin + 0.1 * (np.random.random()-0.5)
            g1=0.
            g2=0.
            T_guess = 0.32 # = 2*(0.4)**2
            flux_guess=intens
#                guess=np.array( [cen1,cen2,g1,g2,log10(T_guess),log10(flux_guess)] )
            guess=np.array( [cen1,cen2,g1,g2,T_guess,flux_guess] )
    
# run the fitter
            fitter.run_lm(guess)
            result=fitter.get_result()

            if Print: print "event", Ntotal
           
            if result['flags'] != 0:
                print " *****  something went wrong ******"
            else:
                Nfitted = Nfitted + 1
    #            print("best fit parameters:",result['pars'])
    #            print("err on parameters:  ",result['pars_err'])
    
# also get the linear parameters
#                    lin_res=fitter.get_lin_result()
                if Print:
                    print "best fit lin pars:",result['pars']
                    print "err on lin pars:  ",result['pars_err']
                    print "chi2:  ",result['chi2per']
    
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
                if Ntotal % 100 == 0: 
                    print "Analysed %s clusters of %s (%s%%) in %s"%(Ntotal, footPrints.size(), round((100 * float(Ntotal)/float(footPrints.size())),2), Fe55file)                    

            if Nmax > 0 and Ntotal == Nmax: break
# end of footprint loop, still in the file loop

# calculate some additional things
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

# pickle all data in a file
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

        pickle_filename = pickle_dir + Fe55file +'.pickle'
        print pickle_filename    
        pickle.dump(pickles, open(pickle_filename, 'wb'), protocol = pickle.HIGHEST_PROTOCOL)

# zero arrays so they can be reused
        xcoords, ycoords, xvectors, yvectors, npixels, clusterI = [], [], [], [], [], []
        majors, minors, thetas = [], [], []
        XX, YY, G1, G2, T, Flux, Theta, Size = [], [], [], [], [], [], [], []
        eXX, eYY, eG1, eG2, eT, eFlux, Chi2 = [], [], [], [], [], [], []
        xco, yco, xve, yve = [], [], [], []
        Sigma, eSigma, Ellip = [], [], []
        Stamp_c, Stamp_t, Stamp_b, Stamp_l, Stamp_r = [], [], [], [], []
        pickles = []

        if Nmax > 0 and Ntotal == Nmax: break

# file loop ends here, we have all we need to fill and save histos

    print 'Total & Fitted'
    print Ntotal, Nfitted
    print '\n***End code***'
    exit()
