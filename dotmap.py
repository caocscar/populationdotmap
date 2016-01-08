# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 16:22:34 2015

@author: Alex Cao, University of Michigan
"""

from PIL import Image, ImageDraw
import os
import globalmaptiles as gmt
import time
import pandas as pd

def transparent(level):
    if level == 4 or level == 5:
        return 153
    elif level == 6 or level == 7:
        return 179
    elif level == 8 or level == 9:
        return 204
    elif level == 10 or level == 11:
        return 230
    elif level == 12 or level == 13:
        return 255
    else:
        return 0.0 
      

def generate_tile(quadkey, df):   
    width = int(512*4)
    bkgrd = 255
    img = Image.new('RGBA', (width,width), (bkgrd,bkgrd,bkgrd,255) )
    draw = ImageDraw.Draw(img)  

    google_tile = proj.QuadKeyToGoogleTile(quadkey)
    tms_tile = proj.GoogleToTMSTile(google_tile[0],google_tile[1],level)
    bounds = proj.TileBounds(tms_tile[0],tms_tile[1],level)

    tile_ll = bounds[0]/A
    tile_bb = bounds[1]/A
    tile_rr = bounds[2]/A
    tile_tt = bounds[3]/A
    
    xscale = width/(tile_rr - tile_ll)
    yscale = width/(tile_tt - tile_bb)
    scale = min(xscale, yscale)
     
    px = scale*(df['x']/A - tile_ll)
    py = -scale*(df['y']/A - tile_tt)
    people = list(set(zip(px,py)))
    draw.point(people, fill=(255,0,0,transparent(level)))
    
    img = img.resize((512,512),resample=Image.BICUBIC)
    filename = r"tile4/{}/{}/{}.png".format(level, google_tile[0], google_tile[1])
    try:
        img.save(filename,'PNG')
    except:                    
        os.makedirs(r"tile4/{}/{}".format(level, google_tile[0]))
        img.save(filename,'PNG')
   

#%%
t0 = time.time()
proj = gmt.GlobalMercator()    
A = 1000
n = 0
zoomlevel = range(4,14)

for level in zoomlevel:
    data = pd.read_csv('Vermont_pop.csv', header=0, usecols=[1,2,3])
    data.loc[:,'quadkey'] = data['quadkey'].map(lambda x: x[0:level])
    for quadkey, df in data.groupby('quadkey'):
        generate_tile(quadkey, df)
        n+=1
        if n%500 == 0:
            print(n)

t1 = time.time()
print("{} png files took {:.1f}s".format(n,t1-t0))


