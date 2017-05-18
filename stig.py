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

nevents = 95089




if __name__ == '__main__':

    analisys = pickle.load(open(sys.argv[1], 'rb'))
    images = {}
    euclid_dist = {}
    x_dist = {}
    y_dist = {} 
    
    for key in analisys.keys():
        print ('Found', len(analisys[key]), 'entry points in for', key, ':')
        image = images[key] = np.zeros((XSTRIPS,YSTRIPS),dtype=np.uint32)
        ed = euclid_dist[key] = []
        xd = x_dist[key] = []
        yd = y_dist[key] = []
        for ev in analisys[key]:
            o = ev[0]
            s = ev[1]
            image[s] += 1
            ed.append(dist(o,s)/2.5)
            xd.append((o[0]-s[0])/2.5)
            yd.append((o[1]-s[1])/2.5)
        print ('\tEuclidean distance: (mean)', np.mean(ed), '(var)', np.var(ed), '(std)', np.std(ed))
        print ('\tDistance X: (mean)', np.mean(xd), '(var)', np.var(xd), '(std)', np.std(xd))
        print ('\tDistance Y: (mean)', np.mean(yd), '(var)', np.var(yd), '(std)', np.std(yd))
    print ('Out of', nevents, 'data sets')
    exit 
    
    
    plt.figure(1)
    nkey = 0
    bins = np.linspace(0, 185/2.5, 100)
    for key in images.keys():
        nkey += 1
        plt.subplot(2,len( images.keys()),nkey)
        plt.title(key)
        image = np.log(images[key]+1)
        plt.imshow(image.T,interpolation='none')
        plt.subplot(2,len(images.keys()),nkey+len(images.keys()))
        plt.title(key + " dist")
        plt.hist(euclid_dist[key], bins)
        plt.yscale('log', nonposy='clip')
        plt.ylim((10,100000))

    plt.figure(2)
    nkey = 0
    bins = np.linspace(-128/2.5, 128/2.5, 100)
    for key in images.keys():
        nkey += 1
        plt.subplot(2,len( images.keys()),nkey)
        plt.title(key + " X dist")
        plt.hist(x_dist[key], bins)
        plt.yscale('log', nonposy='clip')
        plt.ylim((10,100000))
        plt.subplot(2,len(images.keys()),nkey+len(images.keys()))
        plt.title(key + "Y dist")
        plt.hist(y_dist[key], bins)
        plt.yscale('log', nonposy='clip')
        plt.ylim((10,100000))
    plt.show()
