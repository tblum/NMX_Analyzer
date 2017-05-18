import sys
import numpy as np
from H5file import H5file
import matplotlib.pyplot as plt

maxval = 1.0
nbins = 200

if __name__ == '__main__':
    h5file = H5file(sys.argv[1])
    bins = np.linspace(0.0, maxval, nbins)
    bins[-1] += maxval 
    hist = np.zeros(nbins, dtype='int32')
    maxv = 0.0
    nval = 0
    for e in xrange(h5file.nevents):
        (x,y) = h5file.compressedEvent(e)
        if x is None or y is None:
            continue
        values = np.array((x[2]+y[2]))
        values *= -1.0
#        values *= values
        hist += np.bincount(np.digitize(values,bins),minlength=nbins)
        maxv = max(maxv, max(values))
        nval += len(values)
    print (h5file.nevents, nval, maxv)
    bins[-1] -= maxval 
    plt.bar(bins, hist, width=1.0/nbins, color="blue", log=True)
    
    plt.show()
