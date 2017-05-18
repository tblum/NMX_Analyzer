from __future__ import print_function
import sys
import numpy as np
import matplotlib.pyplot as plt
from H5file import H5file

MIN = 1200
MAX = 3000
SCALE = 5

class Display:

    strip = 64
    strip_max = 512
    pedestal = False
    h5file = None
    
    def __init__(self, h5file):
        self.figure, self.axes = plt.subplots(1)
        self.figure.canvas.mpl_connect('key_press_event', self.keyEvent)
        self.h5file = h5file
        self.showStrip()
        plt.show()

    def showStrip(self):
        plt.cla()
        if self.pedestal:
            cut = self.h5file.pedestal['cut'][self.strip/256][self.strip%256]
        else:
            cut = MIN
        self.figure.canvas.set_window_title(str(self.strip).zfill(3))
        bins = np.arange(cut,MAX,SCALE)
        mymax = MAX+(cut-MAX)%SCALE
        print (cut,mymax)
        hist = self.h5file.aggregate['hist'][self.strip][cut:mymax]
        hist = hist.reshape(len(hist)/SCALE,SCALE)
        hist = np.sum(hist,axis=1)
        self.axes.bar(bins, hist, width=SCALE, color="blue", log=True)
        plt.draw()
                
    def keyEvent(self, event):
        if event.key == 'right':
            self.strip = (self.strip + 1) % self.strip_max
        if event.key == 'left':
            self.strip = (self.strip - 1) % self.strip_max
        if event.key == 'up':
            self.strip = (self.strip + 10) % self.strip_max
        if event.key == 'down':
            self.strip = (self.strip - 10) % self.strip_max
        if event.key == 'pageup':
            self.strip = (self.strip + 100) % self.strip_max
        if event.key == 'pagedown':
            self.strip = (self.strip - 100) % self.strip_max
        if event.key == 'p':
            self.pedestal = not self.pedestal
        self.showStrip()


if __name__ == '__main__':
    plt.rcParams['keymap.xscale'] = ''
    plt.rcParams['keymap.yscale'] = ''
    plt.rcParams['keymap.pan'] = ''
    plt.rcParams['keymap.save'] = ''
    plt.rcParams['keymap.fullscreen'] = ''
    
    h5file = H5file(sys.argv[1])
    h5file.readPedestal()
    h5file.readAggregate()
    display = Display(h5file)

