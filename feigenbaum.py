# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 09:56:13 2022
Rev 1.0 - 09 Dec 22
    The program creates a Feigenbaum diagram. It can display (and save) this as 
    a plot. Alternatively, it can simply display the image (and save it) using 
    PIL.
@author: Owner
"""

from math import sin, cos
from matplotlib.pyplot import rcParams, savefig, subplots
from numpy import ones, uint8
from PIL import Image

class Feigenbaum():
    title = "Feigenbaum"
    
    def __init__(self, **kwargs):
        
        self.kStart = kwargs.setdefault("kStart", 1.6)
        self.kEnd = kwargs.setdefault("kEnd", 3.0)
        self.pMin = kwargs.setdefault("pMin", 0.0)
        self.pMax = kwargs.setdefault("pMax", 1.6)
        self.p0 = kwargs.setdefault("p0", 0.3)
        self.ignore = kwargs.setdefault("ignore", 20)
        self.maxIter = kwargs.setdefault("maxIter", 40)
        self.colour0 = kwargs.setdefault("colour0", [0xFF, 0x00, 0xF0])
        self.colour1 = kwargs.setdefault("colour1", [0x00, 0xF0, 0xFF])

    def plot(self, xSize=600, ySize=400, fname="images/tempplot.png", 
             savePlot=False):
        myArray = ones((ySize, xSize, 3), dtype=uint8)
        self.traverse_array(myArray, self.kStart, self.kEnd, 
                            self.pMin, self.pMax, xSize, ySize,
                            self.p0)

        #Create a figure of the right size with one axes that takes up the full 
        #figure
        px = 1/rcParams['figure.dpi']  #pixel in inches
        fig, ax = subplots(figsize=(xSize*px, ySize*px))
        #Start and end of scales form the extent...
        extent = [self.kStart, self.kEnd, self.pMin, self.pMax]
        #Draw the image, wherever you show your plots
        ax.imshow(myArray, interpolation='nearest', extent=extent)
        ax.set_aspect('auto')
        #Save the image
        if savePlot == True:
            savefig(fname)

    def image(self, xSize=800, ySize=400, fname="images/tempfimage.png", 
              saveImage=False):
        myArray = ones((ySize, xSize, 3), dtype=uint8)
        self.traverse_array(myArray, self.kStart, self.kEnd, 
                            self.pMin, self.pMax, xSize, ySize,
                            self.p0)

        #Display the result using PIL
        im = Image.fromarray(myArray)
        im.show()
        if saveImage == True:
            im.save(fname)

    def function(self, p, k):
        return p + k*p*(1-p)
    
    def iterate(self, array, xPixel, pMin, pMax, ySize, p0, k):
        p = p0
        for i in range(self.maxIter):
            p = self.function(p, k)
            #set pixel for this p
            try:
                yPixel = int(ySize*(p-pMin)/(pMax-pMin))
            except OverflowError:
                print("iteration", i, " k:", k, " p:", p)
                break
            if i < self.ignore:
                continue
            if (yPixel > -1) and (yPixel < ySize):
                if i % 2 == 0:
                    colour = self.colour0
                else:
                    colour = self.colour1
                array[(ySize -1 -yPixel), xPixel] = colour
            else:
                print("iteration", i, " k:", k, " p out of bounds:", p)
                break
        #end_for_i
            
    def traverse_array(self, array, kStart, kEnd, pMin, pMax, xSize, ySize,
                       p0):
        #Make start less than end
        if kEnd < kStart:
            kStart, kEnd = kEnd, kStart
        if pMax < pMin:
            pMin, pMax = pMax, pMin
    
        #Determine increase per pixel
        kIncr = (kEnd - kStart)/xSize

        k = kStart
        for xPixel in range(xSize):
            self.iterate(array, xPixel, pMin, pMax, 
                                          ySize, p0, k)
            k += kIncr
        #end_for_x


class Feig2(Feigenbaum):
    
    def function(self, p, k):
        return k*p*p*(1-p)


class Feig3(Feigenbaum):

    def function(self, p, k):
        return k*sin(p)*(cos(p))
    
    
if __name__=="__main__":
    tc = 3
    if tc==0:
        f=Feigenbaum()
        f.plot(500, 350, "tempplot2.png", True)
        print("Now show the plot; look at plot window?")
    if tc==1:
        f=Feigenbaum(ignore=0, maxIter=50)
        f.image()
    if tc==2:
        f=Feig2(ignore=5, maxIter=60, kStart=4.5, kEnd=7.5, pMin=-2)
        f.plot()
    if tc==3:
        f=Feig3()
        f.plot()