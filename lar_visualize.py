#!/usr/bin/env python
"""
Usage:
    python lar_visualize.py [file name] [opt: max # of evts, def==10]
The default file name is: "./nukecc_fuel.hdf5".
Note, one can, if one wants, when working with `Fuel`d data sets, do:
    from fuel.datasets import H5PYDataset
    train_set = H5PYDataset('./mydat_fuel.hdf5', which_sets=('train',))
    handle = train_set.open()
    nexamp = train_set.num_examples
    data = train_set.get_data(handle, slice(0, nexamp))
    # ...work with the data
    train_set.close(handle)
...but we don't do that here. (Just use h5py to cut any requirement of Fuel
to look at the dsets.)
"""
import pylab
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt

max_evts = 10
evt_plotted = 0

if '-h' in sys.argv or '--help' in sys.argv:
    print(__doc__)
    sys.exit(1)

filename = './photon_1-1462232439.h5'
if len(sys.argv) > 1:
    filename = sys.argv[1]
if len(sys.argv) > 2:
    max_evts = int(sys.argv[2])


# def decode_eventid(eventid):
#     """
#     assume encoding from fuel_up_nukecc.py, etc.
#     """
#     eventid = str(eventid)
#     phys_evt = eventid[-2:]
#     eventid = eventid[:-2]
#     gate = eventid[-4:]
#     eventid = eventid[:-4]
#     subrun = eventid[-4:]
#     eventid = eventid[:-4]
#     run = eventid
#     return (run, subrun, gate, phys_evt)


f = h5py.File(filename, 'r')

have_times = False
# look for x, u, v data hits
try:
    data_shp = pylab.shape(f['features'])
except KeyError:
    print("'features' does not exist.")
    data_shp = None
    sys.exit()

data_shp = (max_evts, data_shp[1], data_shp[2], data_shp[3])
data = pylab.zeros(data_shp, dtype='float32')
data = f["features"][:max_evts].astype('float32')

labels_shp = (max_evts,)
labels = pylab.zeros(labels_shp, dtype='float32')

try:
    labels = f['Eng'][:max_evts].astype('float32')
except KeyError:
    labels_shp = None

f.close()

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

shp = list(data.shape)
shp[-1] = shp[-1] / 4   # downsample by 4
simpledata=np.zeros(shp)

for event_n in range(data.shape[0]):
    y=0
    for x in my_range(0, 4096, 4):
        if x == 0:
            print 'checking shapes for event =', event_n
            print '  simpledata slice shape =', simpledata[event_n,:,:,y:(y+1)].shape
            print '  mean(data) slice shape =', np.nanmean(data[event_n,:,:,x:(x+4)], axis=2).shape
        simpledata[event_n,:,:,y:(y+1)] = np.nanmean(data[event_n,:,:,x:(x+4)], axis=2).reshape(2,240,1)
        y+=1

colorbar_tile = 'scaled energy'

def plot_event(img, minv= 0, maxv=1000):
    fig = plt.figure(figsize=(12, 8))
    gs = plt.GridSpec(1, 2)
    for i in range(2):
        ax = plt.subplot(gs[i])
        ax.axis('on')
        ax.xaxis.set_major_locator(plt.NullLocator())
        ax.yaxis.set_major_locator(plt.NullLocator())

        cmap = 'inferno'
        im = ax.imshow(img[i], cmap=pylab.get_cmap(cmap),
                       interpolation='nearest', vmin=minv, vmax=maxv)
        cbar = plt.colorbar(im, fraction=0.04)
        cbar.set_label(colorbar_tile, size=9)
        cbar.ax.tick_params(labelsize=6)
        plt.title("lar", fontsize=12)
        plt.xlabel("wire", fontsize=10)
        plt.ylabel("tick", fontsize=10)

for counter, label in enumerate(labels):
    if evt_plotted > max_evts:
        break
    targ = labels[counter]
    pstring = '{}'.format(targ)
    print(pstring)

    plot_event(simpledata[counter])

    figname = 'evt_%s_%d_%f.pdf' % \
        (filename, counter, labels[counter])
    pylab.savefig(figname)
    pylab.close()
    evt_plotted += 1
