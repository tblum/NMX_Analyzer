#!/usr/bin/python

from __future__ import print_function
import sys
import numpy as np
from H5file import H5file
import operator
import matplotlib.pyplot as plt


def encEnt(d,k):
    try:
        d[k] +=1
    except KeyError:
        d[k] = 1

def engEnt(d,k,v):
    try:
        d[k].append(v)
    except KeyError:
        d[k] = [v]
    
def printStats(name,d,n):
    s = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
    print (name)
    t = 0
    for (k,v) in s:
        t += v
        print ('        {:5.1f}% ({:5d}): {}'.format((float(v)*100.0/n),v,k))
    print ('   sum: {:5.1f}% ({:5d})\n'.format((float(t)*100.0/n),t))


def printSNR(name, stats):
    print (name)
    gamma = np.array(stats[(22,)][0])
    if gamma[-1] == 0:
        gamma[-1] = 1
    bins = stats[(22,)][1]
    neutron = np.array(stats[(2112,)][0])
    rakkg = np.cumsum(gamma[::-1])
    rakkn = np.cumsum(neutron[::-1])
    res = np.empty((len(bins)-1,5),dtype=np.float)
    res[:,0] = bins[0:-1]
    res[:,1] = (rakkn/rakkn[-1])[::-1]
    res[:,2] = (rakkg/rakkg[-1])[::-1]
    res[:,3] = (rakkn/rakkg)[::-1] # S/N
    res[:,4] = neutron/gamma
    print (' Signal Nuetron   Gamma      S/N')
    for l in res:
        print ('{:7.0f}   {:5.1f}   {:5.1f}    {:5.2f}   {:5.2f}'.format(l[0],l[1]*100,l[2]*100,l[3],l[4]))

    
if __name__ == '__main__':
    entries = {}
    entry_pdg = {}
    parent_pdg = {}
    electron_parent = {}
    energy_parent = {}
    max_eng_par = {}
    h5file = H5file(sys.argv[1])
    for i in xrange(h5file.nevents):
    #for i in xrange(2000):
        try:
            entry = h5file.readEntry(i)
            ne = entry.shape[0]
            energy = (h5file.readEvent(i) - 1200).sum()
            max_eng = (h5file.readEvent(i) - 1200).max()
        except:
            continue
        encEnt(entries,ne)
        ep = entry['entry_pdg']
        pp = entry['parent_pdg']
        encEnt(entry_pdg,tuple(np.sort(ep)))
        encEnt(parent_pdg,tuple(np.sort(pp)))
        if ne < 3 and (ep==11).all():
            encEnt(electron_parent,tuple(np.sort(pp)))
            engEnt(energy_parent,tuple(np.sort(pp)),energy)
            engEnt(max_eng_par,tuple(np.sort(pp)),max_eng)
            
    printStats('Entries:',entries,h5file.nevents)
    printStats('Entry PDG:',entry_pdg,h5file.nevents)
    printStats('Parent PDG:',parent_pdg,h5file.nevents)
    printStats('1 or 2 Electron(s) Parent PDG:',electron_parent,h5file.nevents)
    plt.figure(1)
    plt.title('Total energy')
    total = {}
    bins = np.linspace(0, 150000, 101)
    bins[-1] *= 2 
    for k in energy_parent.keys():
        total[k] = plt.hist(energy_parent[k], bins, alpha=0.5, label=str(k))
    plt.legend(loc='upper right')
    plt.xlim((0,150000))
    printSNR("Total energy", total)
        
    plt.figure(2)
    plt.title('Max energy')
    maxx = {}
    bins = np.linspace(0, 2000, 101)
    bins[-1] *= 2 
    for k in max_eng_par.keys():
        maxx[k] = plt.hist(max_eng_par[k], bins, alpha=0.5, label=str(k))
    plt.legend(loc='upper right')
    plt.xlim((0,2000))
    printSNR("Max energy", maxx)
    print ("Events:",h5file.nevents)
    plt.show()



            
        
