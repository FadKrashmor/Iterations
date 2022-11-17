# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 17:57:49 2022
Rev 1.1: 17 Nov 22 adds protection for both x and y = 0
Rev 1.2: 17 Nov 22 palette defined separately and imported avoiding 
                   editing this file for each change.
@author: Owner

The program creates an image of the basins of attraction for the cube 
roots of one,using Newton's method. 
The image is shown to screen and saved with name tempnimage.png 
in the current directory.
"""
from numpy import ones, uint8
from PIL import Image
from scipy import nextafter
import palette5

def belongs_to_root(x, y, limit):
    #given (x,y), is the point close to one of the cube roots of one?
    #returns 0 if not; 1, 2 or 3 depending on which root is close
    if ((x+0.5)**2 + (y+0.8660254)**2) < limit:
        return 1
    elif ((x+0.5)**2 + (y-0.8660254)**2) < limit:
        return 2
    elif ((x-1)**2 + y**2) < limit:
        return 3
    else:
        return 0

def iteration(x, y, maxIter):
    # Find cube roots of 1 using Newton's method
    # Return:
    #   0: root not yet determined
    #   1, 2 or 3 for each respective root
    #   4: we started at a root
    #
    LIMIT = 0.0025 #Terminate iteration when closer than this arbitrary limit
    if belongs_to_root(x, y, LIMIT/10):#Comment this out if 
        return 4                       #you don't want the root marked
    rootFound = 0
    for i in range(maxIter):
        if (x==0) and (y==0):
            x = nextafter(0,1)
            continue
        x_sq, y_sq, d_sq = x*x, y*y, (x*x + y*y)
        temp = 3*(d_sq*d_sq)
        x_new = 2*x/3 + (x_sq - y_sq)/temp
        y_new = 2*y/3 - 2*x*y/temp
        rootFound = belongs_to_root(x_new, y_new, LIMIT)
        if rootFound:
            break
        x = x_new
        y = y_new
    #end_for_i
    return rootFound

#MAIN
palette = palette5.palette

MAX_ITER = 16
aspect = 3/4
xStart = -1.4
xEnd = 1.4
yStart = -1.05
yEnd = yStart + (xEnd - xStart)*aspect
imageWidth = 800
imageHeight = int(imageWidth*aspect)
dx = (xEnd - xStart)/imageWidth
dy = (yEnd - yStart)/imageHeight

iArray = ones((imageHeight, imageWidth, 3), dtype=uint8)

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
except:
    print("Couldn't save file")

            
            
