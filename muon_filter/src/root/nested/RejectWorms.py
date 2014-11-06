def RejectWorms(mi, fpSet):
    filteredImage = mi
    new_fpSet = fpSet
    
    

    footPrints = new_fpSet.getFootprints()
    new_fpSet.setMask(filteredImage.getMask(), "DETECTED")
    print footPrints.size(), "footPrint(s) found\n"
    
    
    
    
    fpSet.setMask(filteredImage.getMask(), "DETECTED")

    
    return filteredImage, new_fpSet

def doLSR(data):
    '''Perform straight line fit using perpendicular offset Least Squares Regression on image
    Returning a, b for f(x) = ax + b with R2 giving the R^2 correlation coefficient'''
    
    a,b,R2 = 0,0,0
    
    for x in xrange(data.shape[0]):
        for y in xrange(data.shape[1]):
#            do stuff
            print
    
    
    
    
        
    
    return a,b,R2

def getRegionData(image, bbox, border = 0):
    data = image.getImage().getArray()
    
    xmin = bbox.getMinX() - border
    xmax = bbox.getMaxX() + border
    ymin = bbox.getMinY() - border
    ymax = bbox.getMaxY() + border
    
    return data[ymin:ymax,xmin:xmax]


def ShowImage(image, mask = None, ROI_Bbox = None, border = 0):
    import pylab as plt
    import numpy as np  
    
    
    if ROI_Bbox is not None:
        imdata = getRegionData(image, bbox = ROI_Bbox, border = border)
    else:    
        imdata = image.getImage().getArray()
    
    
#    fig, ax = plt.subplots()
#    p = ax.pcolor(imdata)
#    cb = fig.colorbar(p, ax=ax)
#    pl.arrow(xmin +3, ymin +3, 4, 4)


    
        
    
    
    fitdata = np.zeros(shape = imdata.shape)
    
    for x in xrange(fitdata.shape[0]):
        for y in xrange(fitdata.shape[1]):
            if (imdata[x,y] > 2500):
                fitdata[x,y] = 2500
    



    plt.imshow(imdata * (fitdata/fitdata.max()), alpha = 1, cmap = 'gray', interpolation='none')
#    plt.imshow(fitdata, alpha = 0.1, cmap = 'gray', interpolation='none')


#    fitdata_plot.set_cmap('gray')
#    fitdata_plot.set_interpolation('none')
#    fitdata_plot.set_alpha(0.2)
    
    
    
#    dataplot = plt.imshow(imdata, alpha = 0.6)
#    dataplot.set_cmap('gray')
#    dataplot.set_interpolation('none')
#    dataplot.set_alpha(1)
    
    
#    fig.colorbar(dataplot)
    
    
    plt.show()
#    pl.show(block = False)
    
    return
    
    
    