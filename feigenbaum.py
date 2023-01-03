# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 09:56:13 2022
Rev 1.0 - 09 Dec 22
    The program creates a Feigenbaum diagram. It can display (and save) this as 
    a plot. Alternatively, it can simply display the image (and save it) using 
    PIL.
Rev 1.1 - 11 Dec 22
    Better functional decomposition.
    Class FeigPtoFofP to display feigenbaum p to f(p).
Rev 1.2 - 12 Dec 22
    Correction to FeigPtoFofP, minor improvements.
Rev 1.3 - 18 Dec 22
    Adds text to plot. Requires subclasses to define their own title.
Rev 1.4 - 03 Jan 23
    FeigPtoFofP has correct text label in plot. Occasioned a quite large 
    reorganisation ...this needs further development actually: ¿a case for dual 
    inheritance?
@author: Owner
"""

from math import sin, cos
from matplotlib.pyplot import rcParams, savefig, subplots, title, xlabel, ylabel
from numpy import ones, uint8
from PIL import Image

class Feigenbaum():
    title = "Feigenbaum: p := p + k*p*(1-p)"
    
    def __init__(self, **kwargs):
        
        self.kStart = kwargs.setdefault("kStart", 1.6)
        self.kEnd = kwargs.setdefault("kEnd", 3.0)
        self.yMin = kwargs.setdefault("yMin", 0.0)
        self.yMax = kwargs.setdefault("yMax", 1.4)
        self.p0 = kwargs.setdefault("p0", 0.3)
        self.ignore = kwargs.setdefault("ignore", 20)
        self.maxIter = kwargs.setdefault("maxIter", 40)
        self.colour0 = kwargs.setdefault("colour0", [0xFF, 0x00, 0xF0])
        self.colour1 = kwargs.setdefault("colour1", [0x00, 0xF0, 0xFF])

        self.SUCCESS = 1
        self.OVERFLOW = 2
        self.OUTOFBOUNDS = 3
        
    def plot(self, **kwargs):
        #"kRes"(~olution) gives the number of increments to the k-value within 
        #bounds set. For the standard iteration this is the x-axis, thus is 
        #the same as the number of x-pixels.
        self.xSize = kwargs.setdefault("xSize", 600)
        self.ySize = kwargs.setdefault("ySize", 400)
        self.fname = kwargs.setdefault("fname", "../images/tempfplot.png")
        self.savePlot = kwargs.setdefault("savePlot", False)
        self.xLabel = kwargs.setdefault("xLabel", "feedback k value")
        self.yLabel = kwargs.setdefault("yLabel", "p value")

        self.myArray = ones((self.ySize, self.xSize, 3), dtype=uint8)

        self.kRes = self.xSize
        self.xMin = self.kStart
        self.xMax = self.kEnd
        self.set_scales()
        self.traverse_k()

        #Create a figure of the right size with one axes that takes up the full 
        #figure
        px = 1/rcParams['figure.dpi']  #pixel in inches
        fig, ax = subplots(figsize=(self.xSize*px, self.ySize*px))
        #Start and end of scales form the extent...
        extent = [self.xMin, self.xMax, self.yMin, self.yMax]
        title(self.title)
        xlabel(self.xLabel)
        ylabel(self.yLabel)
        #Draw the image, wherever you show your plots
        ax.imshow(self.myArray, interpolation='nearest', extent=extent)
        ax.set_aspect('auto')
        #Save the image
        if self.savePlot == True:
            try:
                savefig(self.fname, format="PNG")
            except:
                print("Couldn't save file", self.fname)

    def image(self, **kwargs):
        self.xSize = kwargs.setdefault("xSize", 800)
        self.ySize = kwargs.setdefault("ySize", 400)
        self.fname = kwargs.setdefault("fname", "../images/tempfimage.png")
        self.saveImage = kwargs.setdefault("saveImage", False)

        self.myArray = ones((self.ySize, self.xSize, 3), dtype=uint8)
        
        self.kRes = self.xSize
        self.xMin = self.kStart
        self.xMax = self.kEnd
        self.set_scales()
        self.traverse_k()

        #Display the result using PIL
        im = Image.fromarray(self.myArray)
        im.show()
        if self.saveImage == True:
            try:
                im.save(self.fname, format="PNG")
            except:
                print("Couldn't save file", self.fname)

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
        
    def traverse_k(self):
        #Determine increase per step
        kIncr = (self.kEnd - self.kStart)/self.kRes
        k = self.kStart
        for i in range(self.kRes):
            self.iterate(k)
            k += kIncr
        #end_for_i

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
            elif retcode == self.OVERFLOW:
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
    title = "Feigenbaum: p := k*p*p*(1-p)"
    
    def function(self, p, k):
        return k*p*p*(1-p)


class Feig3(Feigenbaum):
    title = "Feigenbaum: p := k*sin(p)*cos(p)"

    def function(self, p, k):
        return k*sin(p)*(cos(p))
    
    
class FeigPtoFofP(Feigenbaum):
    """ 11 Dec 22
    Plots p to f(p) for standard function.
    """
    title = "p to f(p)"
    def __init__(self, **kwargs):  
        self.xMin = kwargs.setdefault("xMin", 0)
        self.xMax = kwargs.setdefault("xMax", 1.4)
        super().__init__(**kwargs)

    def plot(self, **kwargs):
        #"kRes"(~olution) gives the number of increments to the k-value within 
        #bounds set.
        self.xSize = kwargs.setdefault("xSize", 600)
        self.ySize = kwargs.setdefault("ySize", 600)
        self.kRes = kwargs.setdefault("kRes", 400)
        self.fname = kwargs.setdefault("fname", "../images/tempfplot.png")
        self.savePlot = kwargs.setdefault("savePlot", False)
        self.xLabel = kwargs.setdefault("xLabel", "p value")
        self.yLabel = kwargs.setdefault("yLabel", "f(p)")

        self.myArray = ones((self.ySize, self.xSize, 3), dtype=uint8)

        self.set_scales()
        self.traverse_k()

        #Create a figure of the right size with one axes that takes up the full 
        #figure
        px = 1/rcParams['figure.dpi']  #pixel in inches
        fig, ax = subplots(figsize=(self.xSize*px, self.ySize*px))
        #Start and end of scales form the extent...
        extent = [self.xMin, self.xMax, self.yMin, self.yMax]
        title(self.title)
        xlabel(self.xLabel)
        ylabel(self.yLabel)
        #Draw the image, wherever you show your plots
        ax.imshow(self.myArray, interpolation='nearest', extent=extent)
        ax.set_aspect('auto')
        #Save the image
        if self.savePlot == True:
            try:
                savefig(self.fname, format="PNG")
            except:
                print("Couldn't save file", self.fname)

    def image(self, **kwargs):
        self.xSize = kwargs.setdefault("xSize", 600)
        self.ySize = kwargs.setdefault("ySize", 600)
        self.kRes = kwargs.setdefault("kRes", 400)
        self.fname = kwargs.setdefault("fname", "../images/tempfimage.png")
        self.saveImage = kwargs.setdefault("saveImage", False)

        self.myArray = ones((self.ySize, self.xSize, 3), dtype=uint8)
        
        self.set_scales()
        self.traverse_k()

        #Display the result using PIL
        im = Image.fromarray(self.myArray)
        im.show()
        if self.saveImage == True:
            try:
                im.save(self.fname, format="PNG")
            except:
                print("Couldn't save file", self.fname)

    def iterate(self, k):
        p = self.p0
        for i in range(self.maxIter):
            fp = self.function(p, k)
            if i < self.ignore:
                p = fp
                continue
            #set pixel for this p
            retcode, xPixel, yPixel= self.get_pixel(p, fp)
            if retcode == self.SUCCESS:
                self.myArray[self.ySize-1-yPixel, xPixel]\
                             = self.choose_colour(i)
            elif retcode == self.OVERFLOW:
                break
            #(else p is out of display bounds)
            p = fp
        #end_for_i

        
if __name__=="__main__":
    tc = 5
    if tc==0:
        f=Feigenbaum(kStart=1.8, maxIter=512)
        f.plot(savePlot=True, xSize=1000, ySize=700)
        print("Now show the plot; look at plot window?")
    if tc==1:
        f=Feigenbaum(xSize=300, ySize=200, maxIter=50)
        f.image(saveImage=True)
    if tc==2:
        f=Feig2(ignore=5, maxIter=60, kStart=4.5, kEnd=7.06, yMin=-2, yMax=3)
        f.plot()
        f.image()
    if tc==3:
        f=Feig3(yMax=1.8, kEnd=3.1)
        f.plot()
    if tc==4:
        f=FeigPtoFofP(kStart=1.8, kEnd=3, yMin=1, yMax=1.4)
        f.plot(kRes=100)
        f.image()
    if tc==5:
        f=FeigPtoFofP(kStart=0, kEnd=3, ignore=50, maxIter=100)
        f.plot(kRes=200)
        f.image()