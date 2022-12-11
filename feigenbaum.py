# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 09:56:13 2022
Rev 1.0 - 09 Dec 22
    The program creates a Feigenbaum diagram. It can display (and save) this as 
    a plot. Alternatively, it can simply display the image (and save it) using 
    PIL.
Rev 1.1 -11 Dec 22
    Better functional decomposition.
    Class FeigPtoFofP to display feigenbaum p to f(p).
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
        self.yMin = kwargs.setdefault("yMin", 0.0)
        self.yMax = kwargs.setdefault("yMax", 1.5)
        self.p0 = kwargs.setdefault("p0", 0.3)
        self.ignore = kwargs.setdefault("ignore", 20)
        self.maxIter = kwargs.setdefault("maxIter", 40)
        self.colour0 = kwargs.setdefault("colour0", [0xFF, 0x00, 0xF0])
        self.colour1 = kwargs.setdefault("colour1", [0x00, 0xF0, 0xFF])

        self.SUCCESS = 1
        self.OVERFLOW = 2
        self.OUTOFBOUNDS = 3
        self.kRes = 0
        
    def plot(self, **kwargs):
        self.xSize = kwargs.setdefault("xSize", 600)
        self.ySize = kwargs.setdefault("ySize", 400)
        self.kRes = kwargs.setdefault("kRes", 0) 
        self.fname = kwargs.setdefault("images/tempplot.png")
        self.savePlot = kwargs.setdefault("savePlot", False)
        if self.kRes == 0:
            self.kRes = self.xSize
        self.myArray = ones((self.ySize, self.xSize, 3), dtype=uint8)
        self.set_scales()
        self.traverse_k()

        #Create a figure of the right size with one axes that takes up the full 
        #figure
        px = 1/rcParams['figure.dpi']  #pixel in inches
        fig, ax = subplots(figsize=(self.xSize*px, self.ySize*px))
        #Start and end of scales form the extent...
        extent = [self.xMin, self.xMax, self.yMin, self.yMax]
        #Draw the image, wherever you show your plots
        ax.imshow(self.myArray, interpolation='nearest', extent=extent)
        ax.set_aspect('auto')
        #Save the image
        if self.savePlot == True:
            savefig(self.fname)

    def image(self, **kwargs):
        self.xSize = kwargs.setdefault("xSize", 800)
        self.ySize = kwargs.setdefault("ySize", 400)
        self.kRes = kwargs.setdefault("kRes", 0) 
        self.fname = kwargs.setdefault("images/tempfimage.png")
        self.saveImage = kwargs.setdefault("saveImage", False)
        if self.kRes == 0:
            self.kRes = self.xSize
        self.myArray = ones((self.ySize, self.xSize, 3), dtype=uint8)
        
        self.set_scales()
        self.traverse_k()

        #Display the result using PIL
        im = Image.fromarray(self.myArray)
        im.show()
        if self.saveImage == True:
            im.save(self.fname)

    def set_scales(self):
        self.xMin = self.kStart
        self.xMax = self.kEnd
        
        #Make start less than end
        if self.xMax < self.xMin:
            self.xMin, self.xMax = self.xMax, self.xMin
        if self.yMax < self.yMin:
            self.yMin, self.yMax = self.yMax, self.yMin
            
        self.xRange = self.xMax-self.xMin
        self.yRange = self.yMax-self.yMin
        
        self.xIncr = self.xRange/self.xSize
        self.yIncr = self.yRange/self.ySize
        
    def traverse_k(self):
        #Determine increase per step
        kIncr = (self.kEnd - self.kStart)/self.kRes
        k = self.kStart
        for i in range(self.kRes):
            self.iterate(k)
            k += kIncr
        #end_for_x

    def iterate(self, k):
        p = self.p0
        for i in range(self.maxIter):
            p = self.function(p, k)
            if i < self.ignore:
                continue
            #set pixel for this p
            retcode, xPixel, yPixel= self.get_pixel(k, p)
            if retcode == self.SUCCESS:
                self.myArray[self.ySize-1-yPixel, xPixel]\
                             = self.choose_colour(i)
            else:
                print("iteration", i, " k:", k, " p out of bounds:", p)
                break
        #end_for_i

    def get_pixel(self, xVal, yVal):
        try:
            xPixel = int((xVal-self.xMin)/self.xIncr)
            yPixel = int((yVal-self.yMin)/self.yIncr)
        except OverflowError:
            print("Overflow: x:", xVal, " y", yVal)
            return self.OVERFLOW, None, None
        if ((xPixel > -1) and (xPixel < self.xSize))\
            and ((yPixel > -1) and (yPixel < self.ySize)):
                return self.SUCCESS, xPixel, yPixel
        else:
            return self.OUTOFBOUNDS, None, None

    def choose_colour(self, i):
            if i % 2 == 0:
                return self.colour0
            else:
                return self.colour1


    def function(self, p, k):
        return p + k*p*(1-p)
    

class Feig2(Feigenbaum):
    
    def function(self, p, k):
        return k*p*p*(1-p)


class Feig3(Feigenbaum):

    def function(self, p, k):
        return k*sin(p)*(cos(p))
    
    
class FeigPtoFofP(Feigenbaum):
    """ 11 Dec 22
    Plots p to f(p) for standard function.
    """
    def __init__(self, **kwargs):  
        self.xMin = kwargs.setdefault("xMin", 0)
        self.xMax = kwargs.setdefault("xMax", 1.4)
        super().__init__(**kwargs)

    def set_scales(self):
        #Make start less than end
        if self.xMax < self.xMin:
            self.xMin, self.xMax = self.xMax, self.xMin
        if self.yMax < self.yMin:
            self.yMin, self.yMax = self.yMax, self.yMin
            
        self.xRange = self.xMax-self.xMin
        self.yRange = self.yMax-self.yMin
        
        self.xIncr = self.xRange/self.xSize
        self.yIncr = self.yRange/self.ySize
        
    def iterate(self, k):
        p = self.p0
        for i in range(self.maxIter):
            fp = self.function(p, k)
            if i < self.ignore:
                continue
            #set pixel for this p
            retcode, xPixel, yPixel= self.get_pixel(p, fp)
            p = fp
            if retcode == self.SUCCESS:
                if i % 2 == 0:
                    colour = self.colour0
                else:
                    colour = self.colour1
                self.myArray[self.ySize-1-yPixel, xPixel] = colour        
            else:
                print("iteration", i, " k:", k, " p out of bounds:", p)
                break
        #end_for_i

        
if __name__=="__main__":
    tc = 0
    if tc==0:
        f=Feigenbaum()
        f.plot(xSize=300, ySize=200, fname="../images/tempplot2.png")
        print("Now show the plot; look at plot window?")
    if tc==1:
        f=Feigenbaum(ignore=0, maxIter=50)
        f.image()
    if tc==2:
        f=Feig2(ignore=5, maxIter=60, kStart=4.5, kEnd=7.5, pMin=-2)
        f.plot()
    if tc==3:
        f=Feig3(yMax=1.8, kEnd=3.1)
        f.plot()
    if tc==4:
        f=FeigPtoFofP(kStart=0, kEnd=3, maxIter=200, ignore=50)
        f.plot(fpMin=1, fpMax=1.4, kRes=400)
        f.image()