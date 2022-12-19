# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 12:10:05 2022
Rev 1.0
    Constructs the Henon attractor.
Rev 1.1 - 14 Dec 22
    * Generalised function call, requires constants to be given as a list
    * Rationalised logic of iteration
    * Added Orbiter class
Rev 1.2 - 15 Dec 22
    * No longer prints to console when point out of display bounds
Rev 1.3 - 18 Dec 22
    * Adds text to plot, requires subclasses to give a title
@author: Owner
"""

from math import sin, cos, pi
from matplotlib.pyplot import rcParams, savefig, subplots, title, xlabel, ylabel
from numpy import ones, uint8
from PIL import Image

class Henon():
    title = "Hénon Attractor"
    def __init__(self, **kwargs):
        #The function uses constants a and b:
        self.constants = kwargs.setdefault("constants", [1.4, 0.3])
        self.xMin = kwargs.setdefault("xMin", -1.5)
        self.xMax = kwargs.setdefault("xMax", 1.5)
        self.yMin = kwargs.setdefault("yMin", -0.5)
        self.yMax = kwargs.setdefault("yMax", 0.5)
        self.seed = kwargs.setdefault("seed", [0, 0]) #initial (x, y)
        self.ignore = kwargs.setdefault("ignore", 10)
        self.maxIter = kwargs.setdefault("maxIter", 600)
        self.colour0 = kwargs.setdefault("colour0", [0xFF, 0x00, 0xF0])
        self.colour1 = kwargs.setdefault("colour1", [0x00, 0xF0, 0xFF])
        self.SUCCESS = 1
        self.OVERFLOW = 2
        self.OUTOFBOUNDS = 3
        
    def plot(self, **kwargs):
        self.xSize = kwargs.setdefault("xSize", 600)
        self.ySize = kwargs.setdefault("ySize", 400)
        self.fname = kwargs.setdefault("fname", "../images/temphplot.png")
        self.savePlot = kwargs.setdefault("savePlot", False)

        self.myArray = ones((self.ySize, self.xSize, 3), dtype=uint8)
        self.set_scales()
        self.iterate(self.seed[0], self.seed[1])

        #Create a figure of the right size with one axes that takes up the full 
        #figure
        px = 1/rcParams['figure.dpi']  #pixel in inches
        fig, ax = subplots(figsize=(self.xSize*px, self.ySize*px))
        #Start and end of scales form the extent...
        extent = [self.xMin, self.xMax, self.yMin, self.yMax]
        xlabel("x value")
        ylabel("y value")
        title(self.title)
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
        self.ySize = kwargs.setdefault("ySize", 400)
        self.fname = kwargs.setdefault("fname", "../images/temphimage.png")
        self.saveImage = kwargs.setdefault("saveImage", False)

        self.myArray = ones((self.ySize, self.xSize, 3), dtype=uint8)
        self.set_scales()
        self.iterate(self.seed[0], self.seed[1])

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

        self.xIncr = (self.xMax-self.xMin)/self.xSize
        self.yIncr = (self.yMax-self.yMin)/self.ySize        

    def iterate(self, x, y):
        for i in range(self.maxIter):
            if x==None or y==None:
                break
            retcode, xPixel, yPixel = self.get_pixel(x, y)
            if retcode == self.OVERFLOW:
                print("Overflow - pixel")
                break
            elif retcode == self.SUCCESS:
                if i > self.ignore - 1:
                    self.myArray[(self.ySize -1 -yPixel), xPixel] = self.colour0
            else:
                #print("OOB - pixel, (x,y)=", x, y, "Iter:", i)
                pass
            #end_else
            #   the point may have been out of display bounds,
            #   find next one anyway in this case as well
            retcode, x, y = self.function(self.constants, x, y)
            if retcode == self.OVERFLOW:
                print("Overflow -function")
                break
        #end_for_i
    
    def get_pixel(self, xVal, yVal):
        try:
            xPixel = int((xVal-self.xMin)/self.xIncr)
            yPixel = int((yVal-self.yMin)/self.yIncr)
        except OverflowError:
            return self.OVERFLOW, None, None
        if ((xPixel > -1) and (xPixel < self.xSize))\
            and ((yPixel > -1) and (yPixel < self.ySize)):
                return self.SUCCESS, xPixel, yPixel
        else:
            return self.OUTOFBOUNDS, None, None

    def function(self, constants, x, y):
        a = constants[0]
        b = constants[1]
        try:
            xnPlus1 = y - a*x*x + 1
            ynPlus1 = b*x
        except OverflowError:
            return self.OVERFLOW, None, None
        return self.SUCCESS, xnPlus1, ynPlus1


class Orbiter(Henon):
    title = "Orbiter"
    def __init__(self, **kwargs):
        #The function uses a constant phase angle: 0 =< angle =< pi:
        self.constants = kwargs.setdefault("constants", [pi/3])
        self.xMin = kwargs.setdefault("xMin", -2)
        self.xMax = kwargs.setdefault("xMax", 2)
        self.yMin = kwargs.setdefault("yMin", -2)
        self.yMax = kwargs.setdefault("yMax", 2)
        self.kicks = kwargs.setdefault("kicks", 33)
        self.dx = kwargs.setdefault("dx", 0.015)#x-perturbation
        self.dy = kwargs.setdefault("dy", -0.015)#y-perturbation
        super().__init__(**kwargs)

    def iterate(self, x, y) :
        for i in range(self.kicks):
            super().iterate(x, y)
            x += self.dx
            y += self.dy
        
    def function(self, constants, x, y):
        w = constants[0]
        temp = y-x*x
        cosW = cos(w)
        sinW = sin(w)
        return self.SUCCESS, (x*cosW - temp*sinW), (x*sinW + temp*cosW)
"""
"""
if __name__=="__main__":
    tc = 5
    if tc==0:
        f=Henon()
        f.plot()
        print("Now show the plot; look at plot window?")
    if tc==1:
        f=Henon()
        f.image()
    if tc==2:
        f=Henon(ignore=40, maxIter=1000)
        f.image()
    if tc==3:
        f=Henon(xMin=0.1, xMax=0.4, yMin=0.15, yMax=0.3, ignore=40, maxIter=30000)
        f.plot()
        f.image(xSize=900, ySize=600)
    if tc==4:
        f=Henon(xMin=0.3, xMax=0.36, yMin=0.2, yMax=0.23, ignore=40, maxIter=60000)
        f.plot()
        f.image(xSize=900, ySize=600)
    if tc==5:
        f=Orbiter(maxIter=1000)
        f.plot()
        f.image()
