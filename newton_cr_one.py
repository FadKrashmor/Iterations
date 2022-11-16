# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 17:57:49 2022

@author: Owner

The program creates an image of the basins of attraction for the cube 
roots of one. Image is shown to screen and saved with name tempnimage.png 
in the current directory.
"""
import numpy as np
from PIL import Image

def belongs_to_root(x, y):
    #given (x,y), is the point close to one of the cube roots of one?
    #returns 0 if not; 1, 2 or 3 depending on which root is close
    CLOSE_SQ = 0.0025
    if ((x+0.5)**2 + (y+0.8660254)**2) < CLOSE_SQ:
        return 1
    elif ((x+0.5)**2 + (y-0.8660254)**2) < CLOSE_SQ:
        return 2
    elif ((x-1)**2 + y**2) < CLOSE_SQ:
        return 3
    else:
        return 0

def iteration(x, y, maxIter):
    # Find cube roots of 1 using Newton's method
    # return:
    #   0: root not yet determined
    #   1, 2 or 3 for each respective root
    #   4: (optionally) show roots, commented out
#    if belongs_to_root(x, y):
#        return 4
    for i in range(maxIter):
        x_sq, y_sq, d_sq = x*x, y*y, (x*x + y*y)
        temp = 3*(d_sq*d_sq)
        x_new = 2*x/3 + (x_sq - y_sq)/temp
        y_new = 2*y/3 - 2*x*y/temp
        rootFound = belongs_to_root(x_new, y_new)
        if rootFound:
            break
        x = x_new
        y = y_new
    #end_for_i
    return rootFound

#MAIN
palette = [(0xFF, 0xFF, 0xFF),
           (0xFF, 0xD8, 0x20), 
           (0x00, 0x10, 0xFF),
           (0xD0, 0x00, 0xA0),
           (0x03, 0x03, 0x03)]

MAX_ITER = 100
aspect = 3/4
xStart = -1.4
xEnd = 1.4
yStart = -1.05
yEnd = yStart + (xEnd - xStart)*aspect
imageWidth = 600
imageHeight = int(imageWidth*aspect)
dx = (xEnd - xStart)/imageWidth
dy = (yEnd - yStart)/imageHeight

iArray = np.ones((imageHeight, imageWidth, 3), dtype=np.uint8)

#Populate array with colours depending on the result of the iteration
currentX = xStart
for pixelX in range(imageWidth):
    currentY = yStart
    for pixelY in range(imageHeight):
        iArray[(imageHeight -1 -pixelY), pixelX] = \
            palette[iteration(currentX, currentY, MAX_ITER)]
        currentY += dy
    currentX += dx

#Image is complete    
image = Image.fromarray(iArray)
image.show()
try:
    image.save("tempnimage.png", format="PNG")
#    print("Palette: ", palette)
#    print("Range: ", xStart, xEnd, ";", yStart, yEnd)
except:
    print("Couldn't save file")

            
            
