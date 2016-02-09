# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 10:44:53 2016

@author: caoa
"""

from PIL import Image, ImageDraw
import os
import globalmaptiles as gmt

# determine alpha level of point(s)
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

# create png file given quadkey
def generate_tile(df, quadkey, level):
    tile_size = 256   
    width = int(tile_size*4)
    bkgrd = 255
    img = Image.new('RGBA', (width,width), (bkgrd,bkgrd,bkgrd,255) )
    draw = ImageDraw.Draw(img)  

    proj = gmt.GlobalMercator()
    google_tile = proj.QuadKeyToGoogleTile(quadkey)
    tms_tile = proj.GoogleToTMSTile(google_tile[0],google_tile[1],level)
    bounds = proj.TileBounds(tms_tile[0],tms_tile[1],level)

    A = 1000
    tile_ll = bounds[0]/A
    tile_bb = bounds[1]/A
    tile_rr = bounds[2]/A
    tile_tt = bounds[3]/A
    
    xscale = width/(tile_rr - tile_ll)
    yscale = width/(tile_tt - tile_bb)
    scale = min(xscale, yscale)
     
    px = (scale*(df['x']/A - tile_ll)).astype(int)
    py = (-scale*(df['y']/A - tile_tt)).astype(int)
    draw.point(zip(px,py), fill=(255,0,0,transparent(level)))
    
    img = img.resize((tile_size,tile_size),resample=Image.BICUBIC)
    filename = r"tile4/{}/{}/{}.png".format(level, google_tile[0], google_tile[1])
    try:
        img.save(filename,'PNG')
    except:                    
        os.makedirs(r"tile4/{}/{}".format(level, google_tile[0]))
        img.save(filename,'PNG')
        
        