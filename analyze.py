from __future__ import print_function
import numpy as np
from  scipy.sparse import csr_matrix

def addBorder(event,border):
    shape = np.array(event.shape)
    shape[1] += 2
    eb = np.empty(shape)
    eb[:,1:-1,:] = event
    eb[:,0,:] = border
    eb[:,-1,:] = border
    return eb

def findAllPeaks(event):
    return (event[:,1:-1,:] > event[:,0:-2,:]) & (event[:,1:-1,:] >= event[:,2:,:])

def deadTime(peaks,time=200,bintime=25):
    binDT = time/bintime
    for tb in xrange(peaks.shape[1]-1):
        to = tb + binDT + 1
        to = peaks.shape[1] if to >= peaks.shape[1] else to
        np.logical_and(peaks[:,tb+1:to], np.logical_not(peaks[:,tb,None]),peaks[:,tb+1:to])
    return peaks
    
def findGlobalPeaks(event):
    xtb = np.argmax(event[0],axis=0)
    ytb = np.argmax(event[1],axis=0)
    strips = np.arange(len(xtb))
    mask  = (xtb > 0)
    x = csr_matrix((np.ones(np.sum(mask)),(xtb[mask],strips[mask])),shape=(30,256)).todense()
    mask  = (ytb > 0)
    y = csr_matrix((np.ones(np.sum(mask)),(ytb[mask],strips[mask])),shape=(30,256)).todense()
    return np.array((x,y))

def findPeaks(event):
    return findGlobalPeaks(event)

def _lastTimebin(peaks):
    time = peaks[0]
    strips = peaks[1]
    mask = time == time[-1]
    invmask = np.invert(mask)
    return (time[-1], np.trim_zeros(mask*strips),
            np.array((np.trim_zeros(invmask*time), np.trim_zeros(invmask*strips))) )

def findEntryMatchingTimebin(peaks, span=5):
    try:
        x = np.array(np.nonzero(peaks[0])) + 1
        y = np.array(np.nonzero(peaks[1])) + 1
        (xtb, xstrips, xrest) = _lastTimebin(x)
        (ytb, ystrips, yrest) = _lastTimebin(y)
        if (abs(xtb-ytb)>1): # Make sure that last timebin in X and Y are close
            return None
        if (xstrips.max() - xstrips.min() > span or # Dont allow great spans 
            ystrips.max() - ystrips.min() > span):
            return None
        (xtb2, xstrips2, _) = _lastTimebin(xrest)
        (ytb2, ystrips2, _) = _lastTimebin(yrest)
        if (xstrips2.max() - xstrips2.min() > span or
            ystrips2.max() - ystrips2.min() > span):
            return None
        xstrip = xstrips[-1] if np.average(xstrips) > np.average(xstrips2) else  xstrips[0]
        ystrip = ystrips[-1] if np.average(ystrips) > np.average(ystrips2) else  ystrips[0]
        return ((xtb-1,xstrip-1),(ytb-1,ystrip-1))
    except:
        return None

def findEntrySimple(peaks, span=4):
    try:
        x = np.nonzero(peaks[0])
        y = np.nonzero(peaks[1])
        (xtb, xstrips, xrest) = _lastTimebin(x)
        (ytb, ystrips, yrest) = _lastTimebin(y)
        if (xstrips[-1] - xstrips[0] > span) or (ystrips[-1] - ystrips[0] > span):
            return []
        res = (xtb,xstrips[len(xstrips)/2]),(ytb,ystrips[len(ystrips)/2])
        return [res]
    except:
        return []

def findEntry(peaks):
    return findEntrySimple(peaks)

