from __future__ import print_function
import h5py
import numpy as np
from  scipy.sparse import csr_matrix

class H5file:

    pedestal = {}
    aggregate = {}
    nevents = 0 
    images = None
    ebye = None
    
    def __init__(self, file_name):
        self.file_name = file_name
        try:
            self.file = h5py.File(self.file_name, 'r')
        except IOError:
            print ('Could not open: ', self.file_name)
            return False
        try:
            self.images = self.file['images']
            self.nevents = self.images.attrs['nevents']
            return
        except KeyError:
            self.images = None
        try:
            self.ebye = self.file['ebye']
            self.nevents = self.file['global']['nevents'][0]
            return
        except KeyError:
            self.ebye = None
                        
    def readPedestal(self):
        try:
            self.pedestal['avg'] = self.file['pedestal/average'][:]
            self.pedestal['cut'] = self.file['pedestal/cut-off'][:]
        except KeyError:
            print ('The file ', self.file_name, 'does not contain a pedestal')
            self.pedestal['avg'] = np.zeros((2,256),dtype=np.uint16) + 1220
            self.pedestal['cut'] = np.zeros((2,256),dtype=np.uint16) + 1220

    def readAggregate(self):
        try:
            self.aggregate['avg'] = self.file['aggregate/average'][:]
            self.aggregate['cut'] = self.file['aggregate/cut-off'][:]
            self.aggregate['hist'] = self.file['aggregate/histogram'][:]
        except KeyError:
            print ('The file ', self.file_name, 'does not contain an aggregate')
            return False
        
    @staticmethod
    # Convert Carstens format to dense format  
    def cfToFull(data): # (x(strip,timebin,value[0:1]),y(strip,timebin,value[0:1])) 
        event = np.empty((2,30,256),dtype=np.uint16)
        i = 0
        for dim in data:
            strip = np.array(dim[0]) + 3 # Carsten only has 250 strips 
            timebin = dim[1]
            value = np.array(dim[2]) * (-1800.0) 
            event[i] = csr_matrix((value,(timebin,strip)), shape=(30,256)).todense()
            i += 1
        event += 1200
        return event

        return (int(x*2.5+125.0+3.0),int(y*2.5+125.0+3.0))

    def read(self, i, key):
        event_str = str(i).zfill(6)
        try:
            entry = self.ebye[event_str][key][:]
        except KeyError:
            print ('The file ', self.file_name, 'does not contain', key , event_str)
            raise 
        return entry

    def readEntry(self, i, astype=None):
        return self.astype(self.read(i,'entry'),astype)        

    def readOrigin(self, i, astype=None):
        o = self.astype(self.read(i,'origin'),astype)
        assert len(o) == 1
        return o[0]

    @staticmethod
    def points(eo): # for entry or origin
        x = eo['x']
        y = eo['y']
        return zip(x,y)
    
    @staticmethod
    def strips(eo): # for entry or origin
        return map(lambda (x,y): (int(x*2.5)+128,int(y*2.5)+128), H5file.points(eo))

    @staticmethod
    def astype(eo, rtype): # for entry or origin
        if rtype is None:
            return eo
        elif rtype == 'points':
            return H5file.points(eo)
        elif rtype == 'strips':
            return H5file.strips(eo)
        else:
            print ('Unknown returntype', rtype)
            raise TypeError('Unknown returntype', rtype)

        
    def readEvent(self, i):
        event_str = str(i).zfill(6)
        if self.images:
            try:
                event = self.images[event_str][:]
            except KeyError:
                print ('The file ', self.file_name, 'does not contain events', event_str)
                raise
        elif self.ebye:
            event = self.cfToFull(self.compressedEvent(i))
        else:
            return False 
        return event

    def compressedEvent(self,i):
        event_str = str(i).zfill(6)
        if self.ebye:
            try:
                xdata = self.ebye[event_str]['signal_data_x'][:]
                ydata = self.ebye[event_str]['signal_data_y'][:]
            except KeyError:
                print ('The file ', self.file_name, 'does not contain compressed event', event_str)
                raise
        else:
            raise TypeError('The file ', self.file_name, 'does not contain compressed events')
        return (zip(*xdata),zip(*ydata))
