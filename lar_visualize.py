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

colorbar_tile = 'scaled energy'

for counter, label in enumerate(labels):
    if evt_plotted > max_evts:
        break
    targ = labels[counter]
    pstring = '{}'.format(targ)
    print(pstring)
    fig = pylab.figure(figsize=(12, 8))
    gs = pylab.GridSpec(1, 2)
    for i in range(2):
        ax = pylab.subplot(gs[i])
        ax.axis('on')
        ax.xaxis.set_major_locator(pylab.NullLocator())
        ax.yaxis.set_major_locator(pylab.NullLocator())

        minv = -500
        cmap = 'inferno'
        im = ax.imshow(data[counter][i], cmap=pylab.get_cmap(cmap),
                       interpolation='nearest', vmin=minv, vmax=3000)
        #pylab.show()
        cbar = pylab.colorbar(im, fraction=0.04)
        cbar.set_label(colorbar_tile, size=9)
        cbar.ax.tick_params(labelsize=6)
        pylab.title("lar", fontsize=12)
        pylab.xlabel("wire", fontsize=10)
        pylab.ylabel("tick", fontsize=10)

    figname = 'evt_%s_%d_%f.pdf' % \
        (filename, counter, labels[counter])
    pylab.savefig(figname)
    pylab.close()
    evt_plotted += 1
