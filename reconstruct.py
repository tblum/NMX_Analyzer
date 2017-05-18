#!/usr/bin/python

from __future__ import print_function
import sys
import numpy as np
import matplotlib.pyplot as plt
from H5file import H5file
import analyze
import math
import pickle

XSTRIPS = 256
YSTRIPS = 256

def dist((tx,ty),(x,y)):
    return math.sqrt((tx-x)**2 + (ty-y)**2)

class Reconstruct:

    h5file = None
    images = {}
    stats = {}
    analysis = {}
    
    def __init__(self, h5file):
        self.h5file = h5file
        self.h5file.readPedestal()

    def getEvent(self, i):
        event = self.h5file.readEvent(i).astype(np.int16)
        event = analyze.addBorder(event,self.h5file.pedestal['avg'])
        # Apply pedistal
        event -= self.h5file.pedestal['cut'][:,None,:] 
        event *= event > 0
        return event

    @staticmethod
    def strips(tb_strips):
        return map(lambda (x,y): (x[1],y[1]), tb_strips)
    
    def simpleAll(self,i):
        event = self.getEvent(i)
        ep = analyze.findEntrySimple(analyze.findAllPeaks(event))
        return self.strips(ep)
    
    def simple200(self,i):
        event = self.getEvent(i)
        ep = analyze.findEntrySimple(analyze.deadTime(analyze.findAllPeaks(event),time=200))
        return self.strips(ep)

    def nolow200(self,i):
        event = self.getEvent(i)
        if event.max() < 300:
            return []
        ep = analyze.findEntrySimple(analyze.deadTime(analyze.findAllPeaks(event),time=200))
        return self.strips(ep)
    
    def simple400(self,i):
        event = self.getEvent(i)
        ep = analyze.findEntrySimple(analyze.deadTime(analyze.findAllPeaks(event),time=400))
        return self.strips(ep)
         
    def entry(self,i):
        return self.h5file.readEntry(i,astype='strips')
    
    def setup(self, methods):
        for key in methods.keys():
            self.images[key] = np.zeros((XSTRIPS,YSTRIPS),dtype=np.uint32)
            self.stats[key] = []
            self.analysis[key] = []
        
    def reconstruct(self, nevents=None):
#        methods = {'entry': self.entry,
#                   'all peaks': self.simpleAll,
#                   'dead time 200': self.simple200,
#                   'dead time 400': self.simple400
#        }
        methods = {'dead time 200': self.simple200,
                   'No low 200': self.nolow200
        }
        self.methods = methods
        self.setup(methods)
        if nevents is None:
            nevents = self.h5file.nevents
        self.nevents = nevents
        for i in xrange(nevents):
            try:
                origin = self.h5file.readOrigin(i,astype='strips')
            except:
                origin = None
            for key in methods.keys():
                try:
                    strips = methods[key](i)
                except:
                    print ('No result', i)
                    continue
                for s in strips:
                    self.images[key][s] += 1
                    if origin is not None:
                        self.stats[key].append(dist(s,origin))
            print ('{:5.1f}%'.format(float(i)*100/float(nevents)),end='\r')
            sys.stdout.flush()

    def analyse(self, nevents=None):
#        methods = {'entry': self.entry,
#                   'all peaks': self.simpleAll,
#                   'dead time 200': self.simple200,
#                   'dead time 400': self.simple400
#        }
        methods = {'entry': self.entry,
                   'dead time 200': self.simple200,
                   'No low 200': self.nolow200
        }
        self.methods = methods
        self.setup(methods)
        if nevents is None:
            nevents = self.h5file.nevents
        self.nevents = nevents
        for i in xrange(nevents):
            try:
                origin = self.h5file.readOrigin(i,astype='strips')
            except:
                continue
            for key in methods.keys():
                try:
                    strips = methods[key](i)
                except:
                    continue
                for s in strips:
                    self.analysis[key].append((origin,s))
            print ('{:5.1f}%'.format(float(i)*100/float(nevents)),end='\r')
            sys.stdout.flush()


    def save(self, filename):
        pfile = open(filename+'.pkl', 'wb')
        pickle.dump(self.analysis, pfile)
        pfile.close()



if __name__ == '__main__':
    plt.rcParams['keymap.xscale'] = ''
    plt.rcParams['keymap.yscale'] = ''
    plt.rcParams['keymap.pan'] = ''
    plt.rcParams['keymap.save'] = ''
    plt.rcParams['keymap.fullscreen'] = ''
    
    h5file = H5file(sys.argv[1])
    R = Reconstruct(h5file)
    R.reconstruct(1000)
#    R.analyse()
#    R.save('analysis_nolow')
#    exit
    for key in R.stats.keys():
        print ('Found', len(R.stats[key]), 'entry points in for', key)
    print ('Out of', R.nevents, 'data sets')

    
    nkey = 0
    bins = np.linspace(0, 185, 100)
    for key in R.stats.keys():
        nkey += 1
        plt.subplot(2,len( R.stats.keys()),nkey)
        plt.title(key)
        plt.imshow(R.images[key].T,interpolation='none')
        plt.subplot(2,len( R.stats.keys()),nkey+len( R.stats.keys()))
        plt.title(key)
        plt.hist(R.stats[key], bins)
        plt.yscale('log', nonposy='clip')
        
    plt.show()
