# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 16:22:34 2015

@author: Alex Cao, University of Michigan
"""

from mpi4py import MPI
import pandas as pd
import time
import createtile as tile
import numpy as np

#%% Phase 1: Generate People
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# timing
t0 = time.time()

# specify zoom level limits
lowerzoom = 3
upperzoom = 13

#%% Phase 2: Generate Tile

# convert list to dataframe
data = pd.read_csv("Vermont_pop.csv", header=0, usecols=[1,2,3])
t2 = time.time()
if rank == 0:
    print("Read csv {:.1f}s".format(t2-t0))
# create a range of descending zoomlevels 
zoomlevels = range(upperzoom,lowerzoom,-1)
# mpi4py requires that we pass numpy objects
N = np.zeros(1)
# loop through zoom levels
for j in range(len(zoomlevels)):
    level = zoomlevels[j]
    # grab correct quadkey string based on zoom level
    data.loc[:,'quadkey'] = data['quadkey'].map(lambda x: x[0:level])
    # group dataframe by quadkey
    groups =  data.groupby('quadkey')
    # get list of unique quadkeys and length
    quadtree = data['quadkey'].unique()
    n = len(quadtree)
    count = 0
    # loop through quadkeys
    for i in range(rank, n, comm.size):
        quadkey = quadtree[i]
        # generate tile function
        tile.generate_tile(groups.get_group(quadkey), quadkey, level)
        count += 1        
    # keep count of tiles
    N += count

# mpi4py requires that we pass numpy objects
total = np.zeros(1)
# reduce call
comm.Reduce(N, total, op=MPI.SUM, root=0)
t3 = time.time()
if rank == 0:
    print("Creating {:.0f} png files took {:.1f}s".format(total[0],t3-t2))

