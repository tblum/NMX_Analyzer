#!/usr/bin/python

from __future__ import print_function
import sys
import numpy as np
import matplotlib.pyplot as plt
from H5file import H5file
import analyze

class Display:

    evno = 0
    ped = None
    zero = False
    surface = False
    log = False
    peak = False
    dead = 0
    cor = 0
    diff = 0
    smooth = False
    timeMedian = False
    stripMedian = False
    inverse = False
    
    def __init__(self, h5file):
        self.figure, self.axes = plt.subplots(2)
        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        self.axes = np.append(self.axes,[plt.axes([0.85, 0.1, 0.075, 0.7])])
        self.figure.canvas.mpl_connect('key_press_event', self.keyEvent)
        self.figure.canvas.mpl_connect('button_press_event', self.mouseClick)
        self.h5file = h5file
        self.showEvent(0)
        plt.show()

    def addBorder(self, event):
        return analyze.addBorder(event,self.h5file.pedestal['avg'])
    
    def showEvent(self, i=None):
        if i is None:
            i = self.evno
        event = self.h5file.readEvent(i).astype(np.float32)
        
        if self.peak or self.smooth or self.diff > 0:
            event = self.addBorder(event)

        if not self.ped is None:
            event -= self.h5file.pedestal[self.ped][:,None,:] + self.cor

        if self.stripMedian:
            event -= np.median(event,axis=1)[:,None,:]

        if self.timeMedian:
            event -= np.median(event,axis=2)[:,:,None]

        if self.smooth:
            event[:,1:-1,:] = event[:,1:-1,:]*0.5 + event[:,0:-2,:]*0.25 + event[:,2:,:]*0.25
            
        for d in range(self.diff):
            event = event[:,1:,:] - event[:,:-1,:] 
        
        if self.zero:
            event *= event > 0

        if self.log:
            event = np.log(event+1)

        if self.peak:
            event = analyze.findAllPeaks(event)
            if self.dead > 0:
                event = analyze.deadTime(event,time=self.dead)
            #print (np.nonzero(event))
            entry = analyze.findEntry(event)
            if (entry):
                event[0][entry[0]] +=1
                event[1][entry[1]] +=1
            plt.rcParams['image.cmap'] = 'gray'
        else:
            plt.rcParams['image.cmap'] = 'jet'

        if self.inverse:
            event = -event
            
        min = np.min(event)
        max = np.max(event)
        for a in range(len(self.axes)):
            self.axes[a].cla()
        ex = np.sum(event[0])
        ey = np.sum(event[1])
        e = ex + ey
        self.figure.canvas.set_window_title(str(i).zfill(7))
        self.axes[0].title.set_text('X ' + "{:4.1f}%".format(ex/e*100.0))
        self.axes[1].title.set_text('Y ' + "{:4.1f}%".format(ey/e*100.0))
        self.axes[2].title.set_text(('none' if self.ped is None else self.ped) + ' + ' +
                                    str(self.cor) + ("\nzero" if self.zero else "") +
                                    ("\nlog" if self.log else "") +
                                    ("\nsmooth" if self.smooth else "") +
                                    ("\ntime median" if self.timeMedian else "") +
                                    ("\nstrip median" if self.stripMedian else "") +
                                    (("\ndiff " + str(self.diff)) if self.diff else "") 
        )
        im = self.axes[0].imshow(event[0], interpolation='none', aspect='auto', clim=(min,max))
        im = self.axes[1].imshow(event[1], interpolation='none', aspect='auto', clim=(min,max))
        plt.colorbar(im, cax=self.axes[2])
        plt.draw()

    def mouseClick(self, mev):
        (figx,figy) = self.figure.transFigure.inverted().transform((mev.x,mev.y))
        x = int(mev.xdata)
        y = int(mev.ydata)
        pic = self.addBorder(self.h5file.readEvent(self.evno))[int(figy < 0.5)] 
        print (pic[1:,int(mev.xdata)] - pic[:-1,int(mev.xdata)])
        print(x,y)
        
    def keyEvent(self, event):
#        print (event.key)
#        sys.stdout.flush()
        if event.key == 'right':
            self.evno += 1
        if event.key == 'left':
            self.evno -= 1
        if event.key == 'up':
            self.evno += 100
        if event.key == 'down':
            self.evno -= 100
        if event.key == 'pageup':
            self.evno += 10000
        if event.key == 'pagedown':
            self.evno -= 10000
        if event.key == 'c':
            self.ped = 'cut'
        if event.key == 'a':
            self.ped = 'avg'
        if event.key == 't':
            self.ped = 'test'
        if event.key == 'm':
            self.timeMedian = not self.timeMedian 
        if event.key == 'M':
            self.stripMedian = not self.stripMedian 
        if event.key == 'n':
            self.ped = None
        if event.key == 'z':
            self.zero = not self.zero
        if event.key == 'l':
            self.log = not self.log
        if event.key == 'p':
            self.peak = not self.peak
            self.dead = 0
        if event.key == '2':
            self.dead = 200
        if event.key == '4':
            self.dead = 400
        if event.key == 's':
            self.smooth = not self.smooth
        if event.key == 'd':
            self.diff += 1
        if event.key == 'D':
            self.diff = 0
        if event.key == 'i':
            self.inverse = not self.inverse
        if event.key == '+':
            self.cor += 1
        if event.key == '-':
            self.cor -= 1
        if event.key == '0':
            self.cor = 0
        if event.key == 'C':
            print (self.h5file.pedestal['cut'] - self.h5file.pedestal['avg'])
        self.showEvent()
        

        
if __name__ == '__main__':
    plt.rcParams['keymap.xscale'] = ''
    plt.rcParams['keymap.yscale'] = ''
    plt.rcParams['keymap.pan'] = ''
    plt.rcParams['keymap.save'] = ''
    plt.rcParams['keymap.fullscreen'] = ''
    
    h5file = H5file(sys.argv[1])
    h5file.readPedestal()
    display = Display(h5file)

    
