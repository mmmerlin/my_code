import sys

def imprint(im, stream=sys.stdout, fmt=None):
    if len(im.shape) != 2:
        raise ValueError("image must be 2-dimensional")

    if fmt is None:
        if im.dtype.char in ['f','d']:
            fmt = '%+e'
        else:
            maxint = im.max()
            minint = im.min()
            l = max( len(str(maxint)), len(str(minint)) )
            fmt = '%'+str(l)+'d'

    nrow = im.shape[0]
    ncol = im.shape[1]

    for row in xrange(nrow):
        for col in xrange(ncol):
            stream.write(fmt % im[row,col] )
            if col < (ncol-1):
                stream.write(" ")
        stream.write("\n")
        
