import numpy as np
cimport numpy as np

DTYPE = np.int
ctypedef np.int_t DTYPE_t


def Correlate(np.ndarray[DTYPE_t, ndim=1] histarray, np.ndarray[DTYPE_t, ndim=1] timecodes, int correlmin):
    assert histarray.dtype == DTYPE and timecodes.dtype == DTYPE
    cdef int arraylength, i, j, index
   
    arraylength = len(timecodes)
    
    for i in range(arraylength):
        for j in range(i+1,arraylength):
            index = (timecodes[i]-timecodes[j]) - correlmin
            histarray[index] += 1
    
    return 0
    