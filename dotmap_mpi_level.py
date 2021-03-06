# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 16:22:34 2015

@author: Alex Cao, University of Michigan
"""
import pandas as pd
import time
import createtile as tile
from osgeo import ogr
from shapely.wkb import loads
from shapely.geometry import Point
from random import uniform
from globalmaptiles import GlobalMercator
import os
from mpi4py import MPI # line 1

#%% Phase 1: Generate People
# timing
t0 = time.time()

# specify zoom level limits
lowerzoom = 3
upperzoom = 13

shortcut = False

if not shortcut:
    merc = GlobalMercator()
    
    # specify shapefile
    state_fips = 50
    shapefile = os.path.join("Vermont","tabblock2010_{}_pophu.shp".format(state_fips))
               
    # open the shapefile
    ds = ogr.Open(shapefile)
    
    # obtain the first (and only) layer in the shapefile
    lyr = ds.GetLayerByIndex(0)
    lyr.ResetReading()
    print("{} census blocks".format(len(lyr)) )
    
    # iterate through every feature (Census Block Polygon) in the layer,
    # obtain the population count, and create a point for each person within
    # that feature and append/extend to a list
    population = []
    for j, feat in enumerate(lyr, start=1):   
        # print a progress read-out for every 10000 features  
#        if j % 11000 == 0:
#            t2 = time.time()
#            print("{:.1f} | {:.0f}% complete".format(t2-t0,float(j)/len(lyr)*100))        
        # obtain the OGR polygon object from the feature
        geom = feat.GetGeometryRef()    
        if geom is None:
            continue   
        # convert the OGR Polygon into a Shapely Polygon    
        poly = loads(geom.ExportToWkb())    
        if poly is None:
            continue                
        # obtain the "boundary box" of extreme points of the polygon
        bbox = poly.bounds    
        if not bbox:
            continue    
        # get bounding box for polygon
        leftmost,bottommost,rightmost,topmost = bbox
        # obtain population in each census block
        pop = feat.GetFieldAsInteger("POP10")
        people = []
        for i in range(pop):
            # choose a random longitude and latitude within the boundary box
            # and within the polygon of the census block            
            while True:                
                samplepoint = Point(uniform(leftmost, rightmost),uniform(bottommost, topmost))
                if poly.contains(samplepoint):
                    break
            # convert the longitude and latitude coordinates to meters and
            # a tile reference
            x, y = merc.LatLonToMeters(samplepoint.y, samplepoint.x)
            tx,ty = merc.MetersToTile(x, y, upperzoom)            
            # create a quadkey for each point object
            quadkey = merc.QuadTree(tx, ty, upperzoom)
            people.append((x,y,quadkey))
        population.extend(people)

    # convert list to dataframe
    data = pd.DataFrame(population, columns=['x','y','quadkey'])
    
else:
    data = pd.read_csv("Vermont_pop.csv", header=0, usecols=[1,2,3])

t2 = time.time()
print("{} people took {:.1f}s".format(data.shape[0],t2-t0))

#%% Phase 2: Generate Tile

# create a range of descending zoomlevels 
zoomlevels = range(upperzoom,lowerzoom,-1)
# track number of tiles
N = 0
# line 2
comm = MPI.COMM_WORLD
# loop through zoom levels
for j in range(comm.rank, len(zoomlevels), comm.size): # line 3
    level = zoomlevels[j]
    # grab correct quadkey string based on zoom level
    data.loc[:,'quadkey'] = data['quadkey'].map(lambda x: x[0:level])
    # group dataframe by quadkey
    groups =  data.groupby('quadkey')
    # get list of unique quadkeys and length
    quadtree = data['quadkey'].unique()
    n = len(quadtree)
    # loop through quadkeys
    for i in range(n):
        quadkey = quadtree[i]
        # generate tile function
        tile.generate_tile(groups.get_group(quadkey), quadkey, level)
    # keep count of tiles
    N += n

# line 4
comm.Barrier()

t3 = time.time()
print("Creating {} png files took {:.1f}s".format(N,t3-t2))
print("Total time {:.1f}".format(t3-t0))
