def TimepixToExposure(filename):
    from lsst.afw.image import makeImageFromArray
    import numpy as np
    
    
    data = np.loadtxt(filename)
    x = data[:, 0] 
    y = data[:, 1] 
    t = data[:, 2]

    my_array = np.zeros((256,256), dtype = np.int32)

    for pointnum in range(len(x)):
        my_array[x[pointnum],y[pointnum]] = t[pointnum]
    
    
    my_image = makeImageFromArray(my_array)
    
    
    return my_image